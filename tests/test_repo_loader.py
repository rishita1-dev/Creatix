from rag.repo_loader import load_github_repository


repo_url = "https://github.com/rishita1-dev/Creatix"

documents = load_repository(repo_url)

print(f"Total files loaded: {len(documents)}")

for document in documents[:5]:
    print("\nFile:", document["file_path"])
    print("Content preview:", document["content"][:200])