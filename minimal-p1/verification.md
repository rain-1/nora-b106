# Prototype P1 validation

The original Backplane source was checked with KiCad 10.99.0-bp.4; the working
KiCad 9 export is separately validated and used for the committed fabrication files:
- ERC: 0 violations.
- DRC: 0 violations, 0 unconnected items, 0 schematic parity issues.
- Separate ground check: one continuous bottom ground region; five top ground
  islands with [9, 3, 2, 3, 2] stitching vias (19 ground vias total).
- Independent pad audit: all assigned nets match design.json; 82 module pad
  positions/sizes/mask/paste match the checked land pattern; no open drilled
  via intersects module solder lands. Two layers, 1.6 mm thickness.
- KiCad 9.0.2 compatibility copy: ERC/DRC/parity all zero.
- Schematic, front/back copper, assembly and rear silkscreen previews inspected.
- Gerber ZIP contents match the exported files; plated and non-plated drills
  both present. Source/export SHA-256 hashes are in fabrication/manifest.json.

No warning exclusions were added to obtain these results. Fabrication reports
are in fabrication/reports/. Manufacturer-specific constraints still require
engineering judgement; automated checks do not establish physical operation.

The USB bootloader and GPIO/ADC serial application have now been built, signed
and statically validated; see firmware/dist/validation.json and firmware/README.md.
No physical assembly, Pico attach/programming, USB enumeration/update, ADC
measurement, Bluetooth link or radio test is complete.
