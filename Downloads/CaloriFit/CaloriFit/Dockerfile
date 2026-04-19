FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
COPY app.py .
COPY templates/ ./templates/
COPY static/ ./static/

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=production

CMD ["flask", "run"]
