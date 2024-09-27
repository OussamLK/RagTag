import sys
from celery import Celery
import openai
import numpy as np
import ocr
import embeddings
from embeddings import Embedding
from pprint import pprint
from redis import Redis


celery_app = Celery(
    'rag',
    backend='redis://localhost',
    brocker='pyampq://gest@localhost'
)

celery_app.conf.task_track_started=True

# @celery_app.task
# def background_compute_embeddings(file_name, fileB64):
#     '''return a task id'''
#     file_bytes = base64.b64decode(fileB64)
#     images= pdf2image.convert_from_bytes(file_bytes)
#     page_strings = []
#     for image in tqdm(images):
#         string = pytesseract.image_to_string(image, lang='fra')
#         page_strings.append(string)
#     full_text = " ".join(page_strings)
#     sentences:list[str] = nltk.tokenize.sent_tokenize(full_text)
#     embedding_data = openai.embeddings.create(input=sentences, model='text-embedding-3-small').data
#     vector_embeddings:list[list[float]] = [e.embedding for e in embedding_data]
#     embeddings = [embeddings.Embedding(sentence=sentence, embedding=embedding) for sentence, embedding in zip(sentences, vector_embeddings)]
#     return embeddings
    
# def compute_embeddings(file_name, fileB64:str)->int:
#     res = background_compute_embeddings.delay(file_name, fileB64) #type:ignore
#     return res.id

def task_completed(task_id):
    state = celery_app.AsyncResult(task_id).state
    return state == "SUCCESS"
    
def cosine_similarity(embedding1, embedding2):
    return np.dot(embedding1, embedding2)/(np.linalg.norm(embedding1)*np.linalg.norm(embedding2))

def best_matches(embeddings:list[Embedding], query:str, model:embeddings.EMBEDDING_MODEL, nb_results=5):
    query_embedding = openai.embeddings.create(input=[query], model=model).data[0].embedding
    cosine_similaritie_scores = [dict(sentence=embedding['sentence'], score=cosine_similarity(query_embedding, embedding['embedding'])) for embedding in embeddings]
    return sorted(cosine_similaritie_scores, key=lambda css: css['score'], reverse=True)[:nb_results]

def main():
    path = sys.argv[1]
    first_page = int(sys.argv[2])
    last_page = int(sys.argv[3])
    query = sys.argv[4]
    with open(path, 'rb') as f:
        file = f.read()
    text = ocr.get_text(file, first_page=first_page, last_page=last_page, cache=True)
    model:embeddings.EMBEDDING_MODEL = 'text-embedding-3-large'
    sentence_embeddings = embeddings.sentence_embeddings(text, model, cache=True)
    matches = best_matches(sentence_embeddings, query, model)
    for match in matches:
        print(f"************score: {match['score']}")
        print(match['sentence'])
        print("\n***************************")

if __name__ == '__main__':
    main()
