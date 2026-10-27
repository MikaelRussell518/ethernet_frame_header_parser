# ethernet_frame_header_parser

Decodes Ethernet II (DIX) frame headers, extracting the destination MAC, source MAC, and EtherType from the first 14 bytes of a frame.

## Usage

```python
from ethernet_frame_header_parser import parse

frame = bytes(
    [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,   # destination MAC
     0x00, 0x1A, 0x2B, 0x3C, 0x4D, 0x5E,   # source MAC
     0x08, 0x00]                            # EtherType (IPv4)
)

header = parse(frame)
print(header.destination.hex())  # ffffffffffff
print(header.source.hex())       # 001a2b3c4d5e
print(hex(header.ethertype))     # 0x800
```

Exported names: `parse` (function), `EthernetHeader` (frozen dataclass with `destination`, `source`, `ethertype` fields), `ParseError` (subclass of `ValueError`).

## Why

Network packet dissectors often pull in large dependencies for protocols you don't need. This library does one thing: splits the 14-byte Ethernet II header into its three fields and rejects frames it cannot interpret. `destination` and `source` are returned as raw 6-byte `bytes` objects rather than formatted strings, so formatting (colon, dash, or dot notation) is left to the caller. `ethertype` is returned as an `int` in host byte order, not as a two-byte `bytes` object, because callers almost always compare it against integer constants.

## Edge cases

Frames shorter than 14 bytes raise `ParseError`. The EtherType/Length field is ambiguous in the IEEE 802.3 spec: values ≤ 1500 are lengths, values ≥ 1536 are types. This library only handles Ethernet II frames, so any value ≤ 1500 is rejected. VLAN-tagged frames (EtherType 0x8100) are returned with 0x8100 as the EtherType — the 802.1Q tag and inner EtherType are not parsed.
