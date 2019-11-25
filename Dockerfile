FROM python:3.7-stretch
RUN mkdir /app
WORKDIR /app
COPY . /app
RUN apt-get update && apt-get install -y uuid-runtime
RUN /app/scripts/gen_secret
RUN /app/scripts/install
EXPOSE 8000
ENTRYPOINT [ "scripts/run" ]
