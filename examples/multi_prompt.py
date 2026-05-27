from graver import Prompt

system = Prompt("system")
summarizer = Prompt("summarizer")

system.save("You are a helpful assistant.")
system.save("You are an expert assistant. Be concise.")
system.set_main("v2")

summarizer.save("Summarise the following text in three bullet points.")
summarizer.save(
    "Summarise the following text in three bullet points. Focus on actionable insights."
)
summarizer.set_main("v2")

# List all managed prompts
print("Prompts:", Prompt.list_all())

# Each prompt has its own independent history
print("\nsystem history:")
for entry in system.log():
    flag = " [main]" if entry["is_main"] else ""
    print(f"  {entry['version']}  {entry['timestamp']}{flag}")

print("\nsummarizer history:")
for entry in summarizer.log():
    flag = " [main]" if entry["is_main"] else ""
    print(f"  {entry['version']}  {entry['timestamp']}{flag}")

# Use the pinned versions
print("\nActive prompts:")
print("system:", system.get_main())
print("summarizer:", summarizer.get_main())
