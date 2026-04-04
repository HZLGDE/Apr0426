# Implementation Guide: AI Quote Aggregator

## Prerequisites

### 1. Python Environment Setup

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install langgraph langchain langchain-openai httpx pydantic fastapi uvicorn python-dotenv pytest
```

### 2. Environment Variables

Create a `.env` file in your project directory:

```bash
# Required for LLM (get free key at https://platform.openai.com/)
OPENAI_API_KEY=your_openai_key_here

# Optional (ZenQuotes doesn't need a key)
# QUOTE_API_KEY=optional
```

## Step-by-Step Implementation

### Step 1: Define Your State Schema

Create a `TypedDict` to define the graph state:

```python
from typing import TypedDict, Optional, List, Dict, Any

class QuoteGraphState(TypedDict):
    """State schema for the quote aggregator graph"""
    input: str                           # User's original input
    intent: Optional[str]                # LLM-detected intent (quote_request, greeting, etc.)
    quote: Optional[Dict[str, str]]      # Quote data from API (quote, author)
    formatted_output: Optional[str]      # Final formatted response
    error: Optional[str]                 # Error message if something fails
    metadata: Dict[str, Any]             # Execution metadata
```

**Checkpoint:** Verify state has all fields needed for your graph flow.

### Step 2: Create the Quote API Tool

Use LangChain's `@tool` decorator to wrap the API call:

```python
from langchain_core.tools import tool
from pydantic import BaseModel, Field
import httpx

class QuoteInput(BaseModel):
    """Input schema for quote tool"""
    category: str = Field(default="inspirational")

@tool(args_schema=QuoteInput)
def fetch_quote(category: str = "inspirational") -> dict:
    """
    Fetch a random inspirational quote from ZenQuotes API.
    
    Args:
        category: Type of quote (inspirational, motivational)
    
    Returns:
        Dict with quote and author keys
    """
    # TODO: Implement the API call using httpx
    # API endpoint: https://zenquotes.io/api/random
    # Returns array with objects like: {"q": "quote text", "a": "author"}
    pass
```

**Checkpoint:** Test the tool standalone before integrating into graph.

### Step 3: Create the LLM Processing Node

Create a node that uses an LLM to analyze user input:

```python
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

llm = ChatOpenAI(model="gpt-4o-mini")

def process_intent(state: QuoteGraphState) -> QuoteGraphState:
    """
    Analyze user input to determine intent.
    
    If user wants a quote, route to fetch_quote.
    Otherwise, provide a friendly response.
    """
    user_input = state["input"]
    
    # TODO: Use LLM to classify intent
    # Prompt suggestions:
    # - "Classify this message as 'quote_request', 'greeting', or 'other'"
    # - Return JSON with intent and confidence
    
    # Return updated state with detected intent
    pass
```

**Checkpoint:** Test LLM node with various inputs.

### Step 4: Add Conditional Routing

Create a routing function to decide next node:

```python
def route_by_intent(state: QuoteGraphState) -> str:
    """
    Route to next node based on detected intent.
    
    Returns:
        "fetch_quote" - if user wants a quote
        "greeting_handler" - if user is greeting
        "fallback" - for other requests
    """
    intent = state.get("intent", "other")
    
    # TODO: Implement routing logic
    # if intent == "quote_request": return "fetch_quote"
    # elif intent == "greeting": return "greeting_handler"
    # else: return "fallback"
    pass
```

### Step 5: Create Format and Fallback Nodes

```python
def format_response(state: QuoteGraphState) -> QuoteGraphState:
    """Format the quote for output"""
    quote = state.get("quote", {})
    
    # TODO: Format the response
    # Combine quote and author into a nice message
    # Add metadata about source
    
    pass

def fallback_handler(state: QuoteGraphState) -> QuoteGraphState:
    """Handle non-quote requests gracefully"""
    # TODO: Provide helpful response
    pass
```

### Step 6: Build and Compile the Graph

```python
from langgraph.graph import StateGraph, END

def create_quote_graph():
    """Create and compile the quote aggregator graph"""
    
    # Initialize StateGraph
    graph = StateGraph(QuoteGraphState)
    
    # TODO: Add all nodes
    # graph.add_node("process", process_intent)
    # graph.add_node("fetch_quote", fetch_quote_node)
    # graph.add_node("format_response", format_response)
    # graph.add_node("fallback", fallback_handler)
    
    # TODO: Add edges
    # graph.set_entry_point("process")
    # graph.add_conditional_edges("process", route_by_intent, {...})
    # graph.add_edge("fetch_quote", "format_response")
    # graph.add_edge("format_response", END)
    # graph.add_edge("fallback", END)
    
    # Return compiled graph
    return graph.compile()
```

### Step 7: Create FastAPI Endpoint

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

app = FastAPI(title="Quote Aggregator API")

class GraphRequest(BaseModel):
    message: str = Field(..., description="User input message")

class GraphResponse(BaseModel):
    success: bool
    result: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# Initialize your compiled graph
# TODO: Import and instantiate your graph
# compiled_graph = create_quote_graph()

@app.post("/graph", response_model=GraphResponse)
async def execute_graph(request: GraphRequest) -> GraphResponse:
    """
    Execute the quote aggregator graph.
    """
    try:
        # TODO: Invoke your compiled graph
        # result = compiled_graph.invoke({"input": request.message})
        
        return GraphResponse(
            success=True,
            result={},  # TODO: Add your result
            metadata={}  # TODO: Add metadata
        )
    except Exception as e:
        return GraphResponse(
            success=False,
            result={},
            error=str(e)
        )

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

## Running the Application

```bash
# Start the server
uvicorn your_module:app --reload --port 8000

# Test with curl
curl -X POST http://localhost:8000/graph \
  -H "Content-Type: application/json" \
  -d '{"message": "Give me an inspirational quote"}'

# View interactive docs
open http://localhost:8000/docs
```

## Testing Strategy

1. **Test each node in isolation** - Verify function signatures work
2. **Test the graph flow** - Use `graph.invoke()` directly
3. **Test the API endpoint** - Use curl or FastAPI TestClient
4. **Run pytest tests** - Execute the test suite

## Common Issues and Debugging

- **API key not set**: Ensure `.env` is loaded with `load_dotenv()`
- **LLM timeout**: Add timeout to ChatOpenAI initialization
- **State key errors**: Verify all state fields are initialized
- **Import errors**: Use correct package names (langchain_openai)

## File Structure

```
your_project/
├── .env                 # API keys
├── main.py              # FastAPI app and graph definition
├── requirements.txt     # Dependencies
├── tests.py             # Test suite
└── venv/                # Virtual environment
```
