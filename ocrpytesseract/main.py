from fastapi import FastAPI, Request, File, UploadFile, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import io
import cv2
import pytesseract
import numpy as np
import requests
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

class ImageType(BaseModel):
    url: str

def getLang(x):
    pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
    #pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
    x = pytesseract.image_to_string(x)
    return x

@app.get("/")
def main(request: Request):
    return templates.TemplateResponse('index.html', context={'request': request})

@app.post("/")
async def readFile(request: Request, image_upload: UploadFile = File(...)):
    # file upload
    data = await image_upload.read()
    filename = image_upload.filename

    with open(filename, 'wb') as f:
        f.write(data)

    # template
    FILE_PATH = 'https://i.ibb.co/LhCrxqH/Query.png'
    response = requests.get(FILE_PATH)
    template_filename = 'static/template.jpg'

    with open(template_filename, 'wb') as f:
        f.write(response.content)

    ###
    per = 25
    pixelThreshold = 500

    roi = [[(98, 984), (680, 1074), 'text', 'Name'],
           [(740, 980), (1320, 1078), 'text', 'Phone'],
           [(100, 1418), (686, 1518), 'text', 'Email'],
           [(740, 1416), (1318, 1512), 'text', 'ID'],
           [(110, 1598), (676, 1680), 'text', 'City'],
           [(748, 1592), (1328, 1686), 'text', 'Country']]

    orb = cv2.ORB_create(10000)

    #template
    imgQ = cv2.imread(template_filename)
    h, w, c = imgQ.shape
    orb = cv2.ORB_create(1000)
    kp1, des1 = orb.detectAndCompute(imgQ, None)

    #file upload
    img = cv2.imread(filename)
    kp2, des2 = orb.detectAndCompute(img, None)

    #compare
    bf = cv2.BFMatcher(cv2.NORM_HAMMING)
    matches = bf.match(des2, des1)
    matches.sort(key=lambda x: x.distance)
    good = matches[:int(len(matches) * (per / 100))]

    srcPoints = np.float32([kp2[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
    dstPoints = np.float32([kp1[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)

    srcPoints = np.float32([kp2[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
    dstPoints = np.float32([kp1[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)

    M, _ = cv2.findHomography(srcPoints, dstPoints, cv2.RANSAC, 5.0)
    imgScan = cv2.warpPerspective(img, M, (w, h))

    myData = dict()

    for x, r in enumerate(roi):
        imgCrop = imgScan[r[0][1]:r[1][1], r[0][0]:r[1][0]]

        if r[2] == 'text':
            x = getLang(imgCrop)
            myData[r[3]] = x.replace('\n\f','')

    return myData

if __name__ == '__main__':
    uvicorn.run(app, debug=True)