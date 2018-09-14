#!/bin/bash
docker rm -f $(docker ps -aq)

ovs-vsctl del-br vnbr
