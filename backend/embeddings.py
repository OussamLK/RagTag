import openai
import nltk
nltk.download('punkt_tab')
from typing import Literal, TypedDict
from redis import Redis
redis = Redis()
from hashlib import sha256
import json
from dotenv import load_dotenv
import spacy
load_dotenv()
import logging
logging.basicConfig(level=logging.INFO)
import time

def sentensizer(text):
    model = spacy.load("fr_core_news_lg")
    return map(lambda sent: sent.text, model(text).sents) 

class Embedding(TypedDict):
    sentence: str
    embedding:list[float]


EMBEDDING_MODEL = Literal['text-embedding-3-large', 'text-embedding-3-small']

def sentence_embeddings(text:str, model:EMBEDDING_MODEL, cache=False, sentensizer=None)->list[Embedding]:
    sha = sha256((text+model).encode('utf-8')).digest()
    if cache:
        if res := redis.get(sha):
            return json.loads(res.decode('utf-8')) #type: ignore
    if sentensizer:
        logging.info("Sentensizing the text using Spacy")
        start = time.time()
        sentences = sentensizer(text)
        logging.info(f"Done sentensizing in {time.time()-start:.2f}s")
    else:
        logging.info("Sentensizing nltk")
        sentences = nltk.sent_tokenize(text)
    data = openai.embeddings.create(input=sentences, model=model).data
    logging.info("API answered with embeddings...")
    embedding_vectors: map[list[float]] = map(lambda datum: datum.embedding, data)
    embeddings = [Embedding(sentence=sentence, embedding=embedding) for sentence, embedding in zip(sentences, embedding_vectors)]
    redis.set(sha, json.dumps(embeddings).encode('utf-8'))
    return embeddings