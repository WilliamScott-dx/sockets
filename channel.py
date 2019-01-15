"""
Channels facilitate the transferal of packages from a sender to a receiver,
using the UDP protocol.

Usage:
    (fill in later)

Authors:
    Ben Frengley
    William Read Scott

Date: 23 July 2015
"""

import sys
from random import random, seed
from packet import Packet
from utils import LOCAL_ADDR, DEFAULT_MAGIC_NO, UDPEndpoint, get_port_number

def get_packet_loss(packet_loss):
    """
    Determines if the given packet loss is a float <= 0 and < 1,
    returning the packet loss percentage as a float if so, and exiting otherwise.
    """
    try:
        packet_loss = float(packet_loss)
        assert 0 <= packet_loss < 1
        return packet_loss
    except:
        print("{} is an invalid amount of packet loss --".format(packet_loss),
              "valid packet loss is a float <= 0 and < 1")
        sys.exit(-1)


class Channel(UDPEndpoint):
    """
    A Channel forwards packets between a sender and a receiver, while
    simulating packet loss.
    """
    def __init__(self, cs_in, cs_out, cr_in, cr_out, s_in, r_in, packet_loss):
        # Call seed for better RNG
        seed()
        # create socket pair connected to the sender
        self.cs_in_socket, self.cs_out_socket = self.create_socket_pair(cs_in, cs_out, s_in)

        # create socket pair connected to the receiver
        self.cr_in_socket, self.cr_out_socket = self.create_socket_pair(cr_in, cr_out, r_in)

        self.packet_loss = packet_loss

    def packet_lost(self):
        random_no = random()
        if random_no < self.packet_loss:
            return True
        return False

    def valid_magicno(self, packet): # TODO Should this go here, out of class, or in utils?
        if packet.magicno == DEFAULT_MAGIC_NO:
            return True
        print("Magic Number does not match")
        return False

    def process_packet(self, data_buffer):
        packet = Packet.deserialize(data_buffer)
        if packet is not None:
            if not self.valid_magicno(packet):
                if not self.packet_lost():
                    data_to_send = Packet.serialize()
                    # Check if packet is data (0) or ack (1)
                    if packet.type == 0:
                        self.cs_out_socket.send(data_to_send)
                    else:
                        self.cr_out_socket.send(data_to_send)

    def handle_incoming_packets(self):
        # Create data buffers
        receiver_data_buffer = b''
        sender_data_buffer = b''

        # Loop for handling transfer of packets
        while True:
            # Read in socket buffers
            receiver_data_buffer = self.cr_in_socket.recv(200)
            sender_data_buffer = self.cs_in_socket.recv(1000)

            # Process Data buffers
            self.process_packet(receiver_data_buffer)
            self.process_packet(sender_data_buffer)

def main():
    if len(sys.argv) != 8:
        print("Invalid arguments -- expected arguments are  cs_in,",
              "cs_out, cr_in, cr_out, s_in, r_in, packet_loss,")
        sys.exit(-1)

    # Make sure args are valid, otherwise exit
    cs_in = get_port_number(sys.argv[1])
    cs_out = get_port_number(sys.argv[2])
    cr_in = get_port_number(sys.argv[3])
    cr_out = get_port_number(sys.argv[4])
    s_in = get_port_number(sys.argv[5])
    r_in = get_port_number(sys.argv[6])
    packet_loss = get_packet_loss(sys.argv[7])

    # Create channel
    channel = Channel(cs_in, cs_out, cr_in, cr_out, s_in, r_in, packet_loss)
    channel.handle_incoming_packets()

if __name__ == "__main__":
    main()

