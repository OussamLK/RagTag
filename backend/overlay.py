import logging
from PIL import Image, ImageDraw
logging.basicConfig(level=logging.DEBUG)
from doctr.io import DocumentFile
import numpy as np

type UpperLeft = tuple[float, float]
type LowerRight = tuple[float, float]
type WordGeometry = tuple[UpperLeft, LowerRight] # values are in [0,1]

type ImageMatrix = np.ndarray[tuple[int, ...], np.dtype[np.uint8]]

def highlight_boxes(image_matrix:ImageMatrix, boxes:list[WordGeometry]):
    im = Image.fromarray(image_matrix).convert('RGBA')
    overlay = Image.new("RGBA", im.size, (255, 255, 255, 0))
    drawing = ImageDraw.Draw(overlay)
    for box in boxes:
        box = np.array(box)
        size = np.array(im.size)
        pil_box:list = (box*size).astype(int).tolist()
        logging.debug(f"pil_box is now {pil_box}, from image size {im.size} and box {box}")    
        pil_tuples = map(lambda point: tuple(point), pil_box)
        drawing.rectangle(list(pil_tuples), fill=(255, 255, 0, 100))
    out = Image.alpha_composite(im, overlay)
    return out


if __name__ == '__main__':
    doc = DocumentFile.from_pdf('AO.pdf')[5]
    # split the image into individual bands
    out = highlight_boxes(doc, [((0.66, .073), (.88,.09))])
    out.show()