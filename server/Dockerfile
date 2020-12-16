FROM ubuntu:18.04
RUN apt update
RUN apt -f -y install python3-pip
RUN apt -f -y install python3.7
RUN python3.7 -m pip install pip
RUN mkdir ./server
ADD requirements.txt /server
WORKDIR /server
RUN python3.7 -m pip install -r requirements.txt
ADD . /server
RUN chmod a+x run_server.sh 
EXPOSE 1080
ENTRYPOINT ["./run_server.sh"]