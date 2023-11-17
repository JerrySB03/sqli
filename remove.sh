#!/bin/bash

sudo docker rm -f sqli 2>/dev/null
sudo docker network rm sqli_net 2>/dev/null
sudo docker rmi sqli 2>/dev/null