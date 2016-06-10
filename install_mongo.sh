#!/bin/bash

case $MONGO_VERSION in
  2.6.12 )
    sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 7F0CEB10 &&
    echo 'deb http://downloads-distro.mongodb.org/repo/ubuntu-upstart dist 10gen' | sudo tee /etc/apt/sources.list.d/mongodb.list
    sudo apt-get update
    sudo apt-get install -y mongodb-org-server=$MONGO_VERSION ;;
  3.0.11 )
    sudo apt-key adv --keyserver keyserver.ubuntu.com --recv 7F0CEB10 &&
    echo "deb http://repo.mongodb.org/apt/debian wheezy/mongodb-org/3.0 main" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.0.list
    sudo apt-get update
    sudo apt-get install -y mongodb-org-server=$MONGO_VERSION ;;
  3.2.6 )
    sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv EA312927 &&
    echo "deb http://repo.mongodb.org/apt/debian wheezy/mongodb-org/3.2 main" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.2.list
    sudo apt-get update
    sudo apt-get install -y mongodb-org-server=$MONGO_VERSION ;;
esac
