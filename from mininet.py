from mininet.topo import Topo
from mininet.net import Mininet
from mininet.log import setLogLevel, info
from mininet.node import RemoteController, Controller, OVSKernelSwitch, Node, Host
from mininet.link import TCLink, Link
from mininet.cli import CLI
from mininet.util import dumpNodeConnections
from packet import read_data, read_header, create_LSA_packet, create_multicast_packet, create_unicast_packet
import heapq
import sys


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
        header = read_header(packet)
        dest = header['dst']
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
        header = read_header(packet)
        if header is not None:
            # Process the packet based on its type
            pkt_type = header["type"]
            pkt_data = read_data(packet)
            if pkt_type == 3:  # Multicast packet
                # Process multicast packet
                pass
            elif pkt_type == 4:  # Unicast packet
                # Process unicast packet
                # must determine if data field holds a multicast packet
                if header["dst"] != self.ip:
                    if header["TTL"] > 0:
                        newPacket = create_unicast_packet(header["seq"], header["TTL"] - 1, header["src"], header["dst"], pkt_data)
                        self.send_packet(self, newPacket)
                    else:
                        #drop the packet since TTL is low
                        pass
                
                elif pkt_data[0] == 3: # this means the first byte in data is 3, which is the value of the type field for a multicast packet
                    # now we have to split the packets to unicast, and determine k closest destinations
                    multiHeader = read_header(pkt_data)
                    multiData = read_data(pkt_data)

                    destList = [] # this will be an array containing all 3 destinations, sorted by closest first. We will have to implement a method.

                    # send k packets to destinations. Currently "src" field is the original src where the multicast packet was sent from, SEQ = 1, & TTL = 10
                    for i in range(0, multiHeader["kval"]):
                        self.send_packet(self, create_unicast_packet(1, 10, header["src"], destList[i], multiData))
                
                else:
                    print(f"{self.name} Packet recieved")


            elif pkt_type == 5:  # LSA packet
                
                pass
            else:
                # Invalid packet type
                print("Invalid packet type")
        else:
            print("Error reading packet header")

    def process_packet_queue(self):
        for packet in self.packet_queue:
            self.send_packet(packet)
        self.packet_queue = []

    #def read_header(self, packet):
        # Replace this with the appropriate function

