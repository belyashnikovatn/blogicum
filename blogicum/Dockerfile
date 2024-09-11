FROM python:3.9-slim

RUN mkdir -p /home/app
RUN addgroup --system app && adduser --system --group app

ENV HOME=/home/app
ENV APP_HOME=/home/app/blogicum
RUN mkdir $APP_HOME
RUN mkdir $APP_HOME/staticfiles
WORKDIR $APP_HOME

RUN pip install --upgrade pip

COPY ./requirements.txt .

RUN pip install -r requirements.txt --no-cache-dir

COPY . ${APP_HOME}
RUN chown -R app:app $APP_HOME


CMD ["gunicorn", "--bind", "0.0.0.0:7000", "blogicum.wsgi"]
