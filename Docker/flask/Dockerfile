FROM python:3.13-alpine

WORKDIR /app

COPY ./Web/Flask/requirements.txt /app/web-requirements.txt

COPY ./Database/requirements.txt /app/data-requirements.txt

RUN pip install -r /app/web-requirements.txt \
    && pip install -r /app/data-requirements.txt

COPY ./Web/Flask /app/Web/Flask
COPY ./Database /app/Databas

WORKDIR /app/Web/Flask

EXPOSE 8000

CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=8000", "--debug"]