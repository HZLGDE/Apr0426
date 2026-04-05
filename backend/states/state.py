from typing import TypedDict,Annotated,List
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages

class QuoteState(TypedDict):
    messages: Annotated[List[AnyMessage],add_messages]