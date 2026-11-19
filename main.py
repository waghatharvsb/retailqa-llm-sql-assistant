import streamlit as st
from agent_service import AgentService

st.title("AtliQ T Shirts: Agentic Database Q&A 👕")


@st.cache_resource(show_spinner="Starting MCP server and agent...")
def load_agent():
    return AgentService()


question = st.text_input("Question: ")

if question:
    svc = load_agent()
    with st.spinner("Thinking..."):
        r = svc.ask(question)

    st.header("Answer")
    st.write(r["answer"])

    with st.expander("Show tool calls, SQL and raw result"):
        st.code("\n".join(r["steps"]) or "no tool calls")
        st.code(r["sql"] or "", language="sql")
        st.text(r["result"] or "")