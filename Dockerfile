FROM python:3.13-slim
WORKDIR /app
COPY pyproject.toml README.md ./
RUN pip install --no-cache-dir fastapi[standard] pytest httpx
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
