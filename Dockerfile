FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./requirements.txt
RUN echo "===== requirements.txt =====" && cat requirements.txt
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Проверка наличия pytz и вывод содержимого директории
RUN echo "===== Содержимое /app =====" && ls -la /app
RUN python -c "import pytz; print('✅ pytz установлен и работает')"

CMD ["python", "main.py"]
