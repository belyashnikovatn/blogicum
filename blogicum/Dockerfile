FROM python:3.9-slim


COPY requirements.txt .

RUN pip install -r requirements.txt --no-cache-dir

COPY . /app
WORKDIR /app

CMD [ "gunicorn", "bind", "0.0.0.0:8080", "blogicum.wsgi" ]