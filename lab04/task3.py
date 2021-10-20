# 2. Enable TCP Reno and your selected TCP congestion control algorithm, and test them in Mininet.

from time import sleep
from mininet.link import TCLink
from mininet.node import CPULimitedHost
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import dumpNodeConnections, quietRun
from mininet.log import setLogLevel, info

class SingleSwitchTopo(Topo):
    def build (self,bw=100,delay='200ms',loss=0.1):
        switch1 = self.addSwitch('s1')
        switch2 = self.addSwitch('s2')
        host1 = self.addHost('h1', cpu=.25)
        host2 = self.addHost('h2', cpu=.25)
        self.addLink(host1, switch1, bw=100, delay='5ms', loss=0, use_htb=True)
        self.addLink(host2, switch2, bw=100, delay='5ms', loss=0, use_htb=True)
        self.addLink(switch1, switch2, bw=bw, delay=delay, loss=loss, use_htb=True)

def BandwidthTest():
    with open('bandwidth.dat','w') as f:
        f.write('Bandwidth\treno\tvegas\n')
    bwrange = range(20,181,10)
    bwdict = {bw:[] for bw in bwrange}
    for tcp in ["reno","vegas"]:
        output = quietRun('sysctl -w net.ipv4.tcp_congestion_control=' + tcp +'\n')
        assert tcp in output
        for bw in bwrange:
            topo = SingleSwitchTopo(bw=bw)
            net = Mininet(topo=topo, host=CPULimitedHost, link=TCLink, autoStaticArp=False)
            net.start()
            dumpNodeConnections(net.hosts)
            h1, h2 = net.getNodeByName('h1','h2')
            _serverbw, clientbw = net.iperf([h1,h2],seconds=10)
            bwdict[bw] += [str(clientbw[:-10])]
            print(str(bw)+'\t'+tcp+'\t'+clientbw)
            net.stop()
    with open('bandwidth.dat','a') as f:
        for bw in bwdict.keys():
            f.write(bw+'\t'+'\t'.join(bwdict[bw])+'\n')

def DelayTest():
    with open('delay.dat','w') as f:
        f.write('Delay\treno\tvegas\n')
    delayrange = range(0,401,40)
    delaydict = {delay:[] for delay in delayrange}
    for tcp in ["reno","vegas"]:
        output = quietRun('sysctl -w net.ipv4.tcp_congestion_control=' + tcp +'\n')
        assert tcp in output
        for delay in delayrange:
            topo = SingleSwitchTopo(delay=str(delay)+'ms')
            net = Mininet(topo=topo, host=CPULimitedHost, link=TCLink, autoStaticArp=False)
            net.start()
            dumpNodeConnections(net.hosts)
            h1, h2 = net.getNodeByName('h1','h2')
            _serverbw, clientbw = net.iperf([h1,h2],seconds=10)
            delaydict[delay] += [str(clientbw[:-10])]
            print(str(delay)+'\t'+tcp+'\t'+clientbw)
            net.stop()
    with open('delay.dat','a') as f:
        for delay in delaydict.keys():
            f.write(delay+'\t'+'\t'.join(delaydict[delay])+'\n')

def LossTest():
    with open('loss.dat','w') as f:
        f.write('Loss\treno\tvegas\n')
    lossrange = range(0,61,5)
    lossdict = {loss:[] for loss in lossrange}
    for tcp in ["reno","vegas"]:
        output = quietRun('sysctl -w net.ipv4.tcp_congestion_control=' + tcp +'\n')
        assert tcp in output
        for loss in lossrange:
            topo = SingleSwitchTopo(loss=loss/100)
            net = Mininet(topo=topo, host=CPULimitedHost, link=TCLink, autoStaticArp=False)
            net.start()
            dumpNodeConnections(net.hosts)
            h1, h2 = net.getNodeByName('h1','h2')
            _serverbw, clientbw = net.iperf([h1,h2],seconds=10)
            lossdict[loss] += [str(clientbw[:-10])]
            print(str(loss)+'\t'+tcp+'\t'+clientbw)
            net.stop()
    with open('loss.dat','a') as f:
        for loss in lossdict.keys():
            f.write(loss+'\t'+'\t'.join(lossdict[loss])+'\n')


if __name__ == '__main__':
    # setLogLevel('info')
    print('*** Bandwidth Test')
    BandwidthTest()
    print('*** Delay Test')
    DelayTest()
    print('*** Loss Test')
    LossTest()