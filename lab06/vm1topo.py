from mininet.cli import CLI
from mininet.link import TCLink
from mininet.node import CPULimitedHost
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.log import lg, info
from mininet.util import dumpNodeConnections, run

vm1ip = "192.168.4.131"         #
vm2ip = "192.168.4.132"         #

class VM1Topo(Topo):
    "Topology of VM1."

    def build(self):
        switch1 = self.addSwitch('s1', ip='10.0.0.101')
        host1 = self.addHost('h1', cpu=.25, ip='10.0.0.1')
        host2 = self.addHost('h2', cpu=.25, ip='10.0.0.2')
        self.addLink(host1, switch1, use_htb=True)
        self.addLink(host2, switch1, use_htb=True)

if __name__=="__main__":
    topo = VM1Topo()
    net = Mininet(topo=topo,host=CPULimitedHost, link=TCLink, autoStaticArp=True)
    net.start()
    dumpNodeConnections(net.hosts)

    run('ifconfig s1 10.0.0.101/8 up')
    run('ovs-vsctl del-br br1')
    run('ovs-vsctl add-br br1')
    run('ifconfig ens33 0 up')
    run('ovs-vsctl add-port br1 ens33')
    run('ifconfig br1 ' + vm1ip +  '/24 up')

    # set up VxLAN
    run('ovs-vsctl add-port s1 vxlan0 -- set interface vxlan0 type=vxlan options:remote_ip=' + vm2ip + ' option:key=100 ofport_request=10')

    # config MTU
    run('ifconfig vxlan_sys_4789 mtu 1450')
    s1 = net.switches[0]
    h1, h2 = net.hosts
    h1.cmdPrint('ifconfig h1-eth0 mtu 1450')
    h2.cmdPrint('ifconfig h2-eth0 mtu 1450')
    s1.cmdPrint('ifconfig s1-eth1 mtu 1450')
    s1.cmdPrint('ifconfig s1-eth2 mtu 1450')

    # TBD: set up flow-table manually

    CLI(net)
    net.stop()