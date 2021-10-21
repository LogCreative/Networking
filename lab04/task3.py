# 3. Construct a network with only one pair of sender and receiver. Study how TCP throughput varies with respect to link bandwidth/link delay/loss rate for the above two TCP versions.

import os
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

def Test(type="bandwidth"):
    with open(type+'.dat','w') as f:
        f.write(type+'\treno\tvegas\n')
    if type=="bandwidth":
        myrange = range(20,181,10)
    elif type=="delay":
        myrange = range(0,401,40)
    elif type=="loss":
        myrange = range(0,61,5)
    mydict = {limit:[] for limit in myrange}
    fileSize = os.path.getsize("file.txt")
    for tcp in ["reno","vegas"]:
        output = quietRun('sysctl -w net.ipv4.tcp_congestion_control=' + tcp +'\n')
        assert tcp in output
        for limit in myrange:
            if type=="bandwidth":
                topo = SingleSwitchTopo(bw=limit)
            elif type=="delay":
                topo = SingleSwitchTopo(delay=str(limit)+'ms')
            elif type=="loss":
                topo = SingleSwitchTopo(loss=limit/100)
            net = Mininet(topo=topo, host=CPULimitedHost, link=TCLink, autoStaticArp=False)
            net.start()
            dumpNodeConnections(net.hosts)
            h1, h2 = net.getNodeByName('h1','h2')
            h1.cmdPrint("./server","&")
            res = h2.cmdPrint("./client",fileSize,h1.IP(),h2.name)
            res = res.rstrip('\n')
            print(str(limit)+'\t'+res)
            mydict[limit] += [res]
            net.stop()
            sleep(3)
    with open(type+'.dat','a') as f:
        for limit in sorted(mydict.keys()):
            f.write(str(limit)+'\t'+'\t'.join(mydict[limit])+'\n')

if __name__ == '__main__':
    # setLogLevel('info')
    print('*** Bandwidth Test')
    Test("bandwidth")
    print('*** Delay Test')
    Test("delay")
    print('*** Loss Test')
    Test("loss")