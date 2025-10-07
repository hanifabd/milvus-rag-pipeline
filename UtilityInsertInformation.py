import os
from dotenv import load_dotenv
load_dotenv()
import time
import re
import httpx
import uuid
from typing import List, Optional, Union
from langchain.schema.document import Document
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.text_splitter import RecursiveCharacterTextSplitter
from ManageVectorDB import ManageVectorDB

class InsertInformation:
    def __init__(self):
        self.name = "InsertInformation"
        self.vectorize_url = os.getenv("VECTOR_DOCS_URI")

    def merge_pdf_pages(
        self,
        pages: List[Document],
        client_id: str,
        project_id: str,
        file_id: str):
        try:
            full_content = "".join([page.page_content for page in pages])
            return {
                "text": full_content,
                "file_path": pages[0].metadata.get('file_path'),
                "title": pages[0].metadata.get('title'),
                "total_pages": pages[0].metadata.get('total_pages'),
                "format": pages[0].metadata.get('format'),
                "client_id": client_id,
                "project_id": project_id,
                "file_id": file_id,
            }
        except Exception as e:
            raise Exception(f"Failed to merge pages: {e}")

    def batch_vectorize_documents(self, texts, batch_size=10, timeout=60, retries=3, delay=5):
        all_vectors = []
        # Initialize a synchronous client
        with httpx.Client(timeout=timeout) as client:
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                for attempt in range(retries):
                    try:
                        # Send the request to vectorize the current batch
                        response = client.post(self.vectorize_url, json={"texts": batch})
                        if response.status_code == 200:
                            vectors = response.json().get("vectors", [])
                            all_vectors.extend(vectors)
                            break  # Break out of the retry loop if successful
                        else:
                            raise Exception(f"Failed to vectorize batch: {response.text}")
                    except Exception as e:
                        # print(f"Attempt {attempt + 1} for batch {i // batch_size + 1} failed: {e}")
                        if attempt < retries - 1:
                            time.sleep(delay)  # Wait before retrying
                        else:
                            raise Exception("All retry attempts failed for batch {i // batch_size + 1}.")
        return all_vectors

    def separator_text_splitter(self, document_text, separator):
        informations = document_text.split(separator)
        return informations

    def character_text_splitter(self, document_text, separator, chunk_size, chunk_overlap):
        langchain_text_splitter = CharacterTextSplitter(
            separator=separator,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        informations = [chunk.page_content for chunk in langchain_text_splitter.split_documents([Document(page_content=document_text)])]
        return informations
    
    def recursive_character_text_splitter(self, document_text, separator, chunk_size, chunk_overlap):
        langchain_text_splitter = RecursiveCharacterTextSplitter(
            separator=separator,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        informations = [
            re.sub("|".join(separator), " ", chunk.page_content).strip()
            for chunk in langchain_text_splitter.split_documents([Document(page_content=document_text)])]
        return informations
    
    def indonesia_legal_text_splitter(self, document_text):
        # 0. Clearing Footer with "..." --------------------------------------------------------------------------------------
        document_text = re.sub(r"([^\n]+?(?:\.\s*\.\s*\.\s*|…))", "", document_text)

        # 1. Find BAB Header and Use as Separator ----------------------------------------------------------------------------
        bab_split_pattern = r'(BAB [IVXLCDM]+[\s\n]*[A-Z\s]+)(.*?)(?=BAB [IVXLCDM]+|$)'
        # Find all matches
        matches = re.findall(bab_split_pattern, document_text, re.DOTALL)
        # Extract content before the first "BAB"
        pre_bab_content = re.split(r'BAB [IVXLCDM]+', document_text, maxsplit=1)[0].strip()
        # Combine pre-BAB content and "BAB" segments
        segments = [pre_bab_content] if pre_bab_content else []
        segments.extend([f"{match[0].strip()}\n{match[1].strip()}" for match in matches])

        # 2. Proses Pasal in Each Bab ----------------------------------------------------------------------------------------
        segments_2 = []
        for i, segment in enumerate(segments, start=1):
            # Regular expression to match "BAB" headers
            bab_pattern = r'BAB [IVXLCDM]+[\s\n]*[A-Z\s]+'
            bab_header = re.findall(bab_pattern, segment)
            if bab_header != []:
                # Regular expression to match "Pasal" headers
                pasal_pattern = r'(?:\n{1,2})P(?:\\n|)asal \d+(?:\s*\n{1,2})'
                # Split the text at "Pasal" headers
                split_segments = re.split(pasal_pattern, segment)
                # Capture the headers themselves
                headers = re.findall(pasal_pattern, segment)
                # Combine headers and their respective content
                results = []
                for i, segment in enumerate(split_segments):
                    # Add content before the first "Pasal"
                    if i == 0 and segment.strip():
                        processed_segment = f"{segment.strip()}"
                    elif i > 0:
                        header = headers[i - 1]  # Match the corresponding "Pasal" header
                        processed_segment = f"{header.strip()}\n{segment.strip()}"
                    # Add "BAB" header if not exist
                    if re.findall(bab_pattern, processed_segment) == [] and True:
                        processed_segment = f"{bab_header[0]}\n{processed_segment}"
                    # Append to Result
                    results.append(processed_segment)
                # Append to Final Segment
                segments_2.extend(results)
            else:
                segments_2.append(segment)
        return segments_2

    def insert_information(
        self, 
        client_id: str,
        project_id: str,
        collection_name: str,
        collection_index_type: str,
        files_path: list,
        separator_type: str,
        separator: Optional[Union[str, List[str]]] = None,
        chunk_size: int = 512,
        chunk_overlap: int = 512):

        try:         
            status = []
            for path in files_path:
                file_id = str(uuid.uuid4())
                
                # Load PDF by File Name
                loader = PyMuPDFLoader(path)
                pages = loader.load()

                # Merge Pages
                merged_pages = self.merge_pdf_pages(
                    pages=pages,
                    client_id=client_id,
                    project_id=project_id,
                    file_id=file_id
                )

                # Get Informations
                if separator_type == "SeparatorTextSplitter":
                    informations = self.separator_text_splitter(merged_pages.get("text"), separator)
                elif separator_type == "CharacterTextSplitter":
                    informations = self.character_text_splitter(merged_pages.get("text"), separator, chunk_size, chunk_overlap)
                elif separator_type == "RecursiveCharacterTextSplitter":
                    informations = self.recursive_character_text_splitter(merged_pages.get("text"), separator, chunk_size, chunk_overlap)
                elif separator_type == "IndoLegalTextSplitter":
                    informations = self.indonesia_legal_text_splitter(merged_pages.get("text"))
                # Get Metadata
                metadata = {key: value for key, value in merged_pages.items() if key != "text"}

                # Vectorized Informations
                vectors = self.batch_vectorize_documents(informations, batch_size=10, timeout=60, retries=3, delay=5)

                # Prepare to Milvus Format and Add Metadata
                data = [
                    {"vector": vectors[i], "text": informations[i], **metadata}
                    for i in range(len(vectors))
                ]
                
                # Insert to Milvus Collection
                db_engine = ManageVectorDB()
                insert_info = db_engine.insert_into_collection(collection_name, data)

                status.append({
                    "client_id": client_id,
                    "project_id": project_id,
                    "collection_name": collection_name,
                    "collection_index_type": collection_index_type,
                    "file_id": file_id,
                    "file": path,
                    "chunks": len(data),
                    "separator_type": separator_type,
                    "status": "success",
                    "timestamp": time.time()
                })
        except Exception as e:
            raise Exception(f"Failed to insert documents: {e}")
        return status