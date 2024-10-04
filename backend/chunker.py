import spacy
from app_types import Chunck, OCRWord
from typing import Iterable
from chunk_geometry import get_chunks_geometry


def chunck_filter(chunck: str) -> bool:
    return len(chunck) > 5


def get_context(chuncks, index):
    start = index
    end = index+1
    while len(' '.join(chuncks[start:end])) < 50 and not (start == 0 and end == len(chuncks)):
        start = max(0, start-1)
        end = min(len(chuncks), end+1)
    context = ' '.join(chuncks[start:end])
    return context


def get_chuncks(text: str, words: list[OCRWord]) -> Iterable[Chunck]:
    model = spacy.load('fr_core_news_lg')
    chuncks = [chunk.text for chunk in model(text).sents]

    contexts = (get_context(chuncks, i) for i, _ in enumerate(chuncks))
    chunks_geometry = get_chunks_geometry(chuncks, words)
    return [Chunck(id=i, text=chunck_text, context=context, words=chunk_gemetry) for i, (chunck_text, context, chunk_gemetry) in enumerate(zip(chuncks, contexts, chunks_geometry)) if chunck_filter(chunck_text)]
