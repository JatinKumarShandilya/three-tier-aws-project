FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir flask mysql-connector-python python-dotenv

EXPOSE 5000

CMD ["python", "app.py"]
