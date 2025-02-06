from fastapi import FastAPI, HTTPException, APIRouter
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import json
from typing_extensions import Dict, Any
import asyncio
import time
from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv
from backend.src.request_validate import QueryRequest, BrowserSetupRequest
from backend.src.utilities import setup_browser_2
from backend.src.graph_state import AgentState
from backend.src.master_plan_node import master_plan_node
from backend.src.annotate_page import annotate_page
from backend.src.llm_call_node import llm_call_node
from backend.src.parse_action_node import parse_action_node
from backend.src.click import click_node
from backend.src.type import type_node
from backend.src.scroll import scroll_node
from backend.src.wait import wait_node
from backend.src.go_back import go_back_node
from backend.src.go_to_search_engine import go_to_search_engine_node
from backend.src.answer_node import answer_node


load_dotenv()
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


tools = {
    "Click": "click_node",
    "Type": "type_node",
    "Scroll": "scroll_node",
    "Wait": "wait_node",
    "GoBack": "go_back_node",
    "Google": "go_to_search_engine_node"
}


def tool_router(state: AgentState):
    action = state["action"]["action"]
    action_type = action.split(" ")[0]
    if action_type == "retry":
        return "annotate_page_node"
    if action_type == "Respond":
        return "answer_node"
    return tools[action_type]


workflow = StateGraph(state_schema=AgentState)
workflow.add_node("master_plan_node", master_plan_node)
workflow.add_node("annotate_page_node", annotate_page)
workflow.add_node("llm_call_node", llm_call_node)
workflow.add_node("parse_action_node", parse_action_node)
workflow.add_node("type_node", type_node)
workflow.add_node("scroll_node", scroll_node)
workflow.add_node("click_node", click_node)
workflow.add_node("wait_node", wait_node)
workflow.add_node("go_to_search_engine_node", go_to_search_engine_node)
workflow.add_node("go_back_node", go_back_node)
workflow.add_node("answer_node", answer_node)

workflow.add_edge(start_key=START, end_key="master_plan_node")
workflow.add_edge(start_key="master_plan_node", end_key="annotate_page_node")
workflow.add_edge(start_key="annotate_page_node", end_key="llm_call_node")
workflow.add_edge(start_key="llm_call_node", end_key="parse_action_node")
workflow.add_conditional_edges(source="parse_action_node", path=tool_router,
                               path_map=["annotate_page_node",  "click_node", "type_node", "scroll_node", "wait_node",
                                         "go_back_node", "go_to_search_engine_node", "answer_node"])
workflow.add_edge(start_key="type_node", end_key="annotate_page_node")
workflow.add_edge(start_key="scroll_node", end_key="annotate_page_node")
workflow.add_edge(start_key="click_node", end_key="annotate_page_node")
workflow.add_edge(start_key="wait_node", end_key="annotate_page_node")
workflow.add_edge(start_key="go_to_search_engine_node", end_key="annotate_page_node")
workflow.add_edge(start_key="go_back_node", end_key="annotate_page_node")
workflow.add_edge(start_key="parse_action_node", end_key="answer_node")
workflow.add_edge(start_key="answer_node", end_key=END)

langgraph_app = workflow.compile()


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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
