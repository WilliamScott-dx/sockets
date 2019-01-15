"""
words

the documentation could probably be better

Authors:
    Ben Frengley
    William Read Scott

Date: 1 August 2015
"""

from pickle import dumps, loads
from utils import DEFAULT_MAGIC_NO


class Packet(object):
    """
    A Packet represents a UDP packet to be sent through a channel.

    Packets can have the following types:
        TYPE_DATA - the packet contains between 0 and 512 bytes of data
                    (inclusive) to be sent
        TYPE_ACK  - the packet is an acknowledgement of another packet and
                    contains no data
    """

    TYPE_DATA = 0
    TYPE_ACK = 1

    def __init__(self, data='', packet_type=TYPE_DATA, seqno=0,
            magicno=DEFAULT_MAGIC_NO):
        """

        """
        self.data = data
        self.dataLen = len(data)
        self.type = packet_type
        self.seqno = seqno
        self.magicno = magicno


    def serialize(self):
        """
        Converts the packet to a series of bytes which can be sent over a
        socket.
        """
        return dumps(self)


    @staticmethod
    def deserialize(data):
        """
        Attempts to deserialize the given data into a valid Packet. Returns None if the
        data does not resolve into a Packet, including if it does not resolve into anything.
        """
        obj = b''
        try:
            obj = loads(data)
            if type(obj) == Packet:
                return obj
            else:
                return None
        except:
            return None

