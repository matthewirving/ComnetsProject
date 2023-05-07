import time
#from socket import socket, AF_INET, SOCK_DGRAM, inet_aton
import socket
import struct
import select
import random
import asyncore


#Types:
# 0: Invalid / Null
# 1: Hello Packet
# 2: Hello ACK Packet
# 3: Mulicast Packet
# 4: Unicast Packet
# 5: LSA Packet

# The objective would be to store everything in a struct, but since we have different packet types of varying lengths 
# use this as a reference? https://github.com/sumitece87/comnet2_2020/tree/master/comnetsii_package/Example_Ping
# documentation reference https://docs.google.com/document/d/1meTQd49NvTkn1GZNhilRDmXpstn27qb0XuhDAtOjkKQ/edit#


def create_LSA_packet(seq, TTL, src, hops, advRoute, LSSeq, CRC):
    #Type(1), Len(4), Seq(1), TTL(1), src(1), hops(1), advRoute(4), LSSeq(4), CRC(1)
    #header (18)
    pkttype = 5 # 5 is defined as the pkt type for LSA packets
    header = struct.pack('BBB4sBLLB', pkttype, seq, TTL, socket.inet_aton(src), hops, advRoute, LSSeq, CRC)
    return header

def create_unicast_packet(seq, TTL, src, dst, data):
    #Type(1), Seq(1), TTL(1), src(4), dst(4), data(1-1480)
    #header (11) + data(1-1480) -> 12 - 1491

    pkttype = 4 # 4 is defined as the pkttype for unicast packets

    header = struct.pack('BBB4s4s', pkttype, seq, TTL, socket.inet_aton(src), socket.inet_aton(dst))
    return header + bytes(data, 'utf-8')
    

def create_multicast_packet(seq, TTL, kval, dst1, dst2, dst3, data):
    """Create new packet with given fields"""
    #Type(1), Seq(1), TTL(1), K-val(1), Dest1(4), Dest2(4), Dest3(4), Data(1-1480)
    #header (16) + data(1-1480) -> 17 - 1496

    pkttype = 3 # 3 is defined as the pkttype for multicast packets

    header = struct.pack('BBBB4s4s4s', pkttype, seq, TTL, kval, socket.inet_aton(dst1), socket.inet_aton(dst2), socket.inet_aton(dst3))
    return header + bytes(data, 'utf-8')


def read_header(pkt):
    #change bytes to account for network encapsulations

    #check which packet type it is, and handle accordingly

    rawPacketType = pkt[0]

    if rawPacketType == 0:
        #invalid packet type
        print(0)
    elif rawPacketType == 1:
        #HELLO pkt type
        header = pkt

    elif rawPacketType == 2:
        #HELLO ACK pkt type
        print(2)

    elif rawPacketType == 3:
        #multicast pkt type
        header = pkt[0:16]
        pkttype, seq, TTL, src, dst = struct.unpack('BBBB4s4s4s', header)

    elif rawPacketType == 4:
        #unicast pkt type
        header = pkt[0:11] #correct size for unicast
        pkttype, seq, TTL, src, dst = struct.unpack('BBB4s4s', header)

        src = socket.inet_ntoa(src)
        dst = socket.inet_ntoa(dst)

        return pkttype, seq, TTL, src, dst
        
    elif rawPacketType == 5:
        #LSA packet type
        pkttype, seq, TTL, src, hops, advRoute, LSSeq, CRC = struct.unpack('BBB4sBLLB', header)
        
        src = socket.inet_ntoa(src)

        return pkttype, seq, TTL, src, hops, advRoute, LSSeq, CRC

    else:
        return "error!"


    return

def read_data(pkt):
    #change bytes to account for network encapsulations
    pkttype = pkt[0]

    if pkttype == 0:
        #invalid type
        print(0)
    elif pkttype == 1:
        #HELLO pkttype, no data
        print(1)
    elif pkttype == 2:
        #HELLO ACK pkttype
        print(2)
    elif pkttype == 3:
        #multicast pkttype
        data = pkt[16:]
    elif pkttype == 4:
        #unicast pkttype
        data = pkt[11:]
    elif pkttype == 5:
        data = 0
    
    return data

def main():
    
    myPkt = create_unicast_packet(1, 5, "192.168.1.5", "192.168.1.7", "WHAAAT")
    secondPkt = create_unicast_packet(5, 3, "172.10.0.2", "10.0.0.2", "DATATIME")


    
    pkttype, seq, TTL, src, dst = read_header(myPkt)

    #print(pkttype, seq, TTL, src, dst)

    temp = read_data(myPkt)

    #print("stuff", struct.calcsize('BBB4s4s'), "second ", struct.calcsize('BBB15s15s'))
    #test = struct.pack('BBB4s4s', 4, 1, 5, socket.inet_aton("192.168.1.5"), socket.inet_aton("192.168.1.7"))
    

    

if __name__ == "__main__":
    main()
