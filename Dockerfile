FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt --no-cache-dir

COPY . .

WORKDIR blogicum

CMD [ "gunicorn", "--bind", "0.0.0.0:7000", "blogicum.wsgi" ]