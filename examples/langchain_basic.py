# pip install langchain-core langchain-openai
# export OPENAI_API_KEY=...

from graver import Prompt

# Uncomment to run against the real API:
# from langchain_core.messages import SystemMessage, HumanMessage
# from langchain_openai import ChatOpenAI

p = Prompt("system")

p.save("You are a helpful assistant.")
p.save("You are a technical writer. Explain concepts clearly with examples.")

p.set_main("v2")
system_prompt = p.get_main()

# llm = ChatOpenAI(model="gpt-4o")
# response = llm.invoke([
#     SystemMessage(content=system_prompt),
#     HumanMessage(content="Explain what a context window is."),
# ])
# print(response.content)
