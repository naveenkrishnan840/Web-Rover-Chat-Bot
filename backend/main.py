from fastapi import FastAPI, HTTPException, APIRouter
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import json
from typing_extensions import Dict, Any
import asyncio
import time
from src.request_validate import QueryRequest, BrowserSetupRequest
from src.utilities import setup_browser_2
from src.build_graph import build_graph


app = FastAPI(title="Web Rover Chat Bot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
router = APIRouter()

# Global variable to store browser session
browser_session: Dict[str, Any] = {
    "playwright": None,
    "browser": None,
    "page": None
}

# Global queue for browser events
browser_events = asyncio.Queue()

langgraph_app = build_graph()


@router.post("/setup-browser")
async def setup_browser(request: BrowserSetupRequest):
    try:
        # Clear any existing session
        if browser_session["playwright"]:
            await cleanup_browser()

        # Setup new browser session
        playwright, browser, page = await setup_browser_2(request.url)

        # Store session info
        browser_session.update({
            "playwright": playwright,
            "browser": browser,
            "page": page
        })

        return {"status": "success", "message": "Browser setup complete"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to setup browser: {str(e)}")


@router.post("/cleanup")
async def cleanup_browser():
    try:
        if browser_session["page"]:
            await browser_session["page"].close()
        if browser_session["browser"]:
            await browser_session["browser"].close()
        if browser_session["playwright"]:
            await browser_session["playwright"].stop()

        # Reset session
        browser_session.update({
            "playwright": None,
            "browser": None,
            "page": None
        })

        return {"status": "success", "message": "Browser cleanup complete"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cleanup browser: {str(e)}")


async def emit_browser_event(event_type: str, data: Dict[str, Any]):
    await browser_events.put({
        "type": event_type,
        "data": data
    })


@router.get("/browser-events")
async def browser_events_endpoint():
    async def event_generator():
        while True:
            try:
                event = await browser_events.get()
                yield f"data: {json.dumps(event)}\n\n"
            except asyncio.CancelledError:
                break

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


async def stream_agent_response(query: str, page):
    try:
        initial_state = {
            "input_str": query,
            "page": page,
            "image": "",
            "master_plan": None,
            "bboxes": [],
            "actions_taken": [],
            "action": None,
            "last_action": "",
            "notes": [],
            "answer": ""
        }

        # Keep track of last event for potential retries
        last_event = None
        retry_count = 0
        max_retries = 3

        async for event in langgraph_app.astream(
                initial_state,
                {"recursion_limit": 400}
        ):
            try:
                # Send periodic keepalive to prevent timeout
                yield f"data: {{\n  \"type\": \"keepalive\",\n  \"timestamp\": {time.time()}\n}}\n\n"

                if isinstance(event, dict):
                    last_event = event

                    if "parse_action_node" in event:
                        action = event["parse_action_node"]["action"]
                        thought = event["parse_action_node"]["notes"][-1]

                        # Ensure proper encoding and escaping of JSON
                        thought_json = json.dumps(thought, ensure_ascii=False)
                        yield f"data: {{\n  \"type\": \"thought\",\n  \"content\": {thought_json}\n}}\n\n"

                        if isinstance(action, dict):
                            action_json = json.dumps(action, ensure_ascii=False)
                            yield f"data: {{\n  \"type\": \"action\",\n  \"content\": {action_json}\n}}\n\n"

                            # Handle browser events
                            action_type = action.get("action", "")
                            if action_type == "goto":
                                await emit_browser_event("navigation", {
                                    "url": action["args"],
                                    "status": "loading"
                                })

                    if "answer_node" in event:
                        answer = event["answer_node"]["answer"]
                        answer_json = json.dumps(answer, ensure_ascii=False)
                        yield f"data: {{\n  \"type\": \"final_answer\",\n  \"content\": {answer_json}\n}}\n\n"

                    # Reset retry count on successful event
                    retry_count = 0
            except Exception as e:
                print(f"Error processing event: {str(e)}")
                retry_count += 1
                if retry_count <= max_retries and last_event:
                    # Retry last event
                    yield f"data: {{\n  \"type\": \"retry\",\n  \"content\": \"Retrying last action...\"\n}}\n\n"
                    continue
                else:
                    raise e

    except Exception as e:
        error_json = json.dumps(str(e), ensure_ascii=False)
        yield f"data: {{\n  \"type\": \"error\",\n  \"content\": {error_json}\n}}\n\n"
        raise e
    finally:
        # Ensure proper stream closure
        yield f"data: {{\n  \"type\": \"end\",\n  \"content\": \"Stream completed\"\n}}\n\n"


@router.post("/query")
async def query_agent(request: QueryRequest):
    if not browser_session["page"]:
        raise HTTPException(status_code=400, detail="Browser not initialized. Call /setup-browser first")

    return StreamingResponse(stream_agent_response(request.query, browser_session["page"]),
                             media_type="text/event-stream")

app.include_router(router=router)

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="127.0.0.1", port=8001)
