from app_types import OCRWord
from typing import TypedDict
from overlay import highlight_boxes
import logging
import time
import sys
from redis import Redis
from hashlib import sha256
redis = Redis()
logging.basicConfig(level=logging.INFO)


def capture(file: bytes, first_page: int, last_page: int, cache=False) -> tuple[str, list[OCRWord]]:
    '''Performs ocr on a pdf file given in bytes,
    returns full text and list of word geometry'''

    result = _get_result(file, first_page=first_page,
                         last_page=last_page, cache=cache)
    words: list[OCRWord] = [OCRWord(text=word.render(), geometry=word.geometry, page=page_index+first_page)
                            # type: ignore
                            for page_index, page in enumerate(result.pages)
                            for block in page.blocks
                            for line in block.lines
                            for word in line.words]
    # Using this instead of result.render() to make it much easier to retrieve words from chucks
    # It also makes more sense to have a space instead of a new paragraph when a sentence is split
    # At the end of a page
    full_text = " ".join(word['text'] for word in words)
    return full_text, words


def _get_result(file: bytes, first_page=None, last_page=None, cache=False):
    from doctr.io import DocumentFile
    from doctr.models import ocr_predictor
    import torch
    model = ocr_predictor(det_arch='db_resnet50', pretrained=True)
    if torch.cuda.is_available():
        logging.info("Using CUDA")
        device = torch.device('cuda')
    elif torch.backends.mps.is_available():
        logging.info("Using MPS - Apple Silicon")
        device = torch.device('mps')
    else:
        logging.info("Not using acceleration, using CPU")
        device = torch.device('cpu')
    model.to(device)
    doc = DocumentFile.from_pdf(file)
    first_page = first_page or 1
    last_page = last_page or len(doc)+1
    fragment = doc[first_page-1:last_page]
    logging.info(f"converting {len(fragment)} pages...")
    result = model(fragment)
    return result


def _sha_segment(file: bytes, first_page, last_page):
    signature = f"{file}, pages {first_page}-{last_page}"
    return sha256(signature.encode('utf-8')).digest()


if __name__ == '__main__':
    # test: python3 orc file_path.pdf
    from pprint import pprint
    with open('AO.pdf', 'br') as f:
        fb = f.read()
    result = capture(fb, 22, 22)
    pprint(result)
