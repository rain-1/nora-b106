# Sources checked for revision B

Retrieved 18 October 2026. Downloaded vendor PDFs and extracted text/images are
local reference material, excluded from Git and the fabrication ZIP.

- u-blox **NORA-B1 data sheet, UBX-20027119 R13**, 15 December 2025:
  https://content.u-blox.com/sites/default/files/NORA-B1_DataSheet_UBX-20027119.pdf
  Tables 6/13; Figures 3/10; sections 2.1, 2.2, 2.5.7, 5.1 and 5.2.3.
  Used for pin assignments, normal-voltage power mode, clock options, USB,
  82-pad top-view footprint, and B106 outline. All pads are 0.6 mm square;
  E/F/G/J pins 4 and 5 use the central +/-0.55 mm positions shown in Figure 10.
- u-blox **NORA-B1 system integration manual, UBX-20027617 R10**:
  https://content.u-blox.com/sites/default/files/NORA-B1_SIM_UBX-20027617.pdf
  Sections 1.5, 5, 6.3.3, 6.5, 6.6.2, 6.9. Used for power connections,
  antenna-ground requirements/keepout, SWD, native USB, and paste/mask advice.
- Torex **XC6206**, ETR03005-009:
  https://product.torexsemi.com/system/files/series/xc6206.pdf
  SOT-23 pins: 1=GND, 2=VOUT, 3=VIN; ceramic output capacitor >=1 uF;
  selected ordering code XC6206P332MR-G, 3.3 V, +/-2%.
- ST **USBLC6-2**, SOT-23-6 ordering code USBLC6-2SC6:
  https://www.st.com/resource/en/datasheet/usblc6-2.pdf
  1/6 and 3/4 are the paired I/O channels; 2=GND and 5=VBUS.
- HRO **TYPE-C-31-M-12** connector land pattern, via KiCad's footprint:
  http://www.krhro.com/uploads/soft/180320/1-1P320120243.pdf
  Manufacturer drawing (2020-12-08) also retrieved through LCSC C165948:
  https://datasheet.lcsc.com/datasheet/pdf/9e56b777c022540fcce7c7f67825f55e.pdf?productCode=C165948
  Checked peg spacing 5.78 mm, shell-hole spacing 8.65 mm / 4.18 mm, data
  pitch 0.5 mm, pin names, and connector orientation against the local KiCad
  footprint. Only the edge-overhanging silkscreen was removed. Verify the
  purchased part is this exact variant.
- Raspberry Pi **debugprobe v2.3.1** Pico configuration:
  https://github.com/raspberrypi/debugprobe/blob/debugprobe-v2.3.1/include/board_pico_config.h
  GP2=SWCLK, GP3=SWDIO, GP1=RESET, GP4/GP5=UART TX/RX.
  https://datasheets.raspberrypi.com/pico/Pico-R3-A4-Pinout.pdf
- OpenOCD nRF53 target implementation:
  https://github.com/openocd-org/openocd/blob/master/tcl/target/nordic/nrf53.cfg
  The included config falls back to the older target/nrf53.cfg location.
  Revision B uses upstream source commit
  `2893f940012e19cda8ccb6038766b0d77f26bd0e` for its local CMSIS-DAP build.
  Offline parsing lists both application and network cores. This does not
  establish successful communication with a physical Pico or NORA module.
  Debian 13's stable package is OpenOCD 0.12.0, which lacks nRF53 support:
  https://packages.debian.org/trixie/openocd
  https://github.com/openocd-org/openocd/blob/2893f940012e19cda8ccb6038766b0d77f26bd0e/README.md
- Nordic **nrfx v3.2.0 MDK nrf5340_application.h**:
  https://github.com/NordicSemiconductor/nrfx/blob/v3.2.0/mdk/nrf5340_application.h
  FICR INFO.DEVICEID 0x00FF0204; PART 0x00FF020C;
  P0 secure base 0x50842500; OUTSET +0x08, OUTCLR +0x0C,
  PIN_CNF[20] +0x250. Used only for the non-flash GPIO smoke-test script.
- JLCPCB published manufacturing capabilities:
  https://jlcpcb.com/capabilities/pcb-capabilities
  Used to choose conventional two-layer rules. Upload review and an actual
  quote are still required; no purchase/order has been placed.

Copied stock KiCad library content is covered by the notices in
`hardware/LICENSE-KiCad-footprints.txt` and `hardware/LICENSE-KiCad-symbols.txt`.
The custom module land pattern was derived from the manufacturer's drawing;
its pad numbering was independently checked against the top-view pin map.
