# To construct a centralized structure
# for P2P model.

import os, glob
from sys import argv
from time import sleep
import math
from mininet.link import TCLink
from mininet.topo import LinearTopo, Topo
from mininet.net import Mininet
from mininet.log import lg, info
from mininet.util import dumpNodeConnections,irange, quietRun, run
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
    
    servercmd = "python server.py"
    clientcmd = "python peer.py"
    resultfile = "result_py.dat"
    avgresfile = "avgres_py.dat"
    # if len(argv)>=2:
    #     if(argv[1]=="c"):
    #         servercmd = "./server"
    #         clientcmd = "./client"
    #         resultfile = "result_c.dat"
    #         avgresfile = "avgres_c.dat"

    dirty = False
    if len(argv)>=3:
        if(argv[2]=="--dirty"):
            dirty = True

    topo = CentralizedTopo(hostnumber)
    # topo = LinearTopo(1,hostnumber) # The same.
    net = Mininet(topo=topo, link=TCLink, autoStaticArp=False)
    net.start()
    # Test connectivity.
    if not dirty:
        net.pingAll()

    # clean the files.
    for file_receive in glob.glob("file_receive*"):
        os.remove(file_receive)

    # Generate tracker file
    fileSize = os.path.getsize("file.txt")
    chunkSize = int(math.ceil(fileSize/(hostnumber-1)))
    with open("tracker.dat","w") as tf:
        for i in range(hostnumber-1):
            tf.write(str(i)+"\t"+net.hosts[i+1].IP()+"\n")

    # Try to dump
    dumpNodeConnections(net.hosts)

    # Place the server on h1.
    net.hosts[0].cmdPrint(servercmd,chunkSize,"&")
    
    sleep(2)
    
    # All other host request files.
    for i in range(1,hostnumber):
        net.hosts[i].cmdPrint(clientcmd,chunkSize,net.hosts[0].IP(),net.hosts[i].IP(),"" if i == hostnumber - 1 else "&")
        
    CLI(net)
    
    # check the difference.
    # if not dirty:
    #     for i in range(1,hostnumber):
    #         run("diff file.txt file_receive_"+net.hosts[i].name+".txt")

    results = []
    with open(resultfile,"r") as rf:
        resultlines = rf.read().splitlines()
        for i in range(1,len(resultlines)):
            results.append(float(resultlines[i].split('\t')[1]))
    avg = sum(results)/len(results) if not len(results) == 0 else -1
    print("Average: "+str(avg))
    print("Avaliable: " + str(len(results)) +  "/" + str(hostnumber-1) + "(" + str(int(len(results)*100/(hostnumber-1))) + "%)")
    with open(avgresfile,"a") as af:
        af.write(str(hostnumber-1)+"\t"+str(avg)+"\n")

    net.stop()

if __name__=="__main__":
    lg.setLogLevel( 'info' )
    hostnumber = input("Please input hostnumber:")
    FileTransfer(int(hostnumber))
