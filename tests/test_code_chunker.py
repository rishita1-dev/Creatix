from rag.repo_loader import load_github_repository
from rag.code_chunker import chunk_documents


repo_url = "https://github.com/rishita1-dev/Creatix"

print("Loading repository...")

documents = load_github_repository(repo_url)

print(f"Total files loaded: {len(documents)}")

chunks = chunk_documents(documents)

print(f"Total chunks created: {len(chunks)}")


for chunk in chunks[:5]:
    print("\n" + "=" * 50)
    print("File:", chunk["file_path"])
    print("Chunk number:", chunk["chunk_number"])
    print("Content preview:")
    print(chunk["content"][:300])