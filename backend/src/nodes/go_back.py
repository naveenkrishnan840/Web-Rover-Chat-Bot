from backend.src.graph_state import AgentState


async def go_back_node(state: AgentState):
    page = state["page"]
    await page.go_back()
    return {"last_action": f"Go Back : Navigated back to page {page.url}",
            "actions_taken": [f"Go Back : Navigated back to page {page.url}"]}