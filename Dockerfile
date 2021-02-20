FROM python:3.9 as base
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update -y
RUN apt install libgl1-mesa-glx -y 
RUN apt-get install libleptonica-dev -y 
RUN apt-get install tesseract-ocr -y
RUN apt-get install libtesseract-dev -y
RUN apt-get install 'ffmpeg'\
    'libsm6'\
    'libxext6'  -y
WORKDIR /home/ocrpytesseract

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip && pip install -r requirements.txt


# development image.
FROM base as development

COPY requirements_dev.txt requirements_dev.txt

RUN pip install -r requirements_dev.txt


# testing image.
FROM base as testing

RUN pip install pytest && pip install requests


# production image.
FROM base as production

WORKDIR /production

COPY . .
COPY ocrpytesseract/static ./
COPY ocrpytesseract/templates ./

ARG PORT=80
ARG HOST=0.0.0.0
ARG APP_MODULE=ocrpytesseract.main:app
ARG WORKERS_PER_CORE=1

ENV MODE=production
ENV APP_MODULE=${APP_MODULE}
ENV WORKERS_PER_CORE=${WORKERS_PER_CORE}}
ENV HOST=${HOST}
ENV PORT=${PORT}

EXPOSE ${PORT}

ENTRYPOINT [ "./scripts/start.sh" ]
