# Cyber dragon artwork

`cyber-dragon-source.png` was generated using the built-in image generation tool.
The complete final generation prompt is in [PROMPT.md](PROMPT.md). No image edit
or external CLI/API generation was used. The black source is a positive artwork
mask; its positive shapes become white ink on the PCB.

`cyber-dragon.svg` is the cleaned vector master in a 38 × 49.5 mm back-view frame.
`cyber-dragon.geometry.json` records its polygon geometry. The PCB contains
35 native polygons grouped as **Cyber dragon - back silkscreen**, mirrored into
native board coordinates so the finished back view reads as intended. Holes in
the art are preserved by polygon fracture. Clearance to back solder-pad openings
and via holes is applied during import. Thus some small areas differ from the
unclipped vector master. `manifest.json` records scale/feature cleanup metadata.

Positive features were cleaned at 0.18 mm, negative gaps at 0.20 mm, then
simplified into fabrication vectors. This is a printability starting point,
not a tested ink-resolution guarantee. The image occupies approximately
21.2 × 22.6 mm, below the antenna. It adds no copper or solder-mask openings.
The art and credit are printed in the board's normal white back silkscreen.

The routed native PCB is authoritative; operation scripts under ignored build/
are not a full-board regeneration workflow. Edit the grouped graphic in KiCad
for later artwork changes and regenerate/check the manufacturing files.
