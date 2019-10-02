FROM python:3.7-alpine
LABEL maintainer="mail@wieland.tech"

WORKDIR /root

ADD requirements.txt /root/
RUN pip3 install -r requirements.txt
ADD kubewatch.py /root/

ENTRYPOINT ["python3", "kubewatch.py"]
