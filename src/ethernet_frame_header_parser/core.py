"""Core parsing logic for Ethernet II frame headers.

Only Ethernet II (DIX) frames are supported. A frame shorter than 14 bytes
cannot contain a destination MAC, source MAC, and EtherType, so it is rejected.
Frames whose EtherType is <= 1500 are rejected because in that region the
field is a length, not a type, and decoding it as EtherType would be misleading.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class EthernetHeader:
    """Parsed Ethernet II header.

    Attributes:
        destination: 6-byte destination MAC address.
        source: 6-byte source MAC address.
        ethertype: 2-byte EtherType field as an integer in host order.
    """

    destination: bytes
    source: bytes
    ethertype: int


class ParseError(ValueError):
    """Raised when the input cannot be decoded as an Ethernet II header."""


def parse(frame: bytes) -> EthernetHeader:
    """Decode an Ethernet II frame header from the first 14 bytes of *frame*.

    The destination and source MACs are returned as raw 6-byte objects.
    EtherType is returned as an int in host byte order so callers do not have
to
    worry about network vs. host ordering.

    Raises:
        ParseError: if *frame* is shorter than 14 bytes or if the EtherType/
            length field is <= 1500, which indicates an 802.3 length field
            rather than an EtherType.
    """
    if len(frame) < 14:
        raise ParseError(
            "Ethernet II header requires at least 14 bytes, got {}".format(
                len(frame)
            )
        )

    ethertype = (frame[12] << 8) | frame[13]

    # Values <= 1500 mean the field is a length (802.3), not an EtherType.
    # We reject this so callers never mistake a length for a protocol number.
    if ethertype <= 1500:
        raise ParseError(
            "EtherType/Length field is {} (<=1500); not an Ethernet II frame".format(
                ethertype
            )
        )

    return EthernetHeader(
        destination=bytes(frame[0:6]),
        source=bytes(frame[6:12]),
        ethertype=ethertype,
    )
