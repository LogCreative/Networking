# 4. Construct a network with a bottleneck link shared by multiple pairs of senders and receivers. Study how these sender-receiver pairs share the bottleneck link.

import glob
import os
from time import sleep
from mininet.link import TCLink
from mininet.node import CPULimitedHost
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import dumpNodeConnections, quietRun
from mininet.log import setLogLevel, info

class MultiplePairTopo(Topo):
    def build (self,N=3):
        switch1 = self.addSwitch('s1')
        switch2 = self.addSwitch('s2')
        host0 = self.addHost('h0',cpu=.25)      # served as the server
        self.addLink(switch1, host0, bw=200)
        self.addLink(switch1, switch2, bw=45)
        for i in range(1,N):
            host = self.addHost('h'+str(i), cpu=.25/N)
            self.addLink(switch2, host, bw=i*25/N)

def Test(tcp,hostnumber=3):
    "Create network and run simple performace test."

    fileSize = os.path.getsize("file.txt")

    # clean the files.
    for file_receive in glob.glob("file_receive*"):
        os.remove(file_receive)

    topo = MultiplePairTopo(N=hostnumber)
    net = Mininet(topo=topo, host=CPULimitedHost, link=TCLink, autoStaticArp=False)
    net.start()
    hosts = net.hosts
    dumpNodeConnections(hosts)
    output = quietRun('sysctl -w net.ipv4.tcp_congestion_control=' + tcp +'\n')
    assert tcp in output
    
    server = hosts[0]
    server.cmdPrint("python server.py","&")
    sleep(2)
    for i in range(1,hostnumber):
        hosts[i].cmdPrint("python client.py",fileSize,server.IP(),hosts[i].name,"" if i == hostnumber - 1 else "&")

    complete = 0
    while not complete == hostnumber:
        results = []
        with open("result_py.dat","r") as rf:
            resultlines = rf.read().splitlines()
            complete = len(resultlines)
            for i in range(1,len(resultlines)):
                results.append(float(resultlines[i].split('\t')[1]))
        sleep(5)
    
    os.rename('result_py.dat',tcp+'_multi.dat')

    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    tcp = 'reno'
    Test(tcp,5)
    sleep(2)
    tcp = 'vegas'
    Test(tcp,5)