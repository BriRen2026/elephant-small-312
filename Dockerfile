FROM python:3.8
RUN apt update
RUN apt install python3-pip -y
RUN pip3 install Flask

WORKDIR /root

COPY . .

ENV FLASK_APP app.py
EXPOSE 8080

CMD ["python3","-m","flask","run","--host=0.0.0.0", "--port=8080"]