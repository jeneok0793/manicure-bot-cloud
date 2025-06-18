FROM python:3.11-slim

WORKDIR /app

COPY . .

# DEBUG: выводим структуру файлов и содержимое requirements.txt
RUN echo "📁 Содержимое /app:" && ls -la /app && \
    echo "📄 Содержимое requirements.txt:" && cat /app/requirements.txt

# DEBUG: пробуем найти pytz в requirements.txt
RUN grep pytz /app/requirements.txt || echo "❌ pytz не найден в requirements.txt"

# Установка системных зависимостей (иногда pytz требует gcc)
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

# Установка Python-зависимостей
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt

# Финальный запуск
CMD ["python3", "main.py"]
