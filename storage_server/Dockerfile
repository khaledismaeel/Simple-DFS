FROM python:3

ADD storage_server.py /
ADD requirements.txt /

RUN pip install -r requirements.txt

EXPOSE 8800

CMD ["python", "-u", "./storage_server.py"]