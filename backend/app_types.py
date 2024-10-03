from typing import TypedDict, Iterable
from PIL.Image import Image
import numpy as np

class Embedding(TypedDict):
    chunk_id:int
    sentence: str
    context: str
    vector: np.ndarray[int, np.dtype[np.float64]]

class Overlay(TypedDict):
    chunk_id:int
    page_numbers: list[int]
    overlayed_pages: list[Image]

class OCRWord(TypedDict):
    text: str
    page: int
    geometry: tuple[tuple[float, float], tuple[float, float]]

class Chunk(TypedDict):
    text:str
    context: str
    words: list[OCRWord]

class SearchResult(TypedDict):
    chunk_id:int
    sentence: str
    context: str
    page_numbers: list[int]
    overlayed_pages: list[Image]

