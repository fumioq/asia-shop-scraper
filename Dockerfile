FROM python:3.11-slim
EXPOSE 8080

ENV PYTHONUNBUFFERED True

RUN apt update && apt install tzdata -y
ENV TZ "America/Sao_Paulo"

RUN install -d -m 0755 /etc/apt/keyrings
RUN apt-get update && apt-get install wget -y
RUN wget -q https://packages.mozilla.org/apt/repo-signing-key.gpg -O- | tee /etc/apt/keyrings/packages.mozilla.org.asc > /dev/null

RUN echo "deb [signed-by=/etc/apt/keyrings/packages.mozilla.org.asc] https://packages.mozilla.org/apt mozilla main" | tee -a /etc/apt/sources.list.d/mozilla.list > /dev/null
RUN apt-get update && apt-get install firefox -y

RUN ls /run/secrets
RUN cat /run/secrets/GCP_SERVICE_ACCOUNT > GCP_SERVICE_ACCOUNT.txt

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

CMD exec gunicorn --bind 0.0.0.0:8080 --workers 1 --threads 8 main:app
