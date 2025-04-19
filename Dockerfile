FROM python:3.12.4

WORKDIR /

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade -r requirements.txt

ENV ASPNETCORE_FORWARDEDHEADERS_ENABLED=true
ENV FORWARDED_ALLOW_IPS="*"

COPY . .

EXPOSE 3100

# Ejecutamos primero init_db.py y luego lanzamos el servidor
CMD python init_db.py && gunicorn main:app \
    --bind 0.0.0.0:3100 \
    --worker-class uvicorn.workers.UvicornWorker \
    --log-level info
