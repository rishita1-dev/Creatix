from rag.repo_loader import load_repository
from rag.code_chunker import chunk_documents
from rag.vector_store import CodeVectorStore


repo_url = "https://github.com/rishita1-dev/Creatix"


print("1. Loading repository...")

documents = load_repository(repo_url)

print(f"Files loaded: {len(documents)}")


print("\n2. Creating chunks...")

chunks = chunk_documents(documents)

print(f"Chunks created: {len(chunks)}")


print("\n3. Building vector index...")

vector_store = CodeVectorStore()

vector_store.build_index(chunks)


print("\n4. Searching repository...")

question = "How does the backend process user requests?"

results = vector_store.search(
    query=question,
    top_k=5
)


print("\nMost relevant code chunks:")

for result in results:

    print("\n" + "=" * 60)

    print("File:", result["file_path"])

    print("Chunk:", result["chunk_number"])

    print("Similarity score:", result["score"])

    print("\nContent preview:")

    print(result["content"][:500])