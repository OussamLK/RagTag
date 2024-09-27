from flask import Flask, request
from redis import Redis


app = Flask(__name__)

redis = Redis()

@app.route('/upload', methods=['POST'])
def index():
    file_b64 = request.json['fileB64'] #type: ignore
    file_name:str = request.json['fileName'] #type:ignore
    #task_id = compute_embeddings(file_name, file_b64)
    return dict(fileId = file_name)

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