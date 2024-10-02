from typing import Callable, TypedDict, Iterable, Any
from pprint import pprint
import redis
import json

'''
The task of corresponding chunk to a list of words is not trivial due to the problems of separators.

Assumptions:
    1) all the chunks are all contained in the text, in the correct order.
        with the possible exception the first non-word charaters
        in the first chunk (useful in inductive steps).
    2) Every word from the ocr result is contained in some chunk.
    3) word order is preserved.
    4) Some words are empty words (happens in formulas and some other edge cases)

Observation:
   This implies that
      A) the first word of the ocr result will be the first word in the first chunk.
      B) Consuming a word from the results and removing it from the first chunk keep
         the property (A) correct.
    '''

redis = redis.Redis()

class Word[T](TypedDict):
    text:str
    metadata: T

def get_chunks_metadata(chunks:Iterable[str], words:Iterable[Word]):
    chunks = (chunk for chunk in chunks)
    words = (word for word in words)
    chunks_words:list[list[Word]] = []
    chunk_words:list[Word] = []
    try:
        chunk = next(chunks)
        word = next(words)
        while True:
            while len(word) < len(chunk):
                wp = chunk.find(word['text'])
                if wp < 0:
                    raise Exception(f"I can not find word: '{word}' in chunk:'{chunk}'")
                chunk = chunk[wp+len(word['text']):]
                chunk_words.append(word)
                word = next(words)
            chunks_words.append(chunk_words)
            chunk_words = []
            chunk = next(chunks)
            
    except StopIteration:
        return chunks_words

source = '''These datasets are used in machine learning (ML) research and have been cited in peer-reviewed academic journals. Datasets are an integral part of the field of machine learning. Major advances in this field can result from advances in learning algorithms (such as deep learning), computer hardware, and, less-intuitively, the availability of high-quality training datasets. High-quality labeled training datasets for supervised and semi-supervised machine learning algorithms are usually difficult and expensive to produce because of the large amount of time needed to label the data. Although they do not need to be labeled, high-quality datasets for unsupervised learning can also be difficult and costly to produce.

Many organizations, including governments, publish and share their datasets. The datasets are classified, based on the licenses, as Open data and Non-Open data.

The datasets from various governmental-bodies are presented in List of open government data sites. The datasets are ported on open data portals. They are made available for searching, depositing and accessing through interfaces like Open API. The datasets are made available as various sorted types and subtypes.'''

import nltk
chunks = nltk.sent_tokenize(source)

word_list = (Word(text=text, metadata=f"position {i}") for i, text in enumerate(source.split()))
    
if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'CHUNK':
        pprint(chunks)
        words = get_chunks_metadata(chunks, word_list)
        print(" ".join(word['text'] for chunk in words for word in chunk))
    else:
        import nltk
        from ocr import get_text, get_result
        import pickle
        import io
        key = b'result yeti 10 40'
        with open('yeti.pdf', 'rb') as f:
            if rw:=redis.get(key):
                with io.BytesIO() as f:
                    data:bytes = redis.get(key) #type: ignore
                    f.write(data)
                    f.seek(0)
                    result = pickle.load(f)
            else:
                file = f.read()
                result = get_result(file, 10, 40, cache=True)
                with io.BytesIO() as f:
                    pickle.dump(result, f)
                    f.seek(0)
                    data = f.read()
                    redis.set(key, data)
            chunks = nltk.sent_tokenize(result.render(), language='french')
            text = result.render()
            separators = []
            for chunk in chunks:
                pos = text.find(chunk)
                separators.append(text[:pos])
                text = text[pos+len(chunk):]
            multi_blocks = [len(page.blocks) for page in result.pages if len(page.blocks) > 1] 
            print(multi_blocks)
                
