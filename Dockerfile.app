FROM python:3.12-slim

WORKDIR /code

COPY requirements.txt /code/

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app