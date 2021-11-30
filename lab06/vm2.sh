#!/bin/bash

sudo ovs-vsctl add-br s1
sudo ifconfig s1 10.0.0.102/8 up

sudo ovs-vsctl add-br br1
sudo ifconfig ens33 0 up
sudo ovs-vsctl add-port br1 ens33
sudo ifconfig br1 192.168.4.132/24 up

sudo ovs-vsctl add-port s1 vxlan0 -- set interface vxlan0 type=vxlan options:remote_ip=192.168.4.131

# ====clean====
# sudo ovs-vsctl del-br br1