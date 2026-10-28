# Square P3 validation

- ERC: zero violations.
- DRC: zero violations, unconnected items or schematic-parity issues.
- Ground: one continuous front region and one continuous back region; 38 ground
  stitching vias. The back below the module remains reserved for ground, with
  the antenna ground row protected and K4/K6 stitches retained.
- Audit: all assigned nets and all 82 module land sizes, locations, mask and
  paste match the checked module footprint. No open via drill intersects a
  module solder land; the 100 nF capacitor is nearest the module.
- Mechanical: 49.5 mm square, 1.6 mm, 2 layers; fourteen-pin GPIO header;
  four unplated 2.2 mm mounting holes at the documented coordinates.
  Recommended ground extent and 10 mm antenna clearance to header, USB and
  mounting-hole courtyards are retained. The closest courtyard is H1, 14.70 mm
  away; J3 is 16.16 mm away.
- Firmware: P3 and P1 electrical part/net assignments and J2/J3 pinouts match;
  shared firmware source/image SHA-256 hashes match P1's validated manifest.
  Its twelve-GPIO resolved map matches this board. Eight uploader tests pass.
  The shared P1 binaries are reused unchanged, not rebuilt as P3 firmware.
- Schematic, front/back copper, assembly and signature previews were visually
  inspected. The signature is back silkscreen; no logo copper enters the antenna.
- The fabrication ZIP contains the copper, masks, silkscreens, outline, top
  paste, and separate plated/unplated drill files. Hashes are in its manifest.

Reports and source hashes are under fabrication/. Stencil ordering assumptions
and limitations are in hardware/STENCIL.md. No physical PCB assembly, paste
printing, SWD, USB, GPIO/ADC or radio tests have been performed.
