# LangGraph Daily Exercise: AI-Powered Quote Aggregator

## Problem Statement

Build a LangGraph that processes user requests for inspirational quotes. The graph uses an LLM to understand the user's intent, fetches quotes from a free API, and returns them formatted nicely. This exercise teaches you how to integrate LLMs with external APIs in a LangGraph workflow.

## Learning Objectives

- Master **StateGraph** with typed state using TypedDict
- Learn **LLM tool calling** patterns in LangGraph
- Practice **external API integration** as LangChain tools
- Understand **conditional routing** based on LLM decisions
- Build a complete **FastAPI endpoint** wrapping your graph

## Graph Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   START     │────▶│  PROCESS    │────▶│   FETCH     │
│  (entry)    │     │  (LLM node) │     │  (API node) │
└─────────────┘     └─────────────┘     └─────────────┘
                           │                    │
                           ▼                    ▼
                    ┌─────────────┐     ┌─────────────┐
                    │   ROUTE     │────▶│   FORMAT    │
                    │ (conditional)│     │  (output)   │
                    └─────────────┘     └─────────────┘
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
        ┌──────────┐             ┌──────────┐
        │  QUOTE   │             │ FALLBACK │
        │  (fetch) │             │ (error)  │
        └──────────┘             └──────────┘
```

**Nodes:**
1. `process` - LLM analyzes user request, decides if quote is needed
2. `fetch_quote` - Calls external quote API
3. `format_response` - Formats the quote for output
4. `fallback` - Handles errors gracefully

**Edges:**
- `START` → `process`
- `process` → `fetch_quote` (if quote needed)
- `fetch_quote` → `format_response`
- `format_response` → `END`
- `process` → `fallback` (if invalid request)

## Requirements

- [ ] Define typed state with TypedDict (include: input, intent, quote, formatted_output, error)
- [ ] Create LLM node that uses ChatOpenAI or compatible LLM
- [ ] Integrate Quote API as a LangChain tool with @tool decorator
- [ ] Add conditional routing based on LLM decision
- [ ] Implement error handling with fallback node
- [ ] Create FastAPI endpoint at `/graph`
- [ ] Return structured JSON response with success/error fields

## Success Criteria

1. Graph accepts string input and returns formatted quote
2. LLM correctly identifies quote requests vs. other queries
3. Quote API integration works (or gracefully falls back)
4. Response includes: success status, result, metadata
5. Invalid input returns appropriate error message

## Performance Targets (Small Scale)

- Sequential: < 30s avg (LLM calls dominate)
- Concurrent: > 1 qps throughput
- Success rate: > 90%

## Estimated Time

**Small Scale**: 15-30 minutes

## API Used

- **ZenQuotes API** (`https://zenquotes.io/api/random`) - Free inspirational quotes
  - No API key required
  - Rate limit: reasonable for testing
  - Returns array of quote objects

## Example Interaction

**Input:** "Give me an inspirational quote"
**Output:** 
```json
{
  "success": true,
  "result": {
    "quote": "The only way to do great work is to love what you do.",
    "author": "Steve Jobs"
  },
  "metadata": {
    "intent": "quote_request",
    "api_source": "zenquotes"
  }
}
```

**Input:** "Hello there"
**Output:**
```json
{
  "success": true,
  "result": {
    "message": "Greetings! I can provide inspirational quotes. Just ask!"
  },
  "metadata": {
    "intent": "greeting"
  }
}
```
