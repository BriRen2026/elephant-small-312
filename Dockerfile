FROM python:3.8
ENV FLASK_APP app.py
WORKDIR /root
COPY . .
# RUN apt update
# RUN apt install python3-pip -y
RUN pip3 install -r requirements.txt
RUN pip3 install Flask

EXPOSE 8080

ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.2.1/wait /wait
RUN chmod +x /wait
CMD /wait && python3 -u app.py