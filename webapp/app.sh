#!/bin/bash
sleep 15
sudo apt-get update
sudo apt install zip unzip -y
sudo apt install python3 -y
sudo apt install python3-pip -y

sudo apt install gunicorn3 -y
sudo apt install nginx -y
sudo apt install postgresql-client -y
sudo pip3 install statsd
sudo yum install amazon-cloudwatch-agent -y
mkdir webapp

cd ~/ && unzip webapp.zip -d webapp

sudo curl -o /home/ubuntu/webapp/amazon-cloudwatch-agent.deb https://s3.amazonaws.com/amazoncloudwatch-agent/debian/amd64/latest/amazon-cloudwatch-agent.deb


#cd /home/ubuntu/webapp && wget https://s3.us-east-1.amazonaws.com/amazoncloudwatch-agent-us-east-1/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb

sudo dpkg -i -E /home/ubuntu/webapp/amazon-cloudwatch-agent.deb

sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
    -a fetch-config \
    -m ec2 \
    -c file:/home/ubuntu/webapp/cloudwatch_config.json \
    -s

sudo service start amazon-cloudwatch-agent 
sudo systemctl enable amazon-cloudwatch-agent.service

sudo pip3 install -r /home/ubuntu/webapp/requirements.txt
sudo cp /home/ubuntu/webapp/service_file.service /etc/systemd/system/service_file.service
sudo cp /home/ubuntu/webapp/nginx_config /etc/nginx/sites-available/default


