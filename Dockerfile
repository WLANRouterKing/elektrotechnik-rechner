FROM tiangolo/meinheld-gunicorn-flask:python3.7

COPY . /app

WORKDIR /app

RUN pip install wheel

RUN pip install -r requirements.txt

RUN ls -a
