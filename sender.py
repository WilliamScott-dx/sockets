#!/usr/bin/env python3
"""
The sender for this assignment transfers a file through a channel to a receiver,
as a series of packets, using UDP.

Usage:
    ./sender.py p_in p_out c_in filename
        p_in     - the port that the sender should listen on
        p_out    - the port that the sender should send from
        c_in     - the port the channel is listening on
        filename - the file to send

Authors:
    Ben Frengley
    William Read Scott

Date: 23 July 2015
"""

import sys
from socket import socket, timeout
from packet import Packet
from utils import get_port_number, LOCAL_ADDR, DEFAULT_MAGIC_NO, UDPEndpoint


def get_file_contents(filename):
    """
    Determines if the given file exists and can be successfully opened,
    returning the file contents if so, and exiting otherwise.
    """
    try:
        file = open(filename, "rb")
        contents = file.read()
        file.close()
        return contents
    except:
        print("File \"{}\" doesn't exist")
        sys.exit(-1)


class Sender(UDPEndpoint):
    """
    A Sender takes a file and reads it, sending it to a channel over a socket
    using UDP.
    """
    def __init__(self, s_in, s_out, c_in, data):
        self.in_socket, self.out_socket = self.create_socket_pair(s_in, s_out,
                                                                  c_in)

        self.data = data
        self.next_seqno = 0


    def data_packets(self):
        """
        Lazily creates and yields packets to be sent.
        """
        data_consumed = 0
        data_length = len(self.data)

        # we add 512 to ensure that one blank packet will be sent
        while data_consumed < data_length + 512:
            packet = Packet(data=self.data[data_consumed : data_consumed + 512],
                            packet_type=Packet.TYPE_DATA,
                            seqno=self.next_seqno)
            data_consumed += 512
            self.next_seqno = 1 - self.next_seqno
            yield packet


    def send_packet(self, packet):
        """
        Repeatedly sends a packet until a valid response is received.
        """
        data_to_send = packet.serialize()
        valid_response_received = False

        while not valid_response_received:
            self.out_socket.send(data_to_send)
            print("packet sent")
            response = self.wait_for_response()

            if not response is None:
                # validate the response
                valid_response_received = \
                        response.magicno == DEFAULT_MAGIC_NO and \
                        response.type == Packet.TYPE_ACK and \
                        response.dataLen == 0

        # packet sent!
        print("valid response received")
        return True # probably unneeded


    def wait_for_response(self):
        """
        Listens on the incoming socket, reading in data as it is received and
        returning the deserialized packet if one exists, or None if no response
        or an invalid response was received.
        """
        received_data_buffer = b''

        try:
            received_data_buffer = self.in_socket.recv(200)
        except timeout:
            # nothing arrived within 1 second
            return None

        return Packet.deserialize(received_data_buffer)


    def send_file(self):
        """
        Breaks the file contents up into packets and sends them one by one,
        closing the sockets on completion.
        """
        for packet in self.data_packets():
            self.send_packet(packet)

        self.in_socket.close()
        self.out_socket.close()


def main():
    if len(sys.argv) != 5:
        print("Invalid arguments -- expected arguments are p_in, p_out,",
              "c_in, and filename")
        sys.exit(-1)

    p_in = get_port_number(sys.argv[1])
    p_out = get_port_number(sys.argv[2])
    c_in = get_port_number(sys.argv[3])

    data = get_file_contents(sys.argv[4])

    # initialise file transfer
    sender = Sender(p_in, p_out, c_in, data)
    sender.send_file()


if __name__ == '__main__':
    main()
