FROM python:3.11-slim

ENV PYTHONUNBUFFERED True
RUN apt update && apt install tzdata -y
ENV TZ="America/Sao_Paulo"

ENV GCP_SERVICE_ACCOUNT="a"

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY main.py /

CMD ["python", "main.py"]