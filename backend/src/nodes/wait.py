import asyncio
from src.graph_state import AgentState


async def wait_node(state: AgentState):
    await asyncio.sleep(3)
    return {"last_action": "Wait : waited for 3 seconds", "actions_taken": ["Wait : waited for 3 seconds"]}