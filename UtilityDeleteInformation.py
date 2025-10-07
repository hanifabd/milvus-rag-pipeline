from ManageVectorDB import ManageVectorDB

class DeleteInformation:
    def __init__(self):
        self.name = "DeleteInformation"
    
    async def delete_information(self, client_id, project_id, collection_name, file_id):
        db_engine = ManageVectorDB()
        delete_result = db_engine.delete_in_collection(client_id, project_id, collection_name, file_id)
        return delete_result