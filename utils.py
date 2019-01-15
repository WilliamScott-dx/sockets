"""
This file comtains shared variables and functions for this assignment.

Authors:
    Ben Frengley
    William Read Scott

Date: 1 August 2015
"""

from abc import ABCMeta
from time import sleep
from socket import socket

LOCAL_ADDR = '127.0.0.1'
DEFAULT_MAGIC_NO = 0x497E


def get_port_number(port):
    """
    Determines if the given port is an integer between 1024 and 64000,
    returning the port number as an integer if so, and exiting otherwise.
    """
    try:
        port = int(port)
        assert 1024 < port < 64000
        return port
    except:
        print("{} is an invalid port number --".format(port),
              "valid ports are 1024 to 64000, exclusive")
        sys.exit(-1)


class UDPEndpoint(metaclass=ABCMeta):
    """
    UDPEndpoint is an abstract class used to define the connection algorithm
    which is shared between all of its subclasses.
    """
    def connect(self, socket, target):
        """
        Attempts to connect socket to the target (address, port) pair,
        repeating every 3 seconds until the connection is opened.
        """
        while True:
            try:
                socket.connect(target)
                print("connected successfully to", target)
                return True
            except ConnectionRefusedError:
                print("connection to {} refused...\n".format(target) +
                      "retrying in 3 seconds")
                sleep(3)


    def create_socket_pair(self, in_port, out_port, out_end_port):
        """
        Creates an incoming and outgoing socket pair, blocking until a remote
        socket has connected to the receiving socket on in_port. The outgoing
        socket connects from out_port to out_end_port.

        Returns the pair (receiving port, outgoing port).
        """
        # create a socket to listen for an incoming connection
        in_sock = socket()
        in_sock.bind((LOCAL_ADDR, in_port))
        in_sock.listen(1)

        # create an outgoing socket connected to out_end_port
        out_sock = socket()
        out_sock.bind((LOCAL_ADDR, out_port))
        self.connect(out_sock, (LOCAL_ADDR, out_end_port))

        # accept an incoming connection
        connected_in_sock, addr = in_sock.accept()
        print("incoming connection from", addr, "accepted")
        in_sock.close()

        # set 1.0s timeouts for the listening sockets
        connected_in_sock.settimeout(1.0)

        return connected_in_sock, out_sock

