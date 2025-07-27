FROM python:3.13-slim

WORKDIR /app

# We do not bake the .env into the image, for it is bad practice.

COPY ./src/. /app/src
COPY ./requirements.txt /app

RUN pip install -r ./requirements.txt

EXPOSE 4000

CMD python -m src.main
