# We're using Ubuntu 20.10
FROM nitesh231/docker:latest

#
# Clone repo and prepare working directory
#
RUN git clone -b sql-extended https://github.com/maxpayne7000/RemixGeng /root/userbot
RUN mkdir /root/userbot/.bin
WORKDIR /root/userbot

CMD ["python3","-m","userbot"]
