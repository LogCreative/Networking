from mininet.cli import CLI
from mininet.link import TCLink
from mininet.node import CPULimitedHost
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.log import lg, info
from mininet.util import dumpNodeConnections, run

vm1ip = "192.168.4.131"         #
vm2ip = "192.168.4.132"         #

class VM2Topo(Topo):
    "Topology of VM2."

    def build(self):
        switch2 = self.addSwitch('s2', ip='10.0.0.102')
        host3 = self.addHost('h3', cpu=.25, ip='10.0.0.3')
        host4 = self.addHost('h4', cpu=.25, ip='10.0.0.4')
        self.addLink(host3, switch2, use_htb=True)
        self.addLink(host4, switch2, use_htb=True)

if __name__=="__main__":
    topo = VM2Topo()
    net = Mininet(topo=topo,host=CPULimitedHost, link=TCLink, autoStaticArp=True)
    net.start()
    dumpNodeConnections(net.hosts)
    run('ifconfig s2 10.0.0.102/8 up')
    run('ovs-vsctl del-br br1')
    run('ovs-vsctl add-br br1')
    run('ifconfig ens33 0 up')
    run('ovs-vsctl add-port br1 ens33')
    run('ifconfig br1 ' + vm2ip +  '/24 up')

    # set up VxLAN
    run('ovs-vsctl add-port s2 vxlan0 -- set interface vxlan0 type=vxlan options:remote_ip=' + vm1ip + ' option:key=100 ofport_request=10')

    # config MTU
    run('ifconfig vxlan_sys_4789 mtu 1500')
    s2 = net.switches[0]
    h3, h4 = net.hosts
    h3.cmdPrint('ifconfig h3-eth0 mtu 1450')
    h4.cmdPrint('ifconfig h4-eth0 mtu 1450')
    s2.cmdPrint('ifconfig s2-eth1 mtu 1450')
    s2.cmdPrint('ifconfig s2-eth2 mtu 1450')

    CLI(net)
    net.stop()