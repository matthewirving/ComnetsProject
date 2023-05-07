#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from mininet.topo import Topo
from mininet.net import Mininet
from mininet.log import setLogLevel, info
from mininet.node import RemoteController, Controller, OVSKernelSwitch, Node, Host
from mininet.link import TCLink, Link
from mininet.cli import CLI
from mininet.util import dumpNodeConnections
import packet
import heapq
import sys
from scapy.all import *


class UDPRouter(Node):
    def __init__(self, name, ip, *args, **kwargs):
        super(UDPRouter, self).__init__(name, *args, **kwargs)
        self.ip = ip
        self.routing_table = {}
        self.packet_queue = []

    def config(self, **params):
        super(UDPRouter, self).config(**params)
        self.cmd('sysctl -w net.ipv4.ip_forward=1')

    def get_links(self, net):
        links = {}
        for intf in self.intfList():
            link = self.connectionsTo(intf.node)
            if link:
                neighbor = link[0][1]
                cost = int(intf.bw)
                links[neighbor.name] = cost
            for dest in ['d1', 'd2', 'd3']:
                if dest != self.name:
                    link = self.connectionsTo(net.get(dest))[0]
                    cost = int(link[0].bw)
                    links[dest] = cost
        return links

    def compute_shortest_paths(self, graph, start):
        distance = {}
        for node in graph:
            distance[node] = sys.maxsize
        distance[start] = 0

        heap = [(0, start)]

        while heap:
            (dist, node) = heapq.heappop(heap)

            for neighbor, cost in graph[node]:
                new_dist = dist + cost
                if new_dist < distance[neighbor]:
                    distance[neighbor] = new_dist
                    heapq.heappush(heap, (new_dist, neighbor))

        return distance

    def compute_routing_tables(self, net):
        graph = {}
        for n in net.hosts:
            if n != self:
                graph[n.name] = self.get_links(net)
        self.routing_table = self.compute_shortest_paths(graph, self.name)

    def send_packet(self, packet):
        dest = packet[IP].dst
        if dest in self.routing_table:
            nexthop = self.routing_table[dest]
            out_intf = None
            for intf in self.intfList():
                link = self.connectionsTo(intf.node)
                if link and link[0][1].name == nexthop:
                    out_intf = intf
                    break

            if out_intf:
                info(f"{self.name}: Sending packet to {dest} via {nexthop}\n")
                self.send(out_intf, packet)
            else:
                info(f"{self.name}: No valid interface found for {dest}\n")
        else:
            info(f"{self.name}: Destination {dest} not found in routing table\n")

    def receive_packet(self, packet):
        header = read_header(packet) # get header in order to process packet
        
        if header["dst"] == self.ip: #if the packet's destination is the router
            info(f"{self.name}: Packet received for local processing\n")
            # Process packet here
            #check what type it is
            if(header.type == 1): 
                #hello packet
                print(1)
            elif(header.type == 2):
                #hello ACK packet
                print(2)
            elif(header.type == 3):
                #multicast packet
                print(3)
            elif(header.type == 4):
                #unicast packet
                #check if this router is the intended destination
                #if it is, we also have to check if the data field contains a multicast packet
                data = read_data(packet)

                print(4)
            elif(header.type == 5):
                #LSA packet
                print(5)
            else:
                print("error!")
        else:
            self.packet_queue.append(packet)

    def process_packet_queue(self):
        for packet in self.packet_queue:
            self.send_packet(packet)
        self.packet_queue = []


if __name__ == '__main__':
    print("Router Started...")
    udp_router = UDPRouter("router", "10.0.0.1")

