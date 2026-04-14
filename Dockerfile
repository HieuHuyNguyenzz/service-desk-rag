FROM python:3.10-slim

WORKDIR /app

ARG HTTP_PROXY
ARG HTTPS_PROXY

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
