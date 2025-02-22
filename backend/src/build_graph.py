from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END

from src.graph_state import AgentState
from src.nodes.master_plan_node import master_plan_node
from src.nodes.annotate_page import annotate_page
from src.nodes.llm_call_node import llm_call_node
from src.nodes.parse_action_node import parse_action_node
from src.nodes.click import click_node
from src.nodes.type import type_node
from src.nodes.scroll import scroll_node
from src.nodes.wait import wait_node
from src.nodes.go_back import go_back_node
from src.nodes.go_to_search_engine import go_to_search_engine_node
from src.nodes.answer_node import answer_node


load_dotenv()

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

def build_graph():
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
    return workflow

graph = build_graph().compile()
