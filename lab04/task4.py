# 4. Construct a network with a bottleneck link shared by multiple pairs of senders and receivers. Study how these sender-receiver pairs share the bottleneck link.

from time import time
from select import poll, POLLIN
from subprocess import Popen, PIPE
from time import sleep
from mininet.link import TCLink
from mininet.node import CPULimitedHost
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import decode, dumpNodeConnections, quietRun
from mininet.log import setLogLevel, info

def monitorFiles( outfiles, seconds, timeoutms ):
    "Monitor set of files and return [(host, line)...]"
    devnull = open( '/dev/null', 'w' )
    tails, fdToFile, fdToHost = {}, {}, {}
    for h, outfile in outfiles.items():
        tail = Popen( [ 'tail', '-f', outfile ],
                      stdout=PIPE, stderr=devnull )
        fd = tail.stdout.fileno()
        tails[ h ] = tail
        fdToFile[ fd ] = tail.stdout
        fdToHost[ fd ] = h
    # Prepare to poll output files
    readable = poll()
    for t in tails.values():
        readable.register( t.stdout.fileno(), POLLIN )
    # Run until a set number of seconds have elapsed
    endTime = time() + seconds
    while time() < endTime:
        fdlist = readable.poll(timeoutms)
        if fdlist:
            for fd, _flags in fdlist:
                f = fdToFile[ fd ]
                host = fdToHost[ fd ]
                # Wait for a line of output
                line = f.readline().strip()
                yield host, decode( line )
        else:
            # If we timed out, return nothing
            yield None, ''
    for t in tails.values():
        t.terminate()
    devnull.close()  # Not really necessary

class MultiplePairTopo(Topo):
    def build (self,N=3):
        switch1 = self.addSwitch('s1')
        switch2 = self.addSwitch('s2')
        host0 = self.addHost('h0',cpu=.25)      # served as the server
        self.addLink(switch1, host0, bw=200)
        self.addLink(switch1, switch2, bw=100)
        for i in range(1,N+1):
            host = self.addHost('h'+str(i), cpu=.25/N)
            self.addLink(switch2, host, bw=i*20)

def Test(tcp,seconds=15):
    "Create network and run simple performace test."
    topo = MultiplePairTopo(N=5)
    net = Mininet(topo=topo, host=CPULimitedHost, link=TCLink, autoStaticArp=False)
    net.start()
    hosts = net.hosts
    dumpNodeConnections(hosts)
    output = quietRun('sysctl -w net.ipv4.tcp_congestion_control=' + tcp +'\n')
    assert tcp in output
    
    server = hosts[0]
    outfiles,errfiles = {},{}
    for h in hosts:
        outfiles[ h ] = '/tmp/%s.out' % h.name
        errfiles[ h ] = '/tmp/%s.err' % h.name
        h.cmd( 'echo >', outfiles[ h ] )
        h.cmd( 'echo >', errfiles[ h ] )
        # Create and/or erase output files
        if h == server:
            h.cmdPrint('iperf3','-s','-i','1','-p','3389',
                    '>', outfiles[ h ],
                   '2>', errfiles[ h ],
                   '&')
        else:
            h.cmdPrint('iperf3','-c',server.IP(),'-p','3389',
                    '>', outfiles[ h ],
                   '2>', errfiles[ h ],
                   '&',)
    info( "Monitoring output for", seconds, "seconds\n" )
    for h, line in monitorFiles( outfiles, seconds, timeoutms=500 ):
        if h:
            info( '%s: %s\n' % ( h.name, line ) )
    for h in hosts:
        h.cmd('kill %iperf')
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    tcp = 'reno'
    Test(tcp)
    sleep(2)
    tcp = 'vegas'
    Test(tcp)