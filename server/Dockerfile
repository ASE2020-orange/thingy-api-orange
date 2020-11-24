FROM ubuntu:18.04
ADD . /server
WORKDIR /server
RUN chmod a+x run_server.sh 
RUN apt update && apt -f -y install python3 && apt -f -y install python3-pip && pip3 install -r requirements.txt
EXPOSE 1080
ENTRYPOINT ["./run_server.sh"]
