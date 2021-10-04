# To construct a centralized structure
# for C/S model.

from mininet.link import TCLink
from mininet.topo import LinearTopo, Topo
from mininet.net import Mininet
from mininet.log import lg, info
from mininet.util import dumpNodeConnections,irange, run
from mininet.cli import CLI

class CentralizedTopo(Topo):
    "A centralized topo."
    
    def build(self, hostnumber=2, **params):
        # Central switch
        switch = self.addSwitch('s1')
        # Star hosts
        hosts = [self.addHost('h%s' % h) for h in irange(1,hostnumber)]

        # Star structure
        for host in hosts:
            self.addLink(switch, host)

def FileTransfer(hostnumber=2):
    "Make file transfer between switch and hosts simutanously."
    
    topo = CentralizedTopo(hostnumber)
    # topo = LinearTopo(1,hostnumber) # The same.
    net = Mininet(topo=topo, link=TCLink, autoStaticArp=False)
    net.start()
    # Test connectivity.
    # Currently, s1 could not pass to h1, h2. SINCE IT IS A ROUTER!
    # for i in range(hostnumber):
    #     net.ping([net.switches[0],net.hosts[i]])
    net.pingAll()

    # clean the files.
    run("rm -rf file_receive_*")

    # Place the server on h1.
    net.hosts[0].cmdPrint("./server","&")
    
    # All other host request the file from h1.
    for i in range(1,hostnumber):
        net.hosts[i].cmdPrint("./client",net.hosts[0].IP(),net.hosts[i].name,"&")

    CLI(net)
    
    # check the difference.
    for i in range(1,hostnumber):
        run("diff file.txt file_receive_"+net.hosts[i].name+".txt")
    net.stop()

if __name__=="__main__":
    lg.setLogLevel( 'info' )
    hostnumber = input("Please input hostnumber:")
    FileTransfer(int(hostnumber))
