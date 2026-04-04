# API Documentation: ZenQuotes API

## Overview

**ZenQuotes API** provides access to a collection of inspirational quotes. Used in this exercise to demonstrate external API integration with LangGraph tools.

- **Base URL**: `https://zenquotes.io/api`
- **Authentication**: None required (free tier)
- **Rate Limit**: Reasonable usage (not heavily documented, but works for testing)
- **HTTPS**: Supported

## Verification Status

> ⚠️ Note: Network restrictions prevented live API verification. The API documentation below is based on known working patterns. Test before building your graph.

## Endpoints

### Get Random Quote

**Endpoint:** `GET /api/random`

Returns a random inspirational quote.

#### Request

```bash
curl -X GET "https://zenquotes.io/api/random"
```

#### Response

```json
[
  {
    "q": "The only way to do great work is to love what you do.",
    "a": "Steve Jobs",
    "h": "<blockquote>The only way to do great work is to love what you do.</blockquote><br>&mdash; <footer>Steve Jobs</footer>"
  }
]
```

#### Python Example

```python
import httpx

def get_random_quote():
    """Fetch a random quote from ZenQuotes"""
    client = httpx.Client(timeout=10.0)
    response = client.get("https://zenquotes.io/api/random")
    response.raise_for_status()
    
    data = response.json()
    if data:
        return {
            "quote": data[0]["q"],
            "author": data[0]["a"]
        }
    return {"error": "No quote returned"}
```

### Get Today's Quote

**Endpoint:** `GET /api/today`

Returns the quote of the day.

```bash
curl -X GET "https://zenquotes.io/api/today"
```

### Get Multiple Random Quotes

**Endpoint:** `GET /api/quotes`

Parameters:
- `count` (optional): Number of quotes to return (default: 1)

```bash
curl -X GET "https://zenquotes.io/api/quotes?count=3"
```

## Response Schema

| Field | Type | Description |
|-------|------|-------------|
| `q` | string | The quote text |
| `a` | string | Author name |
| `h` | string | HTML formatted quote |

## LangChain Tool Integration

### Basic Quote Tool

```python
from langchain_core.tools import tool
from pydantic import BaseModel, Field
import httpx

class QuoteInput(BaseModel):
    """Input schema for quote tool"""
    count: int = Field(default=1, description="Number of quotes to fetch")

@tool(args_schema=QuoteInput)
def fetch_quote(count: int = 1) -> dict:
    """
    Fetch inspirational quotes from ZenQuotes API.
    
    Args:
        count: Number of quotes to retrieve (1-50)
    
    Returns:
        List of dicts with quote and author keys
    """
    try:
        client = httpx.Client(timeout=10.0)
        url = f"https://zenquotes.io/api/quotes?count={min(count, 50)}"
        
        response = client.get(url)
        response.raise_for_status()
        
        data = response.json()
        quotes = [{"quote": item["q"], "author": item["a"]} for item in data]
        
        return {
            "quotes": quotes,
            "count": len(quotes)
        }
    except httpx.HTTPError as e:
        return {"error": f"API request failed: {str(e)}"}
    except (KeyError, IndexError) as e:
        return {"error": f"Failed to parse response: {str(e)}"}
```

### Error-Handling Quote Tool

```python
from langchain_core.tools import tool
from tenacity import retry, stop_after_attempt, wait_exponential

@tool
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def fetch_quote_with_retry() -> dict:
    """
    Fetch a quote with automatic retry on failure.
    """
    try:
        import httpx
        client = httpx.Client(timeout=10.0)
        
        response = client.get("https://zenquotes.io/api/random")
        response.raise_for_status()
        
        data = response.json()
        return data[0] if data else {"error": "Empty response"}
        
    except Exception as e:
        # Return fallback quote on failure
        return {
            "q": "Fall seven times, stand up eight.",
            "a": "Japanese Proverb"
        }
```

## Error Codes

| Status Code | Meaning | How to Handle |
|-------------|---------|---------------|
| 200 | Success | Parse JSON response |
| 429 | Rate Limited | Implement backoff, retry later |
| 500 | Server Error | Retry with exponential backoff |
| 503 | Service Unavailable | Use fallback quotes |

## Rate Limiting Strategy

```python
import time
from functools import lru_cache

class RateLimiter:
    """Simple rate limiter for API calls"""
    def __init__(self, calls_per_second: float = 1.0):
        self.min_interval = 1.0 / calls_per_second
        self.last_call = 0
    
    def wait(self):
        elapsed = time.time() - self.last_call
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self.last_call = time.time()

# Create rate limiter
quote_rate_limiter = RateLimiter(calls_per_second=1.0)

def throttled_fetch():
    """Fetch quote with rate limiting"""
    quote_rate_limiter.wait()
    # ... API call
```

## Testing the API

Before building your graph, verify the API works:

```python
import httpx

def test_zenquotes():
    """Test script to verify ZenQuotes API"""
    client = httpx.Client(timeout=10.0)
    
    try:
        # Test random quote
        response = client.get("https://zenquotes.io/api/random")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Quote: {data[0]['q']}")
            print(f"Author: {data[0]['a']}")
            print("✅ API working!")
        else:
            print(f"❌ API error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    test_zenquotes()
```

## Fallback Quotes

In case the API is unavailable, have backup quotes ready:

```python
FALLBACK_QUOTES = [
    {"q": "The only way to do great work is to love what you do.", "a": "Steve Jobs"},
    {"q": "Stay hungry, stay foolish.", "a": "Steve Jobs"},
    {"q": "Innovation distinguishes between a leader and a follower.", "a": "Steve Jobs"},
    {"q": "Life is what happens when you're busy making other plans.", "a": "John Lennon"},
    {"q": "The future belongs to those who believe in the beauty of their dreams.", "a": "Eleanor Roosevelt"},
]

def get_fallback_quote():
    """Return a random fallback quote"""
    import random
    return random.choice(FALLBACK_QUOTES)
```
