FROM python:3.13-alpine

WORKDIR /app

COPY ../Web/Flask/requirements.txt /app/web-requirements.txt

COPY ../Database/requirements.txt /app/data-requirements.txt

RUN pip install -r /app/web-requirements.txt \
    && pip install -r /app/data-requirements.txt

COPY . /app/

EXPOSE 8000

CMD ["python", "Database/sqlalchemy/main.py"] 