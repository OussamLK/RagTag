from app_types import Chunck, Embedding
import numpy as np
from doctr.io import DocumentFile
import logging
from PIL import Image, ImageDraw
logging.basicConfig(level=logging.DEBUG)


type UpperLeft = tuple[float, float]
type LowerRight = tuple[float, float]
type WordGeometry = tuple[UpperLeft, LowerRight]  # values are in [0,1]


type ImageMatrix = np.ndarray[tuple[int, ...], np.dtype[np.uint8]]


def highlight_boxes(image_matrix: ImageMatrix, boxes: list[WordGeometry]):
    im = Image.fromarray(image_matrix).convert('RGBA')
    overlay = Image.new("RGBA", im.size, (255, 255, 255, 0))
    drawing = ImageDraw.Draw(overlay)
    for box in boxes:
        box = np.array(box)
        size = np.array(im.size)
        pil_box: list = (box*size).astype(int).tolist()
        logging.debug(f"pil_box is now {pil_box}, from image size {
                      im.size} and box {box}")
        pil_tuples = map(lambda point: tuple(point), pil_box)
        drawing.rectangle(list(pil_tuples), fill=(255, 255, 0, 100))
    out = Image.alpha_composite(im, overlay)
    return out


def highlight_chunck(chunck: Chunck, document: list[ImageMatrix], document_start_page: int = 1):
    if len(chunck['words']) == 0:
        raise Exception(
            f"trying to highlight a chunck with no words, chunck id {chunck['id']}")
    word_per_pages = [[]]
    current_page = chunck_beginning = chunck['words'][0]['page']
    for word in chunck['words']:
        if current_page != word['page']:
            word_per_pages.append([])  # create a new page
        word_per_pages[-1].append(word)
    images = []
    for i, page in enumerate(word_per_pages):
        boxes = [word['geometry'] for word in page]
        page = document[i+chunck_beginning-document_start_page]
        images.append(highlight_boxes(page, boxes))
    return images


if __name__ == '__main__':
    doc = DocumentFile.from_pdf('AO.pdf')[5]
