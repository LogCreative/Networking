#!/bin/bash

sudo ovs-vsctl del-br s1
sudo ovs-vsctl del-br br1

sudo ovs-vsctl add-br s1
sudo ifconfig s1 10.0.0.102/8 up

sudo ovs-vsctl add-br br1
sudo ifconfig ens33 0 up
sudo ovs-vsctl add-port br1 ens33
sudo ifconfig br1 192.168.4.132/24 up

sudo ovs-vsctl add-port s1 vxlan1 -- set interface vxlan1 type=vxlan options:remote_ip=192.168.4.131 option:key=100 ofport_request=10

# ====clean====
# sudo ovs-vsctl del-br br1