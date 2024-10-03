import spacy
from app_types import Chunk, OCRWord
from typing import Iterable
from chunk_geometry import get_chunks_geometry

def get_chunck_context(text:str, words:list[OCRWord])->Iterable[Chunk]:
    model = spacy.load('fr_core_news_lg')
    chunks = [chunk.text for chunk in model(text).sents]
    def get_context(index):
        start = index
        end = index+1
        while len(' '.join(chunks[index+start:index+end])) < 100 and not (start == 0 and end == len(chunks)):
            start = max(0, start-1)
            end = min(len(chunks), end+1)
        context = ' '.join(chunks[start:end])
        return context
    contexts = (get_context(i) for i, _ in enumerate(chunks))
    chunks_geometry = get_chunks_geometry(chunks, words)
    return [Chunk(text = chunk, context=context, words=chunk_gemetry) for chunk, context, chunk_gemetry in zip(chunks, contexts, chunks_geometry)]
    
