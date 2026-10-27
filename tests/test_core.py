"""Tests for ethernet_frame_header_parser.core."""

import unittest

from ethernet_frame_header_parser.core import (
    parse,
    EthernetHeader,
    ParseError,
)


class TestParse(unittest.TestCase):
    def test_basic_ipv4_frame(self):
        dst = bytes([0x11, 0x22, 0x33, 0x44, 0x55, 0x66])
        src = bytes([0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF])
        ethertype = 0x0800  # IPv4
        frame = dst + src + bytes([0x08, 0x00])
        header = parse(frame)
        self.assertEqual(header.destination, dst)
        self.assertEqual(header.source, src)
        self.assertEqual(header.ethertype, ethertype)

    def test_payload_included(self):
        dst = bytes([0xFF] * 6)
        src = bytes([0x00] * 6)
        payload = b"hello world payload"
        frame = dst + src + bytes([0x86, 0xDD]) + payload  # IPv6
        header = parse(frame)
        self.assertEqual(header.destination, dst)
        self.assertEqual(header.source, src)
        self.assertEqual(header.ethertype, 0x86DD)

    def test_macs_are_bytes_not_bytearray(self):
        frame = bytes([0x01] * 12 + [0x08, 0x00])
        header = parse(frame)
        self.assertIsInstance(header.destination, bytes)
        self.assertIsInstance(header.source, bytes)

    def test_ethertype_arp(self):
        frame = bytes(12) + bytes([0x08, 0x06])
        header = parse(frame)
        self.assertEqual(header.ethertype, 0x0806)

    def test_ethertype_vlan(self):
        frame = bytes(12) + bytes([0x81, 0x00])
        header = parse(frame)
        self.assertEqual(header.ethertype, 0x8100)

    def test_exactly_14_bytes(self):
        frame = bytes([0xDE, 0xAD, 0xBE, 0xEF, 0x00, 0x01]) * 2 + bytes(
            [0x08, 0x00]
        )
        header = parse(frame)
        self.assertEqual(header.destination, bytes([0xDE, 0xAD, 0xBE, 0xEF, 0x00, 0x01]))
        self.assertEqual(header.source, bytes([0xDE, 0xAD, 0xBE, 0xEF, 0x00, 0x01]))
        self.assertEqual(header.ethertype, 0x0800)

    def test_min_valid_ethertype_1536(self):
        frame = bytes(12) + bytes([0x06, 0x00])
        header = parse(frame)
        self.assertEqual(header.ethertype, 0x0600)

    def test_too_short_raises(self):
        with self.assertRaises(ParseError):
            parse(b"\x00" * 13)

    def test_empty_raises(self):
        with self.assertRaises(ParseError):
            parse(b"")

    def test_802_3_length_field_raises(self):
        frame = bytes(12) + bytes([0x05, 0xDC])  # 1500
        with self.assertRaises(ParseError):
            parse(frame)

    def test_802_3_small_length_raises(self):
        frame = bytes(12) + bytes([0x00, 0x10])  # 16
        with self.assertRaises(ParseError):
            parse(frame)

    def test_frozen_dataclass(self):
        frame = bytes(12) + bytes([0x08, 0x00])
        header = parse(frame)
        with self.assertRaises(Exception):
            header.ethertype = 0

    def test_return_type(self):
        frame = bytes(12) + bytes([0x08, 0x00])
        header = parse(frame)
        self.assertIsInstance(header, EthernetHeader)


if __name__ == "__main__":
    unittest.main()
