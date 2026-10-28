# Dragon P3.2 validation

- ERC: zero violations.
- DRC: zero violations, unconnected items or schematic-parity issues.
- Ground: one continuous region on each layer, with 31 ground stitching vias.
  The module's back ground reference, protected antenna ground row, six antenna
  ground pads and K4/K6 stitches are retained.
- All assigned pad nets and 82 module land positions/sizes/mask/paste match the
  checked footprint. No open via drill enters a module solder land; the 100 nF
  bypass remains closest to the module.
- USB-C: pad/drill geometry matches the checked original HRO land pattern.
  Both D+ and both D− contacts are joined; all VBUS/GND contacts and shell are
  connected. CC1 and CC2 each have an independent 5.1k/1% resistor to GND. SBU
  pads remain unconnected. No USB-PD or higher-voltage function is implemented.
- Mechanical: 40.5 × 49.5 mm, 1.6 mm FR4, two layers. Socket centred at x=20.25
  mm, y=46.2 mm; front lip extends about 0.35 mm beyond the board edge.
  Four 2.2 mm unplated M2 holes: H1 (3.5,46), H2 (37,46), H3 (3.5,3.5),
  H4 (37,3.5). Recommended RF ground extent is retained. Closest mounting-hole
  courtyard is H3, 10.20 mm from the antenna; J3 is 11.04 mm away.
- Optional SW1 still grounds RESET_N, with the two pads per terminal connected.
  It remains DNP/optional and does not change the minimum assembly.
- P1 firmware-facing module/header/power/data assignments are unchanged. The
  compatibility check separately verifies the new connector and CC mapping,
  shared P1 source/image hashes and the resolved twelve-GPIO map. Eight host
  uploader tests pass. Existing P1 images are reused unchanged.
- The native back-silkscreen dragon is retained and centred in the wider frame;
  artwork adds no copper or mask openings. It remains 35 vector regions.
- Schematic, copper, assembly and back-art previews visually inspected.
- Current fabrication ZIP includes copper, masks, silkscreens, outline, top
  paste, and both plated/non-plated drill files. Its manifest records source
  and output hashes. Old USB-A/stencil output is not the current order package.

No physical assembly, paste-transfer, SWD, USB, GPIO/ADC or RF tests have been
performed. White/green preview colours are illustrative. See hardware/README.md
for exact connector requirements and hardware/STENCIL.md for stencil ordering.
