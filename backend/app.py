from fastapi import FastAPI
from pydantic import BaseModel, Base64Str
from redis import Redis


class PDFFile(BaseModel):
    name: str
    bytes: Base64Str


app = FastAPI()
redis = Redis()


@app.post('/upload')
def index(file: PDFFile):
    # task_id = compute_embeddings(file_name, file_b64)
    return dict(file_name=file.name)

# @app.route('/status/<task_id>')
# def status(task_id):
#     '''requests the status of document processing'''
#     return dict(status=task_completed(task_id))

# @app.route('/query', methods=['POST'])
# def query():
#     task_id:str = request.json['taskId'] #type: ignore
#     query:str = request.json['query'] #type: ignore
#     matches = best_matches(task_id, query, 5)
#     return dict(matches=matches)
