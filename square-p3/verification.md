# Dragon P3.1 validation

- ERC: zero violations.
- DRC: zero violations, unconnected items or schematic-parity issues.
- Ground: one continuous front region and one continuous back region; 32 ground
  stitching vias. The back beneath U1 remains reserved for ground, with its
  antenna ground row and K4/K6 stitches retained.
- All assigned pad nets and all 82 module land sizes, positions, mask/paste
  match the checked footprint. No open via drill intersects a module solder
  land; the 100 nF capacitor is closest to the module.
- Mechanical: 38 × 49.5 mm, 1.6 mm, 2 layers. USB centre x=19 mm. Two optional
  2.2 mm mounting holes at (3.5, 46), (34.5, 46). Optional normally-open SW1
  resets to GND, with two correctly connected pads per switch terminal.
- Recommended ground extent and 10 mm tall-component antenna clearance are
  retained. Closest relevant courtyard is J3, 11.04 mm from the antenna.
- Core circuit and J2/J3 mappings match P1; the optional switch only connects
  RESET_N/GND. Shared P1 source/image hashes match its validated manifest and
  twelve-GPIO report. Eight uploader tests pass. P1 images are reused unchanged.
- The generated dragon was converted to 35 native B.Silkscreen regions, with
  0.18 mm positive / 0.20 mm negative feature cleanup and solder-pad clearance.
  It adds no decorative copper or solder-mask openings. Source, vector, prompt
  and artwork metadata are in artwork/. Small tips/details were simplified.
- Schematic, front/back copper, assembly and dragon previews visually inspected.
- The fabrication ZIP contains copper, masks, silkscreens, outline, top paste,
  and separate plated/unplated drill files, with hashes in its manifest.

Reports and source hashes are under fabrication/. No physical assembly, paste
transfer, SWD, USB, GPIO/ADC or RF tests have been performed. White ink appearance
in a preview is illustrative; the fabricator's process determines the print.
