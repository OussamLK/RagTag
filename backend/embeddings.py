import openai
import nltk
from typing import Literal, TypedDict
from redis import Redis
redis = Redis()
from hashlib import sha256
import json

class Embedding(TypedDict):
    sentence: str
    embedding:list[float]


EMBEDDING_MODEL = Literal['text-embedding-3-large', 'text-embedding-3-small']

def sentence_embeddings(text:str, model:EMBEDDING_MODEL, cache=False)->list[Embedding]:
    sha = sha256((text+model).encode('utf-8')).digest()
    if cache:
        if res := redis.get(sha):
            return json.loads(res.decode('utf-8')) #type: ignore
    sentences = nltk.sent_tokenize(text)
    data = openai.embeddings.create(input=sentences, model=model).data
    embedding_vectors: map[list[float]] = map(lambda datum: datum.embedding, data)
    embeddings = [Embedding(sentence=sentence, embedding=embedding) for sentence, embedding in zip(sentences, embedding_vectors)]
    redis.set(sha, json.dumps(embeddings).encode('utf-8'))
    return embeddings