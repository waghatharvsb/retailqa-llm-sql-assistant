import asyncio, os, sys
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()
HERE = os.path.dirname(os.path.abspath(__file__))

SYSTEM = """You are a retail database assistant with a MySQL database of t-shirts.
Work in this order:
1. Call search_examples with the user's question.
2. Call get_schema.
3. Write ONE MySQL SELECT query and call run_sql.
4. If run_sql returns ERROR, fix the query and call run_sql again (max 2 retries).
5. Answer in one or two plain-English sentences using ONLY the SQL result. If no rows or None, say no matching records were found. Do not mention SQL.

Rules:
- Never use SELECT *. Use LIMIT 5 unless the question asks for a number of rows (not needed for SUM/COUNT).
- price is the price of ONE t-shirt. Inventory value or revenue = SUM(price * stock_quantity).
- The number of t-shirts in stock = SUM(stock_quantity).
- Brands are exactly: 'Van Huesen', 'Levi', 'Nike', 'Adidas' ("Levi's" means 'Levi').
- discounts.pct_discount is a percentage linked by t_shirt_id. For revenue after discounts, LEFT JOIN discounts and use COALESCE(pct_discount, 0).
"""


async def build_agent():
    client = MultiServerMCPClient({
        "retail": {
            "transport": "stdio",
            "command": sys.executable,
            "args": [os.path.join(HERE, "mcp_server.py")],
        }
    })
    tools = await client.get_tools()
    for t in tools:
        t.handle_tool_error = True  # send tool errors back to the LLM instead of crashing
    llm = ChatOllama(
        model=os.getenv("OLLAMA_MODEL", "llama3.1:latest"),
        temperature=0,
        base_url=os.getenv("OLLAMA_URL", "http://localhost:11434"),
    )
    return create_agent(llm, tools, system_prompt=SYSTEM)


async def ask(agent, question):
    out = await agent.ainvoke(
        {"messages": [{"role": "user", "content": question}]},
        config={"recursion_limit": 12},
    )
    return out["messages"]


if __name__ == "__main__":
    async def main():
        agent = await build_agent()
        q = "How many Levi t-shirts are in stock?"
        seen = 0
        try:
            async for state in agent.astream(
                {"messages": [{"role": "user", "content": q}]},
                config={"recursion_limit": 12},
                stream_mode="values",
            ):
                msgs = state["messages"]
                for m in msgs[seen:]:
                    calls = getattr(m, "tool_calls", None)
                    print(f"[{m.type}]", calls if calls else str(m.content)[:300], "\n")
                seen = len(msgs)
        except Exception as e:
            print("STOPPED:", type(e).__name__)

    asyncio.run(main())