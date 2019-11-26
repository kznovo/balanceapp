FROM python:3.7-stretch
RUN mkdir /app
WORKDIR /app
COPY . /app
RUN /app/scripts/install
EXPOSE 8000
ENTRYPOINT [ "scripts/run" ]
