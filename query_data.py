from langchain_chroma import Chroma
from get_embedding_function import get_embedding_function
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_ollama import OllamaLLM

def main():
    print("Query Data Main Function")
    embedding_model = get_embedding_function()

    db = Chroma(
        persist_directory="db/chroma_db",
        embedding_function=embedding_model,
        collection_metadata={"hnsw:space": "cosine"}
    )

    query = "How much amount was claimed for the service?"

    retriever = db.as_retriever(search_kwargs={"k": 3})

    relevant_docs = retriever.invoke(query)

    print(f"User Query: {query}")
    print ("Printing Context: ")

    for i, doc in enumerate(relevant_docs):
        print(f"Document {i + 1}:")
        print(f"Source: {doc.metadata.get('source')}")
        print(f"Content length: {len(doc.page_content)} characters")
        print(f"Content: {doc.page_content}.")
        print("-" * 50)

    combined_content = f"""Based on the following documents, please answer this question: {query}

    Documents:
    {chr(10).join([f"- {doc.page_content}" for doc in relevant_docs])}

    Please provide a concise and accurate answer to the user's question using the information from the documents. If the documents do not contain enough information to answer the question, please indicate that as well.
    """
    llm = OllamaLLM(model="llama3.2:latest")
    messages = [
        SystemMessage(content="You are a helpful assistant that provides concise and accurate answers to user questions based on the provided documents."),
        HumanMessage(content=combined_content)
    ]
    result = llm.invoke(messages)
    print("Answer:")
    print(result)

if __name__ == "__main__":
    main()