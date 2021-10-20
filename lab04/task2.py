# 2. Enable TCP Reno and your selected TCP congestion control algorithm, and test them in Mininet.

from time import sleep
from mininet.link import TCLink
from mininet.node import CPULimitedHost
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import dumpNodeConnections, quietRun
from mininet.log import setLogLevel, info

class SingleSwitchTopo(Topo):
    def build (self):
        switch1 = self.addSwitch('s1')
        switch2 = self.addSwitch('s2')
        host1 = self.addHost('h1', cpu=.25)
        host2 = self.addHost('h2', cpu=.25)
        self.addLink(host1, switch1, bw=100, delay='5ms', loss=0, use_htb=True)
        self.addLink(host2, switch2, bw=100, delay='5ms', loss=0, use_htb=True)
        self.addLink(switch1, switch2, bw=100, delay='200ms', loss=0.1, use_htb=True)

def Test(tcp):
    "Create network and run simple performace test."
    topo = SingleSwitchTopo()
    net = Mininet(topo=topo, host=CPULimitedHost, link=TCLink, autoStaticArp=False)
    net.start()
    dumpNodeConnections(net.hosts)
    output = quietRun('sysctl -w net.ipv4.tcp_congestion_control=' + tcp +'\n')
    assert tcp in output
    h1, h2 = net.getNodeByName('h1','h2')
    _serverbw, clientbw = net.iperf([h1,h2],seconds=10)
    with open('default.dat','a') as f:
        f.write(tcp+'\t'+clientbw[:-10]+'\n')
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    with open('default.dat','w') as f:
        f.write('Alg\tThroughput\n')
    tcp = 'reno'
    Test(tcp)
    sleep(2)
    tcp = 'vegas'
    Test(tcp)