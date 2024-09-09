FROM python:3.9-slim

WORKDIR /usr/src/app

RUN pip install --upgrade pip

COPY ./requirements.txt .

RUN pip install -r requirements.txt --no-cache-dir

COPY . .

CMD ["gunicorn", "--bind", "0.0.0.0:7000", "blogicum.wsgi"]
