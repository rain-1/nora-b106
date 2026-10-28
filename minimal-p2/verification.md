# Compact P2 validation

- ERC: zero violations.
- DRC: zero violations, unrouted items or schematic parity issues.
- Ground: one continuous back ground region; two front ground regions, each
  connected by at least two stitching vias (17 and 2, 19 total). Antenna-row
  stitching is retained.
- Audit: all assigned nets and 82 module pad sizes/locations/mask/paste match
  the checked module land pattern; no open via drill intersects module lands.
- Mechanical: 31.5 × 27.5 mm, 1.6 mm thickness, four GPIOs on a six-pin header;
  recommended ground extent and 10 mm tall-component antenna clearance retained.
  Antenna-to-courtyard separation: J1 19.15 mm, J2 10.72 mm, J3 10.43 mm.
- Firmware: separate P2 USB IDs/key, four GPIO mappings and ADC at J3 pin 6;
  built signed factory/update images, checked vectors/flash bounds, eight host
  uploader tests passed. Sources are in firmware/ and artifacts in firmware/dist/.
- Schematic, copper and assembly previews visually inspected before delivery.

Fabrication reports/source hashes: fabrication/. Firmware hashes and static
report: firmware/dist/. No physical assembly, SWD, USB, GPIO/ADC or RF tests
have been performed. Earlier P1 files are retained separately under ../minimal-p1/.
