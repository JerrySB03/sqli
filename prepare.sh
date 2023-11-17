#!/bin/bash

# Install dependencies
sudo apt update
sudo apt-get install -y python3 wget docker.io

sudo systemctl enable docker --now
BASE_URL="http://178.16.130.233:8080/files/sqli/"
TMP_DIR=$(mktemp -d)
cd $TMP_DIR

wget -O src.zip $BASE_URL/src.zip 2>/dev/null
wget -O Dockerfile $BASE_URL/Dockerfile 2>/dev/null
wget -O requirements.txt $BASE_URL/requirements.txt 2>/dev/null

unzip src.zip

# Build docker image
sudo docker build -t sqli .
sudo docker rm -f sqli 2>/dev/null
sudo docker network create --subnet=172.21.0.0/16 sqli_net
sudo docker run --detach --name sqli --net sqli_net --ip 172.21.0.2 sqli

cd -
rm -rf $TMP_DIR
