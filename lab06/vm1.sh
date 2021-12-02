#!/bin/bash

sudo mn
h1 ifconfig h1-eth0 mtu 1440
h2 ifconfig h2-eth0 mtu 1440

# ======

sudo ifconfig s1 10.0.0.101/8 up
sudo ovs-vsctl add-br br1
sudo ifconfig ens33 0 up
sudo ovs-vsctl add-port br1 ens33
sudo ifconfig br1 192.168.4.131/24 up

sudo ovs-vsctl add-port s1 vxlan0 -- set interface vxlan0 type=vxlan options:remote_ip=192.168.4.132 option:key=5566 ofport_request=9

sudo ifconfig vxlan_sys_4789 mtu 1440
sudo ifconfig s1-eth1 mtu 1440
sudo ifconfig s1-eth2 mtu 1440