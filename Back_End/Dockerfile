FROM python:3.11-slim

# In docker, "app" will be the root dir
WORKDIR /app

# Copy
COPY requirements.txt .

# Download all dependencies in requirements
RUN pip install --no-cache-dir -r requirements.txt

# Copy all files in Back_End Folder
COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
