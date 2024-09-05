FROM python:3.10-slim

WORKDIR /backend

COPY . /backend

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

ENV FLASK_APP=server.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV PYTHONPATH='/'

CMD ["flask", "--app", "server", "run", "--port", "8000"]
