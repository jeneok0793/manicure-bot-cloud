FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 👇 Покажет, что находится в папке /app — чтобы убедиться, что main.py реально там
RUN ls -la /app

EXPOSE 8080

CMD ["python", "main.py"]
