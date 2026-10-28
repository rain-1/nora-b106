# Primary sources used

- u-blox NORA-B1 data sheet UBX-20027119 R13:
  https://content.u-blox.com/sites/default/files/NORA-B1_DataSheet_UBX-20027119.pdf
  Pin table, normal voltage mode, module geometry and pad/mask/paste dimensions.
- u-blox integration manual UBX-20027617 R10:
  https://content.u-blox.com/sites/default/files/NORA-B1_SIM_UBX-20027617.pdf
  Power, SWD, ground plane and integrated antenna keepouts/reflow instructions.
- Same Sky UP2-AH-TH, 2025-04-24 rev. 1.07:
  https://www.sameskydevices.com/product/resource/up2-ah-th.pdf
  Exact UP2-AH-1-TH plug geometry. Top-view PCB footprint, 1 mm signal holes,
  2.5/2/2.5 mm pin pitch, 11.7 mm shield spacing, 1 × 2.2 mm plated slots,
  4.5 mm locating post spacing. USB pin numbering follows standard USB-A
  convention: with the front pointing +Y, pin 1 (VBUS) is on the right.
- Torex XC6206:
  https://product.torexsemi.com/system/files/series/xc6206.pdf
  SOT-23 pins 1=GND, 2=VOUT, 3=VIN. Separate input/output ceramic capacitors;
  C4 preserves output capacitance with the power jumper open.
- ST USBLC6-2:
  https://www.st.com/resource/en/datasheet/usblc6-2.pdf
  SOT-23-6 I/O pairs 1/6 and 3/4; 2=GND, 5=VBUS.
- Raspberry Pi debugprobe v2.3.1:
  https://github.com/raspberrypi/debugprobe/releases/tag/debugprobe-v2.3.1
  GP2 SWCLK, GP3 SWDIO, GP1 reset, GP4/GP5 UART TX/RX.
- OpenOCD source 2893f940012e19cda8ccb6038766b0d77f26bd0e:
  https://github.com/openocd-org/openocd/tree/2893f940012e19cda8ccb6038766b0d77f26bd0e
  nRF53 support is needed; Debian 13's OpenOCD 0.12.0 is insufficient.
- Nordic MCUboot serial recovery:
  https://nrfconnectdocs.nordicsemi.com/ncs/latest/nrf/app_dev/bootloaders_dfu/mcuboot_serial_recovery.html
  USB firmware updates need suitable firmware/bootloader, initially via SWD.

The CAD checks do not establish physical operation. USB firmware and the Pico
programming combination remain untested. The module symbol and 82-pad land
pattern were reused from the checked revision D project; the Dragon P3.2 layout is updated. Initial P1 was Backplane-assisted; P3.2 uses native
KiCad edits and the KiCad Python API.

Stencil ordering references are linked in hardware/STENCIL.md.
Shared firmware source, dependency licences and artifact hashes are retained
in ../minimal-p1/firmware/; the P3 compatibility check verifies them.

The optional SW_Push symbol and SW_PUSH_6mm footprint come from the installed
KiCad libraries, with their existing licence notices retained in hardware/.
Cyber dragon generation details and vector import constraints are in artwork/.

USB-C uses the same checked HRO TYPE-C-31-M-12 land pattern as revision D:
- Manufacturer drawing, 2020-12-08, via LCSC C165948:
  https://www.lcsc.com/datasheet/C165948.pdf
- HRO drawing referenced by the KiCad footprint:
  http://www.krhro.com/uploads/soft/180320/1-1P320120243.pdf
- ST AN5225, CC pull-downs and USB Type-C device/sink pin mapping:
  https://www.st.com/resource/en/application_note/dm00536349.pdf
The USB-C land/pad geometry is independently audited against the local checked
footprint. Its F.Silkscreen was removed in the original snapshot; pads, paste,
mask, drill, body and courtyard geometry remain unchanged.

Current JLCPCB marking guidance (checked 2026-10-28):
https://jlcpcb.com/help/article/how-to-mark-on-pcb
The legacy order-number placeholder was removed from the current P3.2 artwork.
