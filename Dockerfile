FROM python:3.11-slim

WORKDIR /app

COPY . .
#какое то изменение
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Это нужно, чтобы Cloud Run пересобрал образ (можно оставить)
RUN echo "rebuild"

CMD ["python", "main.py"]
