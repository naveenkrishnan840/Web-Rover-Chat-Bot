from src.graph_state import AgentState


async def go_to_search_engine_node(state: AgentState):
    page = state["page"]
    await page.goto("https://www.google.com")
    return {"last_action": "Go to Search Engine : Navigated to Google",
            "actions_taken": ["Go to Search Engine : Navigated to Google"]}