# 1. Simulate the following topology in Mininet. Set the link bandwidth for (s1,s2) and (s1,s3) as 10Mbps. Use Iperf to test the TCP throughput between every host pair.
#
# h1--s1--s2--h2
#      |
#     s3
#      |
#     h3

import sys
from functools import partial
from mininet.link import TCLink
from mininet.node import OVSKernelSwitch, UserSwitch, Controller
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.log import lg, info
from mininet.util import irange, quietRun

class NetworkTopo(Topo):
    "Topology of task 1."

    def build(self, *args, **params):
        # Create switchs and hosts
        h1, h2, h3 = [self.addHost(h) for h in ('h1','h2','h3')]
        s1, s2, s3 = [self.addSwitch(s) for s in ('s1','s2','s3')]

        # Wire up switches
        self.addLink(h1, s1)
        self.addLink(s1, s3)
        self.addLink(h3, s3)
        self.addLink(s1, s2)
        self.addLink(h2, s2)

def run():
    "Use Iperf to test the TCP throughput between every host pair."

    results={}

    switches = { 'reference user': UserSwitch,
                 'Open vSwitch kernel': OVSKernelSwitch }

    # UserSwitch is horribly slow with recent kernels.
    # We can reinstate it once its performance is fixed
    del switches[ 'reference user' ]

    # Select TCP Reno
    output = quietRun( 'sysctl -w net.ipv4.tcp_congestion_control=reno' )
    assert 'reno' in output

    topo = NetworkTopo()

    for datapath in switches:
        info("*** testing", datapath, "datapath\n")
        Switch = switches[datapath]
        results[datapath]=[]
        link = partial(TCLink, bw=100)
        net = Mininet(topo=topo,switch=Switch,controller=Controller,link=link,waitConnected=True)
        net.start()
        for i in irange(0,2):
            for j in irange(i+1,2):
                src, dst = net.hosts[i], net.hosts[j]
                src.cmd('telnet', dst.IP(), '5001')
                info("testing", src.name, "<->", dst.name, '\n')
                serverbw, _clientbw = net.iperf([src,dst], seconds=5)
                sys.stdout.flush()
                results[datapath] += [(src.name,dst.name,serverbw)]
        net.stop()

        for datapath in switches:
            info("\n*** Network results for", datapath, "datapath:\n")
            result = results[datapath]
            info("Source\tDest\tiperf Results\n")
            for src,dst,serverbw in result:
                info(src,'\t')
                info(dst,'\t')
                info(serverbw,'\n')
            info('\n')

if __name__ == "__main__":
    lg.setLogLevel( 'info' )
    run()