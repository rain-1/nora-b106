# NORA-B106 minimal bring-up requirements

1. SWD programming and externally supplied regulated 3.3 V are the first priority.
2. Expose as many GPIOs as fit easily, with no on-board LED/button loads.
3. Optional native USB, using the selected real through-hole USB-A male plug.
   A PCB-contact plug is not used. USB flashing requires a bootloader first
   programmed over SWD.
4. Bare PCBs from JLCPCB; self assembly. Low parts count and ordinary two-layer
   fabrication take priority over compactness.

New project, separate from revision D. Only the previously checked module
symbol and land pattern are reused; schematic, placement and routing are new.
CAD validation is complete for prototype P1. No physical hardware is tested.
