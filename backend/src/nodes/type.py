import asyncio
import platform
from src.graph_state import AgentState


async def type_node(state: AgentState):
    page = state["page"]
    action = state["action"]
    bbox_id = int(action["action"].split("[")[1].split("]")[0])
    if bbox_id not in [bbox["id"] for bbox in state["bboxes"]]:
        return {"action": "retry", "args": f"Could not find bbox with id {bbox_id}"}
    bbox = state["bboxes"][bbox_id]
    await page.mouse.click(bbox["x"], bbox["y"])
    select_all = "Meta+A" if platform.system() == "Darwin" else "Control+A"
    await page.keyboard.press(select_all)
    await asyncio.sleep(2)
    select_all = "Meta+A" if platform.system() == "Darwin" else "Control+A"
    await page.keyboard.press(select_all)
    await asyncio.sleep(1)
    await page.keyboard.press("Backspace")
    await asyncio.sleep(1)
    await page.keyboard.type(action["args"])
    await asyncio.sleep(3)
    await page.keyboard.press("Enter")
    await asyncio.sleep(3)
    return {"last_action": f"Type : typed {action['args']} into {bbox_id}",
            "actions_taken": [f"Type : typed {action['args']} into {bbox_id}"]}
