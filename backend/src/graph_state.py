from typing_extensions import TypedDict, List, Annotated
from operator import add
from playwright.async_api import Page
from pydantic import BaseModel, Field


class Bbox(TypedDict):
    x: int
    y: int
    text: str
    type: str
    ariaLabel: str


class Action(TypedDict):
    action: str
    args: str | Bbox


class MasterPlanState(BaseModel):
    plan: List[str] = Field(description="To setup the master plan state for model.")


class AgentState(TypedDict):
    input_str: str
    page: Page
    image: str
    master_plan: MasterPlanState
    bboxes: List[Bbox]
    actions_taken: Annotated[List[str], add]
    action: Action | str
    last_action: str
    notes: Annotated[List[str], add]
    answer: str
