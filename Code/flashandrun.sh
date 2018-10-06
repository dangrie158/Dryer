#!/bin/bash

rsync -Lavz -e "ssh" --exclude ".git/*" --exclude ".direnv/*" --progress . pi@192.168.178.29:Dryer
ssh pi@192.168.178.29 -t "cd Dryer && python3 ./run.py"
