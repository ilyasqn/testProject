FROM python:3.12-slim

WORKDIR /app

COPY shared /shared
RUN pip install -e /shared

COPY services/product_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY services/product_service/ .

CMD ["python", "run.py"]
