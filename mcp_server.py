import os
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from langchain_community.utilities import SQLDatabase
from sql_guard import clean_sql, is_safe_select, format_result
import uuid
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from few_shots import few_shots

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

mcp = FastMCP(
    "retail-sql-tools",
    host=os.getenv("MCP_HOST", "127.0.0.1"),
    port=int(os.getenv("MCP_PORT", "8000")),
)

engine = create_engine(
    URL.create(
        "mysql+pymysql",
        username=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", 3306)),
        database=os.getenv("DB_NAME"),
    ),
    pool_pre_ping=True,
)
db = SQLDatabase(engine, include_tables=["t_shirts", "discounts"], sample_rows_in_table_info=3)


@mcp.tool()
def get_schema() -> str:
    """Return the CREATE TABLE definitions and 3 sample rows for the
    t_shirts and discounts tables. Call this before writing SQL."""
    return db.get_table_info()


@mcp.tool()
def run_sql(sql_query: str = "", query: str = "") -> str:
    """Run ONE read-only MySQL SELECT query and return up to 50 rows as text.
    The argument sql_query is the full SQL string.
    If the result starts with 'ERROR', read the message, fix the query and try again."""
    sql = clean_sql(sql_query or query)
    if not is_safe_select(sql):
        return "ERROR: only a single read-only SELECT query is allowed."
    try:
        with engine.connect() as conn:
            res = conn.execute(text(sql))
            cols = list(res.keys())
            rows = res.fetchmany(50)
    except Exception as e:
        return f"ERROR: {e}"
    return format_result(cols, rows)


_selector = None

def _get_selector():
    global _selector
    if _selector is None:  # built once, on first call
        emb = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"},
        )
        _selector = SemanticSimilarityExampleSelector.from_examples(
            few_shots, emb, Chroma, k=3, input_keys=["Question"],
            collection_name=f"few_shots_{uuid.uuid4().hex[:8]}",
        )
    return _selector


@mcp.tool()
def search_examples(question: str) -> str:
    """Return 3 solved example questions with correct SQL that are most similar
    to the given question. Call this first to see how similar questions were solved."""
    ex = _get_selector().select_examples({"Question": question})
    return "\n\n".join(f"Question: {e['Question']}\nSQLQuery: {e['SQLQuery']}" for e in ex)

if __name__ == "__main__":
    if os.getenv("MCP_TRANSPORT", "stdio") == "stdio":
        mcp.run(transport="stdio")
    else:
        mcp.run(transport="streamable-http")