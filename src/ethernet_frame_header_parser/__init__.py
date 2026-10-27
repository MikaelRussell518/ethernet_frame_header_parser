"""ethernet_frame_header_parser: decode Ethernet II frame headers.

Re-exports parse for convenience.
"""
from ethernet_frame_header_parser.core import parse, EthernetHeader, ParseError

__all__ = ["parse", "EthernetHeader", "ParseError"]
