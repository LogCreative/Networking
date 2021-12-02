from mininet.cli import CLI
from mininet.link import TCLink
from mininet.node import CPULimitedHost
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.log import lg, info
from mininet.util import dumpNodeConnections

class VM2Topo(Topo):
    "Topology of VM2."

    def build(self):
        switch1 = self.addSwitch('s1', ip='10.0.0.102')
        host3 = self.addHost('h3', cpu=.25, ip='10.0.0.3')
        host4 = self.addHost('h4', cpu=.25, ip='10.0.0.4')
        self.addLink(host3, switch1, use_htb=True)
        self.addLink(host4, switch1, use_htb=True)

if __name__=="__main__":
    topo = VM2Topo()
    net = Mininet(topo=topo,host=CPULimitedHost, link=TCLink, autoStaticArp=True)
    net.start()
    dumpNodeConnections(net.hosts)
    CLI(net)
    net.stop()