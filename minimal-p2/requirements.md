# Compact P2 requirements

Shrink Minimal P1 while retaining reliable SWD bring-up and optional native USB.
Four GPIOs are sufficient: P0.24, P1.06, P0.20, P0.07/AIN3. Keep all passives at
0805 and leave the minimum population at module + two capacitors. Preserve the
manufacturer antenna/ground recommendations and J2 SWD pinout. Native USB needs
the initially SWD-installed bootloader. No assembly service is requested.

Delivered outline: 31.5 × 27.5 mm, 1.6 mm FR4, two layers. The routed PCB is
authoritative. No physical hardware or programming session has been tested.
