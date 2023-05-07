from mininet.topo import Topo
from mininet.net import Mininet
from mininet.log import setLogLevel, info
from mininet.node import RemoteController, Controller, OVSKernelSwitch, Node, Host
from mininet.link import TCLink, Link
from mininet.cli import CLI
from mininet.util import dumpNodeConnections
import heapq
import sys


class MyTopo(Topo):
    def build(self):
        # Add hosts
        s = self.addHost('s', ip = '10.0.0.1/24')
        d1 = self.addHost('d1', ip = '10.0.0.9/24')
        d2 = self.addHost('d2', ip = '10.0.0.10/24')
        d3 = self.addHost('d3', ip = '10.0.0.11/24')

        # Add routers
        r1 = self.addSwitch('r1', cls=Router)
        r2 = self.addSwitch('r2', cls=Router)
        r3 = self.addSwitch('r3', cls=Router)
        r4 = self.addSwitch('r4', cls=Router)
        r5 = self.addSwitch('r5', cls=Router)
        r6 = self.addSwitch('r6', cls=Router)
        r7 = self.addSwitch('r7', cls=Router)

        # Add links
        # Add links
        self.addLink(s, r1, intfName1='s-eth0', intfName2='r1-eth0', bw=10)
        self.addLink(r1, r2, intfName1='r1-eth1', intfName2='r2-eth0', bw=10)
        self.addLink(r1, r3, intfName1='r1-eth2', intfName2='r3-eth0', bw=10)
        self.addLink(r2, r3, intfName1='r2-eth1', intfName2='r3-eth1', bw=10)
        self.addLink(r2, r6, intfName1='r2-eth2', intfName2='r6-eth0', bw=10)
        self.addLink(r3, r4, intfName1='r3-eth2', intfName2='r4-eth0', bw=10)
        self.addLink(r3, r5, intfName1='r3-eth3', intfName2='r5-eth0', bw=10)
        self.addLink(r4, d2, intfName1='r4-eth1', intfName2='d2-eth0', bw=10)
        self.addLink(r5, d3, intfName1='r5-eth1', intfName2='d3-eth0', bw=10)
        self.addLink(r6, r7, intfName1='r6-eth1', intfName2='r7-eth1', bw=10)
        self.addLink(r7, d1, intfName1='r7-eth0', intfName2='d1-eth0', bw=10)


def configure_ips(net):
    s, r1, r2, r3, r4, r5, r6, r7, d1, d2, d3 = net.get('s', 'r1', 'r2', 'r3', 'r4', 'r5', 'r6', 'r7', 'd1', 'd2', 'd3')

    # Set IP addresses for hosts
    s.setIP('10.0.0.1/24')
    d1.setIP('10.0.0.9/24')
    d2.setIP('10.0.0.10/24')
    d3.setIP('10.0.0.11/24')

    # Set IP addresses for routers
    r1.setIP('10.0.0.2/24', intf='r1-eth0')
    r1.setIP('10.0.1.1/24', intf='r1-eth1')
    r1.setIP('10.0.2.1/24', intf='r1-eth2')

    r2.setIP('10.0.1.2/24', intf='r2-eth0')
    r2.setIP('10.0.3.1/24', intf='r2-eth1')
    r2.setIP('10.0.4.1/24', intf='r2-eth2')

    r3.setIP('10.0.2.2/24', intf='r3-eth0')
    r3.setIP('10.0.3.2/24', intf='r3-eth1')
    r3.setIP('10.0.5.1/24', intf='r3-eth2')
    r3.setIP('10.0.6.1/24', intf='r3-eth3')

    r4.setIP('10.0.4.2/24', intf='r4-eth0')
    r4.setIP('10.0.7.1/24', intf='r4-eth1')

    r5.setIP('10.0.5.2/24', intf='r5-eth0')
    r5.setIP('10.0.8.1/24', intf='r5-eth1')

    r6.setIP('10.0.4.3/24', intf='r6-eth0')
    r6.setIP('10.0.9.1/24', intf='r6-eth1')

    r7.setIP('10.0.6.2/24', intf='r7-eth1')
    r7.setIP('10.0.9.2/24', intf='r7-eth0')

  
def start_network():
    setLogLevel('info')
    topo = MyTopo()
    net = Mininet(topo=topo, controller=RemoteController, link=TCLink)
    net.start()
    configure_ips(net)
    dumpNodeConnections(net.hosts)
    CLI(net)

if __name__ == '__main__':
    start_network()