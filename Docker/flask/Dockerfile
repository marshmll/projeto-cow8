FROM python:3.13-alpine

WORKDIR /app

COPY ./Web/Flask/requirements.txt /app/all-requirements.txt

RUN python -m pip install -r /app/all-requirements.txt

COPY ./Web/Flask /app/Web/Flask

WORKDIR /app/Web/Flask

EXPOSE 8000

CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=8000", "--debug"]