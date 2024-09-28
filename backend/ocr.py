import time
import sys
from redis import Redis
from hashlib import sha256
import json
import pdf2image
redis = Redis()
from io import BytesIO
import torch
import logging
logging.basicConfig(level=logging.INFO)
import cv2
import numpy as np
from overlay import highlight_boxes


def sha_segment(file:bytes, first_page, last_page):
    signature = f"{file}, pages {first_page}-{last_page}"
    return sha256(signature.encode('utf-8')).digest()

def get_result(file:bytes,first_page=None, last_page=None, cache=False):
    from doctr.io import DocumentFile
    from doctr.models import ocr_predictor
    model = ocr_predictor(det_arch='db_resnet50', reco_arch='crnn_mobilenet_v3_large', pretrained=True)
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
    first_page = first_page or 0
    last_page = last_page or len(doc)
    fragment = doc[first_page-1:last_page]
    logging.info(f"converting {len(fragment)} pages...")
    result = model(fragment)
    return result

def get_text(file:bytes,first_page=None, last_page=None, cache=False):
    hash = sha_segment(file, first_page, last_page)
    if cache:
            if res := redis.get(hash):
                logging.info(f"Retrieving the text from Redis cache")
                return res.decode('utf-8') #type: ignore
    result = get_result(file, first_page=first_page, last_page=last_page, cache=cache)
    result_str:str = result.render()
    redis.set(hash, result_str.encode('utf-8'))
    return result_str

def main():
   path = input("Enter file path: ")
   first_page_input = input("Enter first page or leave it blank: ")
   last_page_input = input("Enter last page or leave it blank: ")
   first_page = int(first_page_input) if first_page_input else None
   last_page = int(last_page_input) if last_page_input else None
   with open(path, 'rb') as f:
       file = f.read()
   start = time.time()
   text = get_text(file, first_page=first_page, last_page=last_page, cache=False)
   print(text, end='\n\n')
   print(f"parsed in {time.time()-start}")

if __name__ == '__main__':
    #test: python3 orc file_path.pdf
    if len(sys.argv) > 1 and sys.argv[1] == 'TEST':
        with open('AO.pdf', 'br') as f:
            fb = f.read()
        result = get_result(fb, 5, 10)
        page1 = result.pages[0].page
        boxes= [word.geometry for line in result.pages[0].blocks[0].lines[:10] for word in line.words]
        from pprint import pprint
        pprint(boxes)
        from doctr.io import DocumentFile
        overlayed = highlight_boxes(page1, boxes)
        overlayed.show()

    else:
        main()