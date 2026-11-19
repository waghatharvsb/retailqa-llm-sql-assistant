import asyncio, sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    params = StdioServerParameters(command=sys.executable, args=["mcp_server.py"])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            print("TOOLS:", [t.name for t in tools.tools])

            r = await session.call_tool("get_schema", {})
            print("\nSCHEMA:\n", r.content[0].text[:400])

            r = await session.call_tool(
                "run_sql", {"sql_query": "SELECT SUM(stock_quantity) AS total FROM t_shirts"}
            )
            print("\nGOOD QUERY:\n", r.content[0].text)

            r = await session.call_tool("search_examples", {"question": "How many Nike shirts do we have?"})
            print("\nEXAMPLES:\n", r.content[0].text)

            r = await session.call_tool("run_sql", {"sql_query": "DROP TABLE t_shirts"})
            print("\nBAD QUERY:\n", r.content[0].text)


asyncio.run(main())