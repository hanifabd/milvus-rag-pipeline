from typing import List, Optional, Literal, Union
from pydantic import BaseModel, validator, model_validator, Field

class OutputModelMain(BaseModel):
    status: str
    api: str

    class Config:
        json_schema_extra = {
            "example": {
                "status": "ok",
                "api": "information-retrieval",
            }
        }

class OutputModelUpload(BaseModel):
    status: str
    timestamp: float
    file_path: str

    class Config:
        json_schema_extra = {
            "example": {
                "status": "SUCCESS",
                "timestamp": 1730170211.2242904,
                "file_path": "uploaded_information_data\\mbappe_knowledge_3762f305-fbd6-45f8-929d-2fbc41af92fb.pdf"

            }
        }

class OutputModelInsert(BaseModel):
    task_id: str
    status: str
    timestamp: float

    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "acbd1626-bcf9-4203-841e-80c9a00e8cbd",
                "status": "PENDING",
                "timestamp": 1730170211.2242904
            }
        }

class StatusDataModel(BaseModel):
    client_id: str
    project_id: str
    collection_name: str
    collection_index_type: str
    file_id: str
    file: str
    chunks: int
    separator_type: str
    status: str
    timestamp: float

class OutputModelInsertStatus(BaseModel):
    task_id: str
    status: str
    timestamp: float
    data: List[StatusDataModel]

    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "acbd1626-bcf9-4203-841e-80c9a00e8cbd",
                "status": "PENDING || SUCCESS",
                "timestamp": 1730170211.2242904,
                "data": [
                    {
                        "client_id": "ex_client_id",
                        "project_id": "ex_project_id",
                        "collection_name": "ex_collection_name",
                        "collection_index_type": "IVF_FLAT",
                        "file_id": "5903840b-f74b-4782-a014-235b34476cf9",
                        "file": "<base_url>/kota_blora_knowledge.pdf",
                        "chunks": 10,
                        "separator_type": "CustomTag",
                        "status": "success",
                        "timestamp": 1730171442.124015
                    },
                    # Additional data items...
                ]
            }
        }

class OutputModelDelete(BaseModel):
    delete_chunks: int
    timestamp: float

    class Config:
        json_schema_extra = {
            "example": {
                "delete_chunks": 10,
                "timestamp": 1730171442.124015

            }
        }

class SearchResultModel(BaseModel):
    score: float
    text: str

class OutputModelSearch(BaseModel):
    timestamp: float
    search_time: float
    data: List[SearchResultModel]

    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": 1730172634.3079963,
                "search_time": 1.7687828540802002,
                "data": [
                    {
                        "score": 0.8918651342391968,
                        "text": "\nApa saja tantangan dan pencapaian yang dihadapi Kylian Mbappé sepanjang kariernya\nhingga saat ini?\n...",
                    },
                    # Additional results...
                ]
            }
        }

class OutputModelError(BaseModel):
    detail: str

    class Config:
        json_schema_extra = {
            "example": {
                "detail": "string"
            }
        }

class InsertModel(BaseModel):
    client_id: str = Field(..., description="Client ID")  # Mandatory field
    project_id: str = Field(..., description="Project ID")  # Mandatory field
    collection_name: str = Field(..., description="Collection Name")  # Mandatory field
    collection_index_type: Literal["IVF_FLAT", "HNSW"] = Field("IVF_FLAT", description="Collection Index Type")  # Default to IVF_FLAT
    files_path: List[str] = Field(..., description="List of file paths (only PDFs)")  # Mandatory field
    separator_type: Literal["SeparatorTextSplitter", "CharacterTextSplitter", "RecursiveCharacterTextSplitter", "IndoLegalTextSplitter"] = Field("CharacterTextSplitter", description="Separator Engine")  # Default to CharacterTextSplitter
    separator: Optional[Union[str, List[str]]] = Field(None, description="Information separator in documents")  # Optional field, can be str or list of strings
    chunk_size: Optional[int] = Field(None, description="Document's chunk size")  # Optional field
    chunk_overlap: Optional[int] = Field(None, description="Document's chunk overlap")  # Optional field

    # Custom validator to check if files are PDFs
    @validator('files_path', each_item=True)
    def check_pdf_extension(cls, file_path: str):
        if not file_path.lower().endswith(".pdf"):
            raise ValueError(f"File '{file_path}' is not a PDF.")
        return file_path

    # Root validator for separator_type and separator relationship
    @model_validator(mode="after")
    def validate_separator(self):
        if self.separator_type in ["SeparatorTextSplitter", "CharacterTextSplitter"] and not isinstance(self.separator, (str, type(None))):
            raise ValueError("For 'CharacterTextSplitter', 'separator' must be a string.")
        elif self.separator_type == "RecursiveCharacterTextSplitter" and not isinstance(self.separator, (list, type(None))):
            raise ValueError("For 'RecursiveCharacterTextSplitter', 'separator' must be a list of strings.")
        return self

    # Validator for chunk size and overlap logic
    @model_validator(mode="after")
    def validate_chunk_size_and_overlap(self):
        if self.chunk_size is not None and self.chunk_overlap is not None:
            if self.chunk_size < self.chunk_overlap:
                raise ValueError("'chunk_size' must be greater than 'chunk_overlap'.")
        return self

class DeleteModel(BaseModel):
    client_id: str = Field(..., description="Client ID")  # Mandatory field
    project_id: str = Field(..., description="Project ID")  # Mandatory field
    collection_name: str = Field(..., description="Collection Name")  # Mandatory field
    file_id: str = Field(..., description="Collection Name")  # Mandatory field

class SearchModel(BaseModel):
    client_id: str = Field(..., description="Client ID")  # Mandatory field
    project_id: str = Field(..., description="Project ID")  # Mandatory field
    collection_name: str = Field(..., description="Collection Name")  # Mandatory field
    collection_index_type: Literal["IVF_FLAT", "HNSW"] = Field("IVF_FLAT", description="Collection Index Type")  # Default to IVF_FLAT, options are IVF_FLAT or HNSW
    query: str = Field(..., description="Search Query")  # Mandatory field
    number_results: int = Field(..., description="Number of Results")  # Mandatory field
    rerank: Optional[bool] = Field(False, description="Rerank Documents")  # Optional field