import re
from app_types import OCRWord, Chunk
import os
from typing import Callable, TypedDict, Iterable, Any
from pprint import pprint
import redis
import logging

'''
The task of corresponding chunk to a list of words is not trivial due to the problems of separators.
The issue seems to be exlusively when a chunck splits a word in two.
ex: (Annexe) is split in `(` and `Annexe)`

This still has a problem with chuncks that do not include ending `.` while words do.
In this case, words are always included in the next chunck.

Assumptions:
    1) words do not have spaces in them.
    2) Chuncks from the concatenation of the ocr word list (" ".join(words))
    3) all the chunks are all contained in the text, in the correct order.
        with the possible exception the first non-word charaters
        in the first chunk (useful in inductive steps).
    4) Every word from the ocr result is contained in some chunk.
    5) word order is preserved.
    6) Some words are empty words (happens in formulas and some other edge cases)
    7) A chunck can start or end with a space

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


def common_prefix(s1: str, s2: str) -> str:
    substr = []
    i = 0
    while i < len(s1) and i < len(s2):
        if s1[i] != s2[i]:
            break
        substr.append(s1[i])
        i += 1
    return ''.join(substr)


def get_chunks_geometry(chuncks: Iterable[str], words: Iterable[OCRWord]) -> list[list[OCRWord]]:
    chuncks_words: list[list[OCRWord]] = []
    chunck_words: list[OCRWord] = []
    chuncks = list(chuncks)
    words = list(words)
    wi = 0  # word_index
    def wt(): return words[wi]['text']
    chunck_rest = ''
    for ci, chunck in enumerate(chuncks):
        debug_logger.debug(f"word is {wt()} while {wi=}")
        chunck = chunck_rest + chunck
        while wi < len(words):
            if len(wt()) > len(chunck):
                break
            wp = chunck.find(wt())
            if wp != 0:
                raise Exception(f"word '{wt()}' should be prefix of chunck '{
                                chuncks[ci]}' chunck is {ci=} and word is {wi=}")
            offset = wp+len(wt())
            debug_logger.debug(f"updating the chunk\nfrom '{chunck}'\nto '{
                chunck[offset:]}' after seeing word\n'{wt()}'\n")
            chunck = chunck[offset:].strip()
            chunck_words.append(words[wi])
            wi += 1
        chuncks_words.append(chunck_words)
        chunck_words = []
        chunck_rest = chunck
    return chuncks_words


if __name__ == '__main__':
    import nltk
    from ocr import capture
    with open('AO.pdf', 'rb') as f:
        fb = f.read()
        text, words = capture(fb, 20, 30)
        chunks = nltk.sent_tokenize(text)
        chunks_metadata = get_chunks_geometry(chunks, words)
