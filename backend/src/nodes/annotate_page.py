from src.graph_state import AgentState
from src.utilities import mark_page


async def annotate_page(state: AgentState):
    page = state["page"]
    result = await mark_page(page)
    return {"image": result["image"], "bboxes": result["bboxes"]}
