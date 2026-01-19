FROM python:3.9-slim
WORKDIR /app

COPY api/requirements.txt . 
RUN pip install -r requirements.txt

COPY api/ .
COPY modelo/ ./modelo/
COPY Dados/ ./Dados/

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app_Tech4:app"]
