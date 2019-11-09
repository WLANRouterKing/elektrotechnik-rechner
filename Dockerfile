FROM tiangolo/meinheld-gunicorn-flask:python3.7

COPY . /app

WORKDIR /app

RUN pip install -r requirements.txt

ENTRYPOINT [ "python" ]

RUN ls -a

CMD [ "main.py" ]