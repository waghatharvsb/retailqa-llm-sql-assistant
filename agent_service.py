import asyncio, os, sys, threading
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.errors import GraphRecursionError

from agent import SYSTEM

load_dotenv()
HERE = os.path.dirname(os.path.abspath(__file__))
EXTRA = "\n- If the same tool returns an error twice, stop and tell the user you could not get the answer."


def _text(content):
    if isinstance(content, list):
        return "\n".join(b.get("text", "") for b in content if isinstance(b, dict))
    return str(content)


class AgentService:
    def __init__(self):
        self.agent = None
        self.error = None
        self.ready = threading.Event()
        self.loop = asyncio.new_event_loop()
        threading.Thread(target=self.loop.run_forever, daemon=True).start()
        asyncio.run_coroutine_threadsafe(self._main(), self.loop)
        self.ready.wait(timeout=120)
        if self.error:
            raise self.error

    async def _main(self):
        try:
            MCP_URL = os.getenv("MCP_URL")
            if MCP_URL:   # Docker: connect to the MCP service over HTTP
                conn = {"transport": "streamable_http", "url": MCP_URL}
            else:         # local dev: start the server as a subprocess
                conn = {
                    "transport": "stdio",
                    "command": sys.executable,
                    "args": [os.path.join(HERE, "mcp_server.py")],
                    "env": dict(os.environ),
                }
            client = MultiServerMCPClient({"retail": conn})
            # session stays open for the whole app lifetime
            async with client.session("retail") as session:
                tools = await load_mcp_tools(session)
                for t in tools:
                    t.handle_tool_error = True
                llm = ChatOllama(
                    model=os.getenv("OLLAMA_MODEL", "llama3.1:latest"),
                    temperature=0,
                    base_url=os.getenv("OLLAMA_URL", "http://localhost:11434"),
                )
                self.agent = create_agent(llm, tools, system_prompt=SYSTEM + EXTRA)
                self.ready.set()
                await asyncio.Event().wait()  # keep the session alive
        except Exception as e:
            self.error = e
            self.ready.set()

    async def _ask(self, question):
        try:
            out = await self.agent.ainvoke(
                {"messages": [{"role": "user", "content": question}]},
                config={"recursion_limit": 12},
            )
        except GraphRecursionError:
            return {"answer": "Sorry, I could not work out the answer. Please rephrase.",
                    "steps": [], "sql": None, "result": None}
        msgs = out["messages"]
        steps, sql, result = [], None, None
        for m in msgs:
            if m.type == "ai" and getattr(m, "tool_calls", None):
                for c in m.tool_calls:
                    steps.append(f"{c['name']}({c['args']})")
                    if c["name"] == "run_sql":
                        sql = c["args"].get("sql_query")
            elif m.type == "tool" and m.name == "run_sql":
                result = _text(m.content)
        return {"answer": _text(msgs[-1].content), "steps": steps, "sql": sql, "result": result}

    def ask(self, question):
        return asyncio.run_coroutine_threadsafe(self._ask(question), self.loop).result()