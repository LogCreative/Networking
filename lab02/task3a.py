# 3. Let us add another link between s2 and s3. 
# Try pinging h2 from h1. What would happen? 
# 
# h1--s1--s2--h2
#      | /
#     s3
#      |
#     h3

from mininet.link import TCLink
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.log import lg, info
from mininet.util import dumpNodeConnections
from mininet.cli import CLI

class NetworkTopo(Topo):
    "Topology of task 1."

    def build(self):
        # Create switchs and hosts
        h1, h2, h3 = [self.addHost(h) for h in ('h1','h2','h3')]
        s1, s2, s3 = [self.addSwitch(s) for s in ('s1','s2','s3')]

        # Wire up switches with constriants
        self.addLink(s1, s2, bw=10, loss=5)
        self.addLink(s1, s3, bw=10, loss=5)

        # New link between s2, s3
        self.addLink(s2, s3, bw=10, loss=5)

        self.addLink(h1, s1)
        self.addLink(h3, s3)
        self.addLink(h2, s2)

def pingTest():
    topo = NetworkTopo()
    net = Mininet(topo=topo,link=TCLink,autoStaticArp=True)
    net.start()
    dumpNodeConnections(net.hosts)
    # h1, h2 = net.getNodeByName('h1','h2')
    # net.ping([h2, h1])
    CLI(net)            # debug interface
    net.stop()
    
if __name__ == "__main__":
    # lg.setLogLevel( 'info' )
    pingTest()