FROM python:3.12.9-alpine3.21

WORKDIR /app

COPY . /app
#ENV GOOGLE_APPLICATION_CREDENTIALS="/app/application_default_credentials.json"
ENV GCLOUD_PROJECT="certain-haiku-443118-n2"
RUN pip install -r requirements.txt

ENTRYPOINT ["python", "main.py"]