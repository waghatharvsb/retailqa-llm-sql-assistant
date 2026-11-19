import streamlit as st
from langchain_helper import get_few_shot_db_chain

st.title("AtliQ T Shirts: Database Q&A 👕")


@st.cache_resource(show_spinner="Loading model and examples...")
def load_chain():
    return get_few_shot_db_chain()


question = st.text_input("Question: ")

if question:
    chain = load_chain()
    with st.spinner("Thinking..."):
        response = chain(question)

    st.header("Answer")
    st.write(response["answer"])

    with st.expander("Show SQL and raw result"):
        st.code(response["sql"], language="sql")
        st.text(response["result"] or "")