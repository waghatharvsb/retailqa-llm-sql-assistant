FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HF_HOME=/opt/hf \
    PIP_DEFAULT_TIMEOUT=300 \
    PIP_RETRIES=10

WORKDIR /app

# torch's small dependencies come from PyPI first
RUN pip install --no-cache-dir filelock typing-extensions sympy networkx jinja2 fsspec

# CPU-only torch, installed from the wheel downloaded on the host
COPY wheels/ /tmp/wheels/
RUN if ls /tmp/wheels/torch-*.whl >/dev/null 2>&1; then \
        pip install --no-cache-dir /tmp/wheels/torch-*.whl; \
    else \
        pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu; \
    fi && rm -rf /tmp/wheels

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Bake the embedding model into the image
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"

COPY few_shots.py sql_guard.py mcp_server.py agent.py agent_service.py main.py ./

EXPOSE 8501
CMD ["streamlit", "run", "main.py", "--server.address=0.0.0.0", "--server.port=8501", "--browser.gatherUsageStats=false"]
