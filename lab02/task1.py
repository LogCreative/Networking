# 1. Simulate the following topology in Mininet. Set the link bandwidth for (s1,s2) and (s1,s3) as 10Mbps. Use Iperf to test the TCP throughput between every host pair.
#
# h1--s1--s2--h2
#      |
#     s3
#      |
#     h3

from mininet.link import TCLink
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.log import lg, info
from mininet.util import dumpNodeConnections

class NetworkTopo(Topo):
    "Topology of task 1."

    def build(self):
        # Create switchs and hosts
        h1, h2, h3 = [self.addHost(h) for h in ('h1','h2','h3')]
        s1, s2, s3 = [self.addSwitch(s) for s in ('s1','s2','s3')]

        # Wire up switches with constriants
        self.addLink(s1, s2, bw=10)
        self.addLink(s1, s3, bw=10)

        self.addLink(h1, s1)
        self.addLink(h3, s3)
        self.addLink(h2, s2)

def perfTest():
    "Use Iperf to test the TCP throughput between every host pair."
    topo = NetworkTopo()
    # The constructor of TCLink is required
    # to get the constraints from topo.
    net = Mininet(topo=topo,link=TCLink,autoStaticArp=True)
    net.start()
    dumpNodeConnections(net.hosts)
    h1, h2, h3 = net.getNodeByName('h1','h2','h3')
    net.iperf((h1,h2))
    net.iperf((h1,h3))
    net.iperf((h2,h3))
    net.stop()
    
if __name__ == "__main__":
    # lg.setLogLevel( 'info' )
    perfTest()