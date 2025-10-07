from project_docs import project_info
import os
import time
import uuid
import datetime
import uvicorn
import logging
from pathlib import Path

from fastapi import FastAPI, HTTPException, status, UploadFile, File
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from IOModel import InsertModel, DeleteModel, SearchModel
from IOModel import (
    OutputModelMain,
    OutputModelError,
    OutputModelUpload,
    OutputModelInsert,
    OutputModelInsertStatus,
    OutputModelDelete,
    OutputModelSearch
)

from ManageVectorDB import ManageVectorDB

from app_worker import insert_app, insert_information_worker
from celery.result import AsyncResult
from UtilitySearchInformation import SearchInformation
from UtilityDeleteInformation import DeleteInformation

# Logging Settings
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# Working Dir Settings
current_dir = os.getcwd()

# FastApi App Settings
app = FastAPI(**project_info.project_info())
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app_response_message = {
    500: {"model": OutputModelError}, # Internal Service Error Response Template
    405: {"model": OutputModelError}, # Method not Allowed Response Template
}

# Apps Start Log Information
log.info(f'''\n
[APP START] ********************************************************************
Loading model and starting server. Please wait until server has fully started
Started       : {datetime.datetime.now()}
Work Dir      : {current_dir}
********************************************************************************\n''')
# Main Route -----------------------------------------------------------------------------------------------------------------------------------------------------------------
@app.get(
    "/", 
    response_model=OutputModelMain, # Swagger for Main Output Template
    responses=app_response_message # Swagger for Error Template
)
async def main():
    response = OutputModelMain(
        status="ok",
        api="information-retrieval" # Api Identifier for Information Retriever
    )
    return response

# Upload File Route ----------------------------------------------------------------------------------------------------------------------------------------------------------
@app.post(
    "/upload",
    response_model=OutputModelUpload, # Swagger for Upload Output Template
    responses=app_response_message # Swagger for Error Template
)
async def upload_file(file: UploadFile = File(...)):
    # Create request_id for Trace Log E2E Process in Route
    request_id = str(uuid.uuid4()) 
    log.info(f"{datetime.datetime.now()}  \033[94m[U] Upload {request_id}:\033[0m {file.filename}")

    try:
        # Check if the uploaded file is a PDF
        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Invalid file type. Only PDF files are allowed.")

        # Define file location and customized uploaded file name
        UPLOAD_FOLDER = Path("uploaded_information_data")
        UPLOAD_FOLDER.mkdir(exist_ok=True)
        file_location = UPLOAD_FOLDER / f"{file.filename.rsplit('.', 1)[0]}_{uuid.uuid4()}.{file.filename.rsplit('.', 1)[-1]}"

        # Save the uploaded file to the defined folder
        with open(file_location, "wb") as buffer:
            buffer.write(await file.read())

        # Define response
        response = OutputModelUpload(
            status="SUCCESS",
            timestamp=time.time(),
            file_path=str(file_location)
        )
        
        log.info(f"{datetime.datetime.now()}  \033[94m[U] Upload {request_id}:\033[0m {repr(response)}")
        return response
    except Exception as e:
        # Error Handling Block: General Error Information
        log.error(f"{datetime.datetime.now()} \033[93m[E] Upload Error Exception {request_id}:\033[0m {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

# Insert Information Route ---------------------------------------------------------------------------------------------------------------------------------------------------
@app.post(
    "/insert",
    response_model=OutputModelInsert, # Swagger for Insert Output Template
    responses=app_response_message # Swagger for Error Template
)
async def insert_document(request_insert: InsertModel):
    # Create request_id for Trace Log E2E Process in Route
    request_id = str(uuid.uuid4()) 
    log.info(f"{datetime.datetime.now()}  \033[94m[I] Insert {request_id}:\033[0m {repr(request_insert.dict())}")

    try:
        # Check if collection exist or not
        db_engine = ManageVectorDB()
        if not db_engine.check_collection_exists(request_insert.collection_name):
            # If collection not exist then create collection
            collection_creation_status = db_engine.create_collection(request_insert.collection_name, request_insert.collection_index_type)
        
        # Push each file path to the Celery queue for processing
        task = insert_information_worker.delay(request_insert.dict())
        
        # Define response 
        response = OutputModelInsert(
            task_id=task.id,
            status=task.state,
            timestamp=time.time()
        )

        log.info(f"{datetime.datetime.now()}  \033[94m[I] Insert {request_id}:\033[0m {repr(response)}")
        return response
    except Exception as e:
        # Error Handling Block: General Error Information
        log.error(f"{datetime.datetime.now()} \033[93m[E] Insert Error Exception {request_id}:\033[0m {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

# Insert Information Status Route --------------------------------------------------------------------------------------------------------------------------------------------
@app.get(
    '/insert/status/{task_id}',
    response_model=OutputModelInsertStatus, # Swagger for Insert Status Output Template
    responses=app_response_message # Swagger for Error Template
)
async def insert_task_result(task_id: str):
    # Create request_id for Trace Log E2E Process in Route
    request_id = str(uuid.uuid4()) 
    log.info(f"{datetime.datetime.now()}  \033[94m[IS] Insert Status {request_id}:\033[0m {repr(task_id)}")

    try:
        # Define task id
        task = AsyncResult(task_id, app=insert_app)    

        if task.state != "SUCCESS":
            # Define response for in progress
            response = OutputModelInsertStatus(
                task_id=task.id,
                status=task.state,
                timestamp=time.time(),
                data=[]
            )
        else:
            # Define response for finished
            response = OutputModelInsertStatus(
                task_id=task.id,
                status=task.state,
                timestamp=time.time(),
                data=task.get()
            )

        log.info(f"{datetime.datetime.now()}  \033[94m[IS] Insert Status {request_id}:\033[0m {repr(response)}")
        return response
    except Exception as e:
        # Error Handling Block: General Error Information
        log.error(f"{datetime.datetime.now()} \033[93m[E] Insert Status Error Exception {request_id}:\033[0m {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

# Delete Information Route ---------------------------------------------------------------------------------------------------------------------------------------------------
@app.post(
    "/delete",
    response_model=OutputModelDelete, # Swagger for Delete Output Template
    responses=app_response_message # Swagger for Error Template
)
async def delete_document(request_delete: DeleteModel):
    # Create request_id for Trace Log E2E Process in Route
    request_id = str(uuid.uuid4()) 
    log.info(f"{datetime.datetime.now()}  \033[94m[D] Delete {request_id}:\033[0m {repr(request_delete.dict())}")
    try:
        # Delete information
        delete_engine = DeleteInformation()
        delete_result = await delete_engine.delete_information(**request_delete.dict())
        
        # Define response
        response = OutputModelDelete(
            delete_chunks=delete_result.delete_count,
            timestamp=time.time(),
        )

        log.info(f"{datetime.datetime.now()}  \033[94m[D] Delete {request_id}:\033[0m {repr(response)}")
        return response
    except Exception as e:
        # Error Handling Block: General Error Information
        log.error(f"{datetime.datetime.now()} \033[93m[E] Delete Error Exception {request_id}:\033[0m {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

# Search Information Route ---------------------------------------------------------------------------------------------------------------------------------------------------
@app.post("/search",
    response_model=OutputModelSearch, # Swagger for Delete Output Template
    responses=app_response_message # Swagger for Error Template
)
async def search_document(request_search: SearchModel):
    # Create request_id for Trace Log E2E Process in Route
    request_id = str(uuid.uuid4()) 
    log.info(f"{datetime.datetime.now()}  \033[94m[S] Search {request_id}:\033[0m {repr(request_search.dict())}")

    try:
        # Log start time to calculate execution time
        start_time = time.time()
        
        # Search
        search_engine = SearchInformation()
        search_result = await search_engine.search_information(**request_search.dict())
        
        # Formatting result
        format_result = await search_engine.format_search_results(search_result)
        
        # Log finish time to calculate execution time
        finish_time = time.time()
        
        # Define response
        response = OutputModelSearch(
            timestamp=time.time(),
            search_time=finish_time - start_time,
            data=format_result
        )
        
        log.info(f"{datetime.datetime.now()}  \033[94m[S] Search {request_id}:\033[0m {repr(response)}")
        return response
    except Exception as e:
        # Error Handling Block: General Error Information
        log.error(f"{datetime.datetime.now()} \033[93m[E] Search Error Exception {request_id}:\033[0m {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

# App Initialization ---------------------------------------------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":    
    log.info(f"{Path(__file__).stem}:app")
    uvicorn.run(f"{Path(__file__).stem}:app", port=2024, host="0.0.0.0")