# pip install openai
# export OPENAI_API_KEY=...

from graver import Prompt

# Uncomment to run against the real API:
# from openai import OpenAI
# client = OpenAI()

p = Prompt("system")

# Iterate on the prompt
p.save("You are a helpful assistant.")
p.save("You are an expert analyst. Answer in bullet points. Be concise.")

print(p.changes())
# system  |  v1 -> v2
# + ADDED: You are an expert analyst. Answer in bullet points. Be concise.
# - REMOVED: You are a helpful assistant.

# Pin the version that performs best
p.set_main("v2")

# Use it — get_main() always returns the pinned version
system_prompt = p.get_main()

# response = client.chat.completions.create(
#     model="gpt-4o",
#     messages=[
#         {"role": "system", "content": system_prompt},
#         {"role": "user", "content": "Summarise the key risks of LLMs in production."},
#     ],
# )
# print(response.choices[0].message.content)
