
from typing import List
import json

from unstructured.partition.pdf import partition_pdf
from unstructured.chunking.title import chunk_by_title
from langchain_core.documents import Document
from langchain_ollama import OllamaLLM
from langchain_core.messages import HumanMessage
from populate_database import create_vector_store

def partition_documents(file_path):
    print(f"Partitioning document: {file_path}")
    elements = partition_pdf(
        filename=file_path,
        strategy="hi_res",
        infer_table_structure=True,
        extract_image_block_types=["Image"],
        extract_image_block_to_payload=True
        )
    print(f"Partitioned {len(elements)} elements.")
    return elements

def create_chunk_by_title(elements):
    print("Creating chunks by title...")
    chunks = chunk_by_title(
        elements,
        max_characters=3000,
        new_after_n_chars=2400,
        combine_text_under_n_chars=500
        )
    print(f"Created {len(chunks)} chunks.")
    return chunks

def separate_content_types(chunk):
    print("Separating content types in chunk...")
    content_data = {
        "text": chunk.text,
        "tables": [],
        "images": [],
        "types": ['text']
    }

    if hasattr(chunk, "metadata") and hasattr(chunk.metadata, "orig_elements"):
        for element in chunk.metadata.orig_elements:
            element_type = type(element).__name__

            if element_type == "Table":
                content_data["types"].append("table")
                table_html = getattr(element.metadata, "text_as_html", element.text)
                content_data["tables"].append(table_html)
            elif element_type == "Image":
                if hasattr(element, 'metadata') and hasattr(element.metadata, "image_base64"):
                    element.filename = element.metadata.filename
                    content_data["types"].append("image")
                    content_data["images"].append(element.metadata.image_base64)
    content_data["types"] = list(set(content_data["types"]))
    return content_data

def create_ai_enhanced_summary(text: str, tables: List[str], images: List[str]) -> str:
    print("Creating AI-enhanced summary...")
    
    try:
        llm =  OllamaLLM(model="llama3.2:latest")
        prompt_text = f"""You are creating a searchable description for document content retrieval.

        CONTENT TO ANALYZE:
        TEXT CONTENT:
        {text}

        """
        if tables:
            prompt_text += "TABLES:\n"
            for i, table in enumerate(tables):
                prompt_text += f"TABLE {i+1}:\n{table}\n\n"

                prompt_text += """
                YOUR TASK:
                Genarate a comprehensive, searchable description tha covers:

                1. Key facts, numbers, and data points from text and tables
                2. Main topics and concepts discussed.
                3. Questions this content could answer.
                4. Visual content analysis (charts, diagrams, patterns in images)
                5. Alternative search terms users might use

                Make it detailed and searchable - prioritize findability over brevity.

                SEARCHABLE DESCRIPTION:
                """

        message_content = [{"type": "text", "text": prompt_text}]

        for image_base64 in images:
            message_content.append({
                "type": "image_url",
                    "image_url": f"data:image/jpeg;base64,{image_base64}"
                    })
            
        message = HumanMessage(content=message_content)
        response = llm.invoke([message])
        return response
    except Exception as e:
        print(f"Error in AI summary generation: {e}")
        summary = f"{text[:300]}..."
        if tables:
            summary += f" [Contains {len(tables)} table(s)]"
        if images:
            summary += f" [Contains {len(images)} image(s)]"
        return summary

def summarise_chunks(chunks):
    print("Summarising chunks...")
    langchain_documents = []
    total_chunks = len(chunks)

    for i, chunk in enumerate(chunks):
        current_chunk = i + 1
        print(f"Summarising chunk {current_chunk}/{total_chunks}...")

        content_data = separate_content_types(chunk)

        print(f"Types found: {content_data['types']}")
        print(f"Tables: {len(content_data['tables'])}, Images: {len(content_data['images'])}")

        if content_data["tables"] or content_data["images"]:
            print("Creating AI summary for chunk with tables/images...")
            try:
                enhanced_content = create_ai_enhanced_summary(
                    content_data["text"],
                    content_data["tables"],
                    content_data["images"]
                )
                print("Enhanced AI summary created successfully.")
                print(f"Enhanced summary: {enhanced_content[:200]}...")  # Print first 200 chars of summary
            except Exception as e:
                print(f"Error creating AI summary: {e}")
                enhanced_content = content_data["text"]
        else:
            print("No tables/images found, using original text.")
            enhanced_content = content_data["text"]

        doc = Document(
            page_content=enhanced_content,
            metadata={
                "original_content": json.dumps({
                    "raw_text": content_data['text'],
                    "tables_html": content_data['tables'],
                    "images_base64": content_data['images']
                })            
            })
        langchain_documents.append(doc)
    return langchain_documents

def export_chunks_to_json(chunks, filename="chunks_export.json"):
    """Export processed chunks to clean JSON format"""
    export_data = []
    
    for i, doc in enumerate(chunks):
        chunk_data = {
            "chunk_id": i + 1,
            "enhanced_content": doc.page_content,
            "metadata": {
                "original_content": json.loads(doc.metadata.get("original_content", "{}"))
            }
        }
        export_data.append(chunk_data)
    
    # Save to file
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Exported {len(export_data)} chunks to {filename}")
    return export_data

def main():
    elements = partition_documents("docs/history.pdf")
    chunks = create_chunk_by_title(elements)
    print(elements)
    processed_chunks = summarise_chunks(chunks)
    json_data = export_chunks_to_json(processed_chunks)
    create_vector_store(processed_chunks)

if __name__ == "__main__":
    main()