from langchain_ollama import ChatOllama

llm = ChatOllama(model="llama3.1:latest", temperature=0, base_url="http://localhost:11434")
reply = llm.invoke("Write a MySQL query for the total stock_quantity of all Nike t-shirts in table t_shirts. Return only SQL.")
print(reply.content)
