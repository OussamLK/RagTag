from app_types import OCRWord, Chunk
import os
from typing import Callable, TypedDict, Iterable, Any
from pprint import pprint
import redis
import logging

'''
The task of corresponding chunk to a list of words is not trivial due to the problems of separators.

Assumptions:
    1) all the chunks are all contained in the text, in the correct order.
        with the possible exception the first non-word charaters
        in the first chunk (useful in inductive steps).
    2) Every word from the ocr result is contained in some chunk exception for possibly trailing non-alnum characters.
    3) word order is preserved.
    4) Some words are empty words (happens in formulas and some other edge cases)

Observation:
   This implies that
      A) the first word of the ocr result will be the first word in the first chunk.
      B) Consuming a word from the results and removing it from the first chunk keep
         the property (A) correct.
    '''

redis = redis.Redis()
LANGUAGE = os.environ['LANGUAGE']
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)
file_handler = logging.FileHandler('chunk_geometry.log', mode='w')
file_handler.setLevel(logging.WARNING)
logger.addHandler(file_handler)

debug_logger = logging.getLogger(f"{__name__}.debug_logger")
debug_logger.setLevel(logging.DEBUG)
debug_formatter = logging.Formatter("%(name)s:%(levelname)s:%(message)s\n")
file_handler_debug = logging.FileHandler('chunk_geometry_debug.log', mode='w')
file_handler_debug.setLevel(logging.DEBUG)
file_handler_debug.setFormatter(debug_formatter)
debug_logger.addHandler(file_handler_debug)
debug_logger.debug("initialized...")


def get_chunks_geometry(chunk_texts: Iterable[str], words: Iterable[OCRWord]) -> list[list[OCRWord]]:
    debug_logger.debug(f"words are {[word['text'] for word in words]}")
    chunk_texts = iter(chunk_texts)
    words = iter(words)
    chunks_words: list[list[OCRWord]] = []
    chunk_words: list[OCRWord] = []
    try:
        chunk = next(chunk_texts)
        word = next(words)
        while True:
            while len(word) < len(chunk):
                wp = chunk.find(word['text'])
                i = len(word['text'])
                if wp < 0:
                    if word['text'][-1].isalnum():
                        logger.warning(f"I can not find word: '{
                            word['text']}' in chunk:'{chunk}'")
                        word = next(words)
                        continue
                    # the last letter is probably some seperator
                    while not word['text'][i-1].isalnum() and i > 0:
                        i -= 1
                    if i == 0:
                        logger.warning(f"I can not find word: '{
                            word['text']}' in chunk:'{chunk}' removed all all non alnum characters")
                        word = next(words)
                        continue
                    wp = chunk.find(word['text'][:i])
                    if wp < 0:
                        logger.warning(f"I can not find word: '{
                            word['text']}' in chunk:'{chunk}' checked {word['text'][:i]}")
                        word = next(words)
                        continue
                offset = wp+len(word['text'][:i])
                debug_logger.debug(f"updating the chunk\nfrom '{chunk}'\nto '{
                    chunk[offset:]}' after seeing word\n'{word['text'][:i]}'\n")
                chunk = chunk[offset:]
                chunk_words.append(word)
                word = next(words)
            chunks_words.append(chunk_words)
            chunk_words = []
            chunk = next(chunk_texts)

    except StopIteration:
        return chunks_words


if __name__ == '__main__':
    import nltk
    from ocr import capture
    with open('AO.pdf', 'rb') as f:
        fb = f.read()
        text, words = capture(fb, 20, 30)
        chunks = nltk.sent_tokenize(text)
        chunks_metadata = get_chunks_geometry(chunks, words)
