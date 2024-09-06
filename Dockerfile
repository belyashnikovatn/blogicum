FROM python:3.9-slim

RUN pip install --upgrade pip

COPY requirements.txt .

RUN pip install -r requirements.txt --no-cache-dir

COPY . /app
WORKDIR /app

ENTRYPOINT [ "sh", "entrypoint.sh" ]