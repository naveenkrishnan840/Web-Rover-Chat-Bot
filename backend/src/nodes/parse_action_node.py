from backend.src.graph_state import AgentState, Action


async def parse_action_node(state: AgentState):
    action_prefix = "Action: "
    text = state["action"]
    if not text.strip().split("Action:")[-1]:
        return {"action": "retry", "args": f"Could not parse LLM Output: {text}"}
    action_block = text.strip().split("Action: ")[-1]
    thought_block = text.strip().split("Action: ")[0].split("Thought: ")[-1]
    split_output = action_block.split("; ", 1)
    if len(split_output) == 1:
        action, args = split_output[0], None
    else:
        action, args = split_output

    return {"action": Action(action=action, args=args), "notes": [thought_block]}
