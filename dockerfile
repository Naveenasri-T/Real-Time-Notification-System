FROM python:3.10-slim

WORKDIR /app

# Copy app package into /app/app so `import app` resolves correctly
COPY ./app /app/app
COPY ./app/requirements.txt /app/

RUN pip install --no-cache-dir -r /app/requirements.txt

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
FROM python:3.10-slim

WORKDIR /app
COPY ./app /app/app
COPY ./app/requirements.txt /app/

RUN pip install --no-cache-dir -r /app/requirements.txt

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
