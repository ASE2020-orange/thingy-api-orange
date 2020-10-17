FROM ubuntu:18.04
ADD . /server
WORKDIR /server
RUN apt update && apt -f -y install python3 && apt -f -y install python3-pip && pip3 install -r requirements.txt
EXPOSE 1080
CMD ["python3", "./server.py",  "1080"]
