FROM python:3.6.9

#WORKDIR /storage_server
#COPY . /storage_server

ADD storage_server.py /

EXPOSE 8800

CMD ["python", "-u", "./storage_server.py"]