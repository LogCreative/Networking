from mininet.cli import CLI
from mininet.link import TCLink
from mininet.node import CPULimitedHost
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.log import lg, info
from mininet.util import dumpNodeConnections

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
    CLI(net)
    net.stop()