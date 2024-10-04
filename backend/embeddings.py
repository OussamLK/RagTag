import numpy as np
from app_types import Embedding
import time
import logging
import spacy
from dotenv import load_dotenv
import json
from hashlib import sha256
from redis import Redis
from typing import Literal, Iterable
import openai
from app_types import Chunck
import pickle
redis = Redis()
load_dotenv()
logging.basicConfig(level=logging.INFO)


def sentensizer(text):
    model = spacy.load("fr_core_news_lg")
    return map(lambda sent: sent.text, model(text).sents)


EMBEDDING_MODEL = Literal['text-embedding-3-large', 'text-embedding-3-small']


def sentence_embeddings(chuncks: Iterable[Chunck], model: EMBEDDING_MODEL, cache=False) -> list[Embedding]:
    sig = (" ".join(chunck['context']
           for chunck in chuncks)+'|'+model).encode('utf-8')
    sha = sha256(sig).digest()
    if cache:
        if res := redis.get(sha):
            return pickle.loads(res)  # type: ignore
    else:
        redis.delete(sha)
    contexts = [chunck['context'] for chunck in chuncks]
    data = openai.embeddings.create(input=contexts, model=model).data
    logging.info("API answered with embeddings...")
    embedding_vectors: np.ndarray[int, np.dtype[np.float64]] = np.array(list(map(
        lambda datum: datum.embedding, data)))

    embeddings = [Embedding(chunck_id=chunck['id'], sentence=chunck['text'], vector=embedding, context=chunck['context'])  # type: ignore
                  for chunck, embedding in zip(chuncks, embedding_vectors)]
    if cache:
        redis.set(sha, pickle.dumps(embeddings))
    return embeddings
