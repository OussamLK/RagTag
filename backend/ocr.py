import time
import sys
from redis import Redis
from hashlib import sha256
import json
import pdf2image
redis = Redis()
from io import BytesIO
import torch

def hash_digest(bytes:bytes):
    return sha256(bytes).digest()

def sha_segment(file:bytes, first_page, last_page):
    signature = f"{file}, pages {first_page}-{last_page}"
    return hash_digest(signature.encode('utf-8'))

def pdf_to_page_image_bytes(file:bytes, first_page=None, last_page=None):
    images = pdf2image.convert_from_bytes(file, first_page= first_page or 0) if not last_page else pdf2image.convert_from_bytes(file, first_page=first_page or 0, last_page=last_page)
    images_bytes = []
    with BytesIO() as byteIO:
        for image in images:
            image.save(byteIO, format='PNG')
            byteIO.seek(0)
            images_bytes.append(byteIO.read())
            byteIO.seek(0)
            byteIO.truncate()
    return images_bytes

def get_text(file:bytes,first_page=None, last_page=None, cache=False):
    hash = sha_segment(file, first_page, last_page)
    if cache:
            if res := redis.get(hash):
                print(f"Retrieving the text from cache")
                return json.loads(res.decode('utf-8')) #type: ignore
    images = pdf_to_page_image_bytes(file, first_page, last_page)
    from doctr.io import DocumentFile
    from doctr.models import ocr_predictor
    print(f"Converting {len(images)} pages")
    doc = DocumentFile.from_images(images)
    model = ocr_predictor(det_arch='fast_base', reco_arch='crnn_mobilenet_v3_large', pretrained=True)
    if torch.cuda.is_available():
        device = torch.device('cuda')
    elif torch.backends.mps.is_available():
        device = torch.device('mps')
    else:
        device = torch.device('cpu')
    model.to(device)
    result = model(doc)
    result_json = result.export()
    pages = result_json['pages']
    blocks = (block for page in pages for block in page['blocks'])
    lines = []
    for block in blocks:
        for line in block['lines']:
            lines.append(line)
        #lines.append({"words":[{"value": '.'}]}) 
    def get_words(line): return map(lambda word: word['value'], line['words']) 
    lines_str = [" ".join(get_words(line)) for line in lines]
    res = " ".join(lines_str)
    redis.set(hash, json.dumps(res).encode('utf-8'))
    return res

def main():
   path = sys.argv[1] 
   first_page = int(sys.argv[2]) if len(sys.argv) >= 4 else None
   last_page = int(sys.argv[3]) if len(sys.argv) >= 4 else None
   with open(path, 'rb') as f:
       file = f.read()
   start = time.time()
   text = get_text(file, first_page=first_page, last_page=last_page, cache=False)
   print(text, end='\n\n')
   print(f"parsed in {time.time()-start}")

if __name__ == '__main__':
    #test: python3 orc file_path.pdf
    main()