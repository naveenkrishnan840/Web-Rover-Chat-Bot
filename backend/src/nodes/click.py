import asyncio

from src.graph_state import AgentState


async def click_node(state: AgentState):
    page = state["page"]
    action = state["action"]
    bbox_id = int(action["action"].split(" ")[1].split("[")[1].split("]")[0])
    if bbox_id not in [bbox["id"] for bbox in state["bboxes"]]:
        return {"action": "retry", "args": f"Could not find bbox with id {bbox_id}"}
    bbox = state["bboxes"][bbox_id]
    await asyncio.sleep(2)
    await page.mouse.click(bbox["x"], bbox["y"])
    await asyncio.sleep(4)
    return {"last_action": f"Click : clicked on {bbox_id}", "actions_taken": [f"Click : clicked on {bbox_id}"]}
