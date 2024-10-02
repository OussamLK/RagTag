from typing import Callable, TypedDict, Iterable, Any
from pprint import pprint
import redis

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

from ocr import OCRWord

def get_chunks_metadata(chunks:Iterable[str], words:Iterable[OCRWord])->list[list[OCRWord]]:
    chunks = (chunk for chunk in chunks)
    words = (word for word in words)
    chunks_words:list[list[OCRWord]] = []
    chunk_words:list[OCRWord] = []
    try:
        chunk = next(chunks)
        word = next(words)
        while True:
            while len(word) < len(chunk):
                wp = chunk.find(word['text'])
                if wp < 0:
                    if word['text'][-1].isalnum():
                        raise Exception(f"I can not find word: '{word['text']}' in chunk:'{chunk}'")
                    #the last letter is probably some seperator
                    i = len(word['text'])
                    while not word['text'][i-1].isalnum() and i > 0:
                        i-=1
                    if i == 0:
                        raise Exception(f"I can not find word: '{word['text']}' inside chunk {chunk} ")
                    wp = chunk.find(word['text'][:i])
                    if wp < 0:
                        raise Exception(f"I can not find word: '{word['text'][:i]}' inside chunk {chunk} ")

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

    
if __name__ == '__main__':
    import nltk
    from ocr import capture
    with open('AO.pdf', 'rb') as f:
        fb = f.read()
        text, words = capture(fb, 20, 20)
        chunks = nltk.sent_tokenize(text)
        chunks_metadata = get_chunks_metadata(chunks, words)
