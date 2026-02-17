from get_embedding_function import get_embedding_function
from langchain_chroma import Chroma

def create_vector_store(chunks, persist_directory="db/chroma_db"):
    # Create a vector store from the chunks
    print("Creating vector store...")
    if not chunks:
        print("No chunks to create vector store.")
        return None

    embedding_model = get_embedding_function()

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model,
        persist_directory=persist_directory,
        collection_metadata={"hnsw:space": "cosine"}
        )

    print(f"Vector store created and saved to {persist_directory}.")
    return vector_store