# pip install anthropic
# export ANTHROPIC_API_KEY=...

from graver import Prompt

# Uncomment to run against the real API:
# import anthropic
# client = anthropic.Anthropic()

p = Prompt("system")

p.save("You are a helpful assistant.")
p.save("You are a senior software engineer. Be direct. Skip pleasantries.")

# Check full history
for entry in p.log():
    flag = " [main]" if entry["is_main"] else ""
    print(f"{entry['version']}  {entry['timestamp']}{flag}")

# Pin the version to use in production
p.set_main("v2")
system_prompt = p.get_main()

# message = client.messages.create(
#     model="claude-opus-4-5",
#     max_tokens=1024,
#     system=system_prompt,
#     messages=[{"role": "user", "content": "Review this function for bugs."}],
# )
# print(message.content[0].text)
