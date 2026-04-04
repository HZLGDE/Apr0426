# LangGraph Core Concepts

## StateGraph Overview

StateGraph is LangGraph's core abstraction for building stateful, multi-step workflows. Unlike simple function chains, StateGraph allows:

- **Cyclic workflows** (loops, feedback)
- **Conditional routing** based on state
- **Parallel execution** of nodes
- **State persistence** with checkpoints

### Basic StateGraph Pattern

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict

class GraphState(TypedDict):
    """Define your state schema"""
    input: str
    output: str

def node_a(state: GraphState) -> GraphState:
    return {"output": f"Processed: {state['input']}"}

# Build the graph
graph = StateGraph(GraphState)
graph.add_node("process", node_a)
graph.add_edge("__start__", "process")
graph.add_edge("process", END)

compiled = graph.compile()
```

## State Management

### TypedDict Pattern

Use TypedDict for type-safe state:

```python
from typing import TypedDict, Optional, List

class AgentState(TypedDict):
    input: str
    intent: Optional[str]
    quotes: List[dict]
    formatted_output: Optional[str]
    error: Optional[str]
    metadata: dict
```

### State Updates

Nodes return partial state that gets merged:

```python
def process_node(state: AgentState) -> AgentState:
    # Return only fields to update
    return {
        "intent": "quote_request",
        "metadata": {"source": "llm_decision"}
    }
```

## LLM Integration in LangGraph

### Using LangChain's LCEL with LangGraph

```python
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

llm = ChatOpenAI(model="gpt-4o-mini")

def llm_node(state: GraphState) -> GraphState:
    response = llm.invoke([
        HumanMessage(content=f"Analyze: {state['input']}")
    ])
    return {"llm_response": response.content}
```

### Tool Calling with LLM

```python
from langchain_core.tools import tool

@tool
def get_quote() -> dict:
    """Fetch a random inspirational quote"""
    import httpx
    resp = httpx.get("https://zenquotes.io/api/random")
    return resp.json()[0]

# Bind tools to LLM
llm_with_tools = llm.bind_tools([get_quote])

def process_with_tools(state: GraphState) -> GraphState:
    response = llm_with_tools.invoke(state["input"])
    # Handle tool calls
    if response.tool_calls:
        for tool_call in response.tool_calls:
            result = get_quote.invoke(tool_call)
            return {"quotes": [result]}
    return {"response": response.content}
```

## Conditional Routing

### Simple Conditional Edge

```python
def should_fetch_quote(state: GraphState) -> str:
    """Route based on intent"""
    if state.get("intent") == "quote_request":
        return "fetch_quote"
    return "fallback"

# Add conditional edge
graph.add_conditional_edges(
    "process",
    should_fetch_quote,
    {
        "fetch_quote": "fetch_quote",
        "fallback": "fallback"
    }
)
```

### Multiple Routing Options

```python
def route_by_intent(state: AgentState) -> str:
    intent = state.get("intent", "")
    
    if intent == "quote_request":
        return "fetch_quote"
    elif intent == "joke_request":
        return "fetch_joke"
    elif intent == "fact_request":
        return "fetch_fact"
    else:
        return "fallback"
```

## Tool Integration Patterns

### Basic Tool with @tool Decorator

```python
from langchain_core.tools import tool
from pydantic import BaseModel, Field

class QuoteInput(BaseModel):
    category: str = Field(default="inspirational")

@tool(args_schema=QuoteInput)
def get_quote(category: str = "inspirational") -> dict:
    """Fetch a quote from the API"""
    import httpx
    resp = httpx.get("https://zenquotes.io/api/random")
    data = resp.json()[0]
    return {
        "quote": data["q"],
        "author": data["a"]
    }
```

### Tool with Error Handling

```python
@tool
def safe_get_quote() -> dict:
    """Fetch quote with error handling"""
    try:
        import httpx
        resp = httpx.get("https://zenquotes.io/api/random", timeout=5.0)
        resp.raise_for_status()
        return resp.json()[0]
    except Exception as e:
        return {"error": str(e), "fallback_quote": "Keep moving forward!"}
```

## Error Handling Patterns

### Try/Except in Nodes

```python
def robust_node(state: GraphState) -> GraphState:
    try:
        result = risky_operation()
        return {"result": result}
    except Exception as e:
        return {"error": str(e), "fallback_result": "default_value"}
```

### Fallback Node Pattern

```python
def fallback_node(state: GraphState) -> GraphState:
    error = state.get("error", "Unknown error")
    return {
        "formatted_output": f"Sorry, something went wrong: {error}",
        "metadata": {"handled": True}
    }
```

## FastAPI Integration

### Basic Endpoint Pattern

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

app = FastAPI()

class GraphRequest(BaseModel):
    message: str = Field(..., description="User input message")

class GraphResponse(BaseModel):
    success: bool
    result: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

@app.post("/graph", response_model=GraphResponse)
async def execute_graph(request: GraphRequest) -> GraphResponse:
    try:
        result = compiled_graph.invoke({"input": request.message})
        return GraphResponse(success=True, result=result)
    except Exception as e:
        return GraphResponse(success=False, result={}, error=str(e))
```

## Best Practices

1. **Always define typed state** - Use TypedDict for clarity
2. **Handle errors in every node** - Don't let exceptions propagate
3. **Use conditional routing** - Keep logic declarative
4. **Return partial state** - Only return fields you're updating
5. **Add metadata** - Track execution path for debugging
6. **Test incrementally** - Test each node before connecting

## Common Pitfalls

- Forgetting to call `.compile()` on the graph
- Not handling None values in state
- Blocking LLM calls in async endpoints
- Missing error handling in API tools
- Not validating input in FastAPI endpoint
