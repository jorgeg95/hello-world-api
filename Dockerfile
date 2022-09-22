FROM python:3.9-alpine

WORKDIR /app

RUN apk update

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . /app

EXPOSE 8080

CMD [ "python3", "revolut_code_challenge_server.py" ]


