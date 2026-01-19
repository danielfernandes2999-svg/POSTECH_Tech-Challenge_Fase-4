FROM python:3.9-slim
WORKDIR /app
COPY streamlit/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY streamlit/ .

EXPOSE 8501
CMD ["streamlit", "run", "app_Tech4.py", "--server.port=8501", "--server.address=0.0.0.0"]


