FROM python:3.12-slim

WORKDIR /code

COPY app/requirements.txt ./app/requirements.txt
RUN pip install --no-cache-dir -r app/requirements.txt

COPY app/ ./app/
COPY frontend/ ./frontend/

EXPOSE 5000

CMD gunicorn --bind 0.0.0.0:$PORT --workers 2 app.app:application