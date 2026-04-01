FROM python:3.12.4

WORKDIR /

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade -r requirements.txt

ENV ASPNETCORE_FORWARDEDHEADERS_ENABLED=true
ENV FORWARDED_ALLOW_IPS="*"

COPY . .

EXPOSE 10000

# Run init_db.py first and then start the server
# CMD python init_db.py && gunicorn main:app \
CMD alembic upgrade head || echo "Migration skipped" && gunicorn main:app \
    --bind 0.0.0.0:$PORT \
    --worker-class uvicorn.workers.UvicornWorker \
    --workers 1 \
    --log-level info
