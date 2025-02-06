from pydantic import BaseModel


class BrowserSetupRequest(BaseModel):
    url: str = "https://www.google.com"


class QueryRequest(BaseModel):
    query: str


