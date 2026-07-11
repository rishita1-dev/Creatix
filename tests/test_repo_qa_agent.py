from agents.repo_qa_agent import RepoQAAgent


repo_url = "https://github.com/rishita1-dev/Creatix"


print("Creating Repository Q&A Agent...")

agent = RepoQAAgent()


print("\nLoading and indexing repository...")

stats = agent.load_repository(repo_url)

print("\nRepository loaded successfully!")
print("Files loaded:", stats["files_loaded"])
print("Chunks created:", stats["chunks_created"])


question = "How does the backend process user requests?"

print("\nQuestion:")
print(question)


print("\nGenerating answer...")

answer = agent.ask(question)


print("\nAnswer:")
print(answer)