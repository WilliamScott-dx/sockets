#!/usr/bin/env python3
"""
The receivers listens on a channel for packets and forms them into a file,
saving it in the specified location.

Usage:
    ./receiver.py p_in p_out c_in filename
        p_in     - the port that the receiver should listen on
        p_out    - the port that the receiver should send from
        c_in     - the port the channel is listening on
        filename - the file to which to write the received data

Authors:
    Ben Frengley
    William Read Scott

Date: 23 July 2015
"""

import sys
from socket import socket
from packet import Packet
from utils import get_port_number, LOCAL_ADDR, DEFAULT_MAGIC_NO, UDPEndpoint


class Receiver(UDPEndpoint):
    """
    A Receiver receives incoming packets to construct a sent file,
    sends acknowledgement packets upon successful transfer of packet.
    """
    def __init__(self, r_in, r_out, c_in, filename):
        self.in_socket, self.out_socket = self.create_socket_pair(r_in, r_out,
                                                                  c_in)
        # remove timeout from the listening socket
        self.in_socket.settimeout(None)

        # open file we will write to
        try:
            self.file = open(filename, "xb")
        except FileExistsError:
            print("Invalid file - file already exists.")
            sys.exit(-1)

        # Expected sequence number, is either a 0 or 1.
        self.expected = 0

    def create_packet(self):
        """
        Create a new acknowledgement packet with the current expected number.
        """
        return Packet(packet_type=Packet.TYPE_ACK,
                      seqno=self.expected)

    def send_ack_packet(self):
        """
        Sends an acknowledgement packet through the out socket.
        """
        packet = self.create_packet()
        self.out_socket.send(packet.serialize())

    def close_sockets(self):
        """
        Closes all sockets.
        """
        self.in_socket.close()
        self.out_socket.close()

    def handle_incoming_packets(self):
        """
        Main loop for receiver, handles incoming packets
        and sends acknowledgement packet when received
        """
        received_data_buffer = b''

        while True:
            # Read in socket buffer
            received_data_buffer = self.in_socket.recv(1000)
            # Deserialize packet
            packet = Packet.deserialize(received_data_buffer)

            # validate the received packet
            if packet is None:
                continue
            if packet.magicno != DEFAULT_MAGIC_NO:
                continue

            self.send_ack_packet()

            if packet.seqno == self.expected:
                self.expected = 1 - self.expected

                # write any data from the packet to the file, or exit
                # if the data packet was empty
                if packet.dataLen > 0:
                    print(packet.dataLen, "bytes written to file")
                    self.file.write(packet.data)
                elif packet.dataLen == 0:
                    self.close_sockets()
                    self.file.close()
                    sys.exit(0)


def main():
    # Make sure we received expected number of args
    if len(sys.argv) != 5:
        print("Invalid arguments -- expected arguments are p_in, p_out,",
              "c_in, and filename")
        sys.exit(-1)

    # Make sure all port numbers are valid
    p_in = get_port_number(sys.argv[1])
    p_out = get_port_number(sys.argv[2])
    c_in = get_port_number(sys.argv[3])
    filename = sys.argv[4]

    # Initialize the receiver
    receiver = Receiver(p_in, p_out, c_in, filename)
    receiver.handle_incoming_packets()

if __name__ == '__main__':
    main()
