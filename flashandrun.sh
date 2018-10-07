#!/bin/bash

IP=192.168.178.29
rsync -Lavz -e "ssh" --exclude ".git/*" --exclude ".direnv/*" --progress ./Code/ pi@$IP:Dryer
scp dryer.service pi@$IP:

if [ "$1" = "DEBUG" ]
then
    ssh pi@$IP -t "sudo systemctl stop dryer.service \
        && chmod +x ~/Dryer/run.py \
        && cd Dryer \
        && ./run.py"
else
    ssh pi@$IP -t "sudo systemctl stop dryer.service \
        && chmod +x ~/Dryer/run.py \
        && sudo cp ~/dryer.service /etc/systemd/system/ \
        && sudo systemctl daemon-reload \
        && sudo systemctl enable dryer.service || true \
        && sudo systemctl start dryer.service"
fi