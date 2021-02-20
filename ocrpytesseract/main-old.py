from fastapi import FastAPI
from ocrpytesseract.utils.settings import Settings


app = FastAPI()
settings = Settings()


@app.get("/")
async def root():
    return {"message": f"Hello World, {settings.mode}"}
