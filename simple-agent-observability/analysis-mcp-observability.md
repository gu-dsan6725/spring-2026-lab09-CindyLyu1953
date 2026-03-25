# MCP Observability Analysis

![MCP tools `resolve-library-id` and `query-docs` in a Braintrust trace](braintrust-mcp-tool.png)

I connected to the **Context7** MCP server over streamable HTTP (`https://mcp.context7.com/mcp`) and exposed its documentation tools through Strands’ `MCPClient` alongside the existing DuckDuckGo tool. The trace above comes from a run where the model first resolved a library (for example, it returned the Context7 id `/fastapi/fastapi` for FastAPI in the `resolve-library-id` tool output panel), then issued **`query-docs`** in a later cycle before the final `chat` response.

In Braintrust, **MCP tool calls** show up like other tools—as `execute_tool …` spans nested under `execute_event_loop_cycle`, each with duration and ordering after a `chat` span. Here they appear as a short chain: resolve library, query docs, then a concluding model turn. **DuckDuckGo** runs the same way (`execute_tool duckduckgo_search`), but its inputs are open web queries and its outputs are search hits, whereas the Context7 tools take structured arguments (library id and doc-focused questions) and return curated documentation snippets. That difference is easy to see in the span outputs: MCP steps surface library metadata and doc text, while DuckDuckGo steps surface ranked web results.
