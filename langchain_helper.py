import os
import re
import uuid
from decimal import Decimal

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from langchain_community.utilities import SQLDatabase
from langchain_ollama import ChatOllama
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate

from few_shots import few_shots

load_dotenv()

PREFIX = """You are a MySQL expert. Given an input question, write ONE syntactically correct MySQL SELECT query that answers it.

Rules:
- Return only the SQL query. No explanation, no markdown, no code fences.
- Use only the tables and columns shown below. Never query columns that do not exist.
- Never use SELECT *. Select only the columns needed.
- Unless the question asks for a specific number of rows, return at most {top_k} rows using LIMIT (not needed for aggregates such as SUM or COUNT).
- price is the price of ONE t-shirt. Inventory value or revenue = SUM(price * stock_quantity).
- The number of t-shirts in stock = SUM(stock_quantity).
- Brands are exactly: 'Van Huesen', 'Levi', 'Nike', 'Adidas' (so "Levi's" means 'Levi' and "Van Heuson" means 'Van Huesen').
- discounts.pct_discount is a percentage linked by t_shirt_id. For revenue after discounts, LEFT JOIN discounts and use COALESCE(pct_discount, 0).

Table information:
{schema}

Here are similar questions with correct queries:"""

SUFFIX = "\nQuestion: {Question}\nSQLQuery:"

ANSWER_PROMPT = """You are a helpful retail assistant. Using ONLY the SQL result below, answer the question in one or two plain-English sentences. If no rows were returned or the value is None, say that no matching records were found. Do not mention SQL.

Question: {question}
SQL used: {sql}
SQL result:
{result}

Answer:"""

FORBIDDEN = re.compile(
    r"\b(insert|update|delete|drop|alter|truncate|create|grant|revoke|replace|"
    r"rename|call|outfile|dumpfile|load_file|sleep|benchmark)\b",
    re.I,
)


def clean_sql(raw):
    s = raw.strip()
    m = re.search(r"```(?:sql)?\s*(.*?)```", s, re.S | re.I)
    if m:
        s = m.group(1)
    s = re.sub(r"^\s*SQLQuery:\s*", "", s, flags=re.I)
    return s.strip()


def is_safe_select(sql):
    s = sql.strip().rstrip(";").strip()
    if not s or ";" in s or "--" in s or "/*" in s:
        return False
    if not re.match(r"(?is)^(select|with)\b", s):
        return False
    return not FORBIDDEN.search(s)


def _fmt(v):
    if isinstance(v, Decimal):
        v = float(v)
        return str(int(v)) if v == int(v) else f"{v:.2f}"
    return str(v)


def format_result(cols, rows):
    if not rows:
        return "No rows returned."
    lines = [" | ".join(cols)] + [" | ".join(_fmt(v) for v in r) for r in rows]
    return "\n".join(lines)


def get_few_shot_db_chain():
    # DB connection with the read-only app user (credentials come from .env)
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
    schema = db.get_table_info()

    # Llama via Ollama
    llm = ChatOllama(
        model=os.getenv("OLLAMA_MODEL", "llama3.1:latest"),
        temperature=0,
        base_url=os.getenv("OLLAMA_URL", "http://localhost:11434"),
    )

    # Few-shot retrieval: embed only the questions, store in Chroma, fetch the 3 closest
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
    )
    example_selector = SemanticSimilarityExampleSelector.from_examples(
        few_shots,
        embeddings,
        Chroma,
        k=3,
        input_keys=["Question"],
        collection_name=f"few_shots_{uuid.uuid4().hex[:8]}",
    )

    few_shot_prompt = FewShotPromptTemplate(
        example_selector=example_selector,
        example_prompt=PromptTemplate.from_template("\nQuestion: {Question}\nSQLQuery: {SQLQuery}"),
        prefix=PREFIX,
        suffix=SUFFIX,
        input_variables=["Question", "schema", "top_k"],
    )

    def ask(question):
        prompt = few_shot_prompt.format(Question=question, schema=schema, top_k=5)
        sql = clean_sql(llm.invoke(prompt).content)

        if not is_safe_select(sql):
            return {"sql": sql, "result": None,
                    "answer": "Sorry, I can only run read-only SELECT queries, and the generated query was not safe to run."}
        try:
            with engine.connect() as conn:
                res = conn.execute(text(sql))
                cols = list(res.keys())
                rows = res.fetchmany(50)
        except Exception as e:
            return {"sql": sql, "result": str(e),
                    "answer": "The generated SQL failed to run. Please try rephrasing your question."}

        result_text = format_result(cols, rows)
        answer = llm.invoke(ANSWER_PROMPT.format(question=question, sql=sql, result=result_text)).content.strip()
        return {"sql": sql, "result": result_text, "answer": answer}

    return ask