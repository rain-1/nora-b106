# Remaining components for two minimum assemblies

Prepared 8 November 2026 for two square-p3 boards already fitted with
U1, C1 and C2. This list adds the USB power/data hardware, optional reset
buttons and headers. It does not buy another module or duplicate the fitted
capacitors. The authoritative population list is README.md and BOM.csv.

The suggested order uses LCSC for one consolidated order, including the exact
USB-C connector. LCSC is an international supplier, not UK-dispatched stock.
Check actual availability, order multiples and the delivered price including
shipping/VAT for your Edinburgh address in the basket before paying. Prices
and quantities can change; this is a parts shortlist, not a live basket quote.

The [CSV](shopping-two-boards.csv) contains suggested order quantities with
spares/small-pack minimums. Review and adjust quantities if the supplier
requires a different multiple. Optional switches/headers can be deleted if
you already have suitable parts. Use LCSC's component shop; JLCPCB's assembly
parts-library purchases are not a route to receive loose components.

| Reference | Needed for two boards | Suggested order | Exact part and listing |
|---|---:|---:|---|
| J1 | 2 | 5 | HRO TYPE-C-31-M-12 — [C165948](https://www.lcsc.com/product-detail/C165948.html) |
| U2 | 2 | 5 | Torex XC6206P332MR-G, SOT-23-3 — [C5446](https://www.lcsc.com/product-detail/C5446.html) |
| U3 | 2 | 10 | ST USBLC6-2SC6, SOT-23-6 — [C7519](https://www.lcsc.com/product-detail/C7519.html) |
| C3/C4 | 4 total | 20 | Samsung CL21B105KBFNNNE, 1 µF 50 V X7R 0805 — [C28323](https://www.lcsc.com/product-detail/C28323.html) |
| R1/R2 | 4 total | 100 | Yageo RC0805FR-075K1L, 5.1 kΩ 1% 0805 — [C84375](https://www.lcsc.com/product-detail/C84375.html) |
| SW1, optional | 2 | 5 | B3F-1000 normally-open 6 mm through-hole — [C93157](https://www.lcsc.com/product-detail/C93157.html) |
| J2/J3, optional | Two 5-pin + two 14-pin sections | 5 strips | ZHOURI 2.54-1*40 straight single-row 40-pin male strip — [C2977586](https://www.lcsc.com/product-detail/C2977586.html) |

The Samsung capacitor is intentionally **50 V rather than the BOM's 16 V**:
the capacitance, X7R dielectric and 0805 package match, and the higher voltage
rating meets the circuit's requirement. This is not a change to the PCB.

The reset footprint has a 6.5 × 4.5 mm hole-centre pattern. B3F-1000 uses
that standard pattern; see page 4 of the [manufacturer drawing via Farnell](https://www.farnell.com/datasheets/2082873.pdf).
The supplier may describe this switch family as Omron or Aratas, formerly
Omron Components. Match the full part number and drawing.

For each board, cut one header strip into 5-pin and 14-pin sections. Male
strips are convenient with female jumper leads. If you prefer female sockets,
buy 2.54 mm single-row 5-position and 14-position sockets instead; these are
optional mechanical choices, not different electrical pinouts.

JP1 is a **solder bridge**: no component needs to be purchased. H1–H4 are
optional M2 mounting holes; screws/standoffs are not required to operate the
board. There is no on-board LED population in this design; the test LED and
its series resistor remain external.

## UK alternatives

If delivery speed matters, these UK storefronts list matching parts. Compare
the total across deliveries against one consolidated order; the USB-C socket
still needs the exact HRO part/land pattern.

- ST USBLC6-2SC6: [Farnell 1269406](https://uk.farnell.com/stmicroelectronics/usblc6-2sc6/esd-protection-17v-sot-23/dp/1269406),
  or [RS 624-7693](https://uk.rs-online.com/web/p/tvs-diodes/6247693).
- Yageo RC0805FR-075K1L: [Farnell 3496074](https://uk.farnell.com/yageo/rc0805fr-075k1l/res-5k1-1-0-125w-0805-thick-film/dp/3496074).
- 1 µF X7R 0805 capacitor: TDK C2012X7R1E105K125AB, 25 V,
  listed as [Farnell 2346940](https://uk.farnell.com/c/passive-components/capacitors/ceramic-capacitors/smd-mlcc-multilayer-ceramic-capacitors?capacitance=1uf&capacitor-case-package=0805-2012-metric-).
- B3F-1000 reset button: [RS 686-6847](https://uk.rs-online.com/web/p/tactile-switches/6866847)
  or [Mouser](https://www.mouser.co.uk/en/ProductDetail/Omron-Electronics/B3F-1000?qs=lK7M36XCk6JQHckSc1xIsg%3D%3D).

Supplier listings, not catalogue images, determine the chosen package. Do not
substitute a different USB-C socket merely because it has sixteen contacts,
or a different SOT-23 regulator merely because it is marked 3.3 V. Pinouts and
mechanical land patterns must match. Both separate 5.1 kΩ CC resistors are
required for the USB population.

## After assembly

Fit the complete USB group before using that connector for target power.
With power disconnected, bridge JP1 for USB power and disconnect the Pico's
3V3 OUT wire. Retain common debugger ground if SWD/UART remains connected.
Do not tie USB regulator output and Pico 3V3 OUT together. Verify the target
rail remains approximately 3.3 V before reconnecting signals.

The working BLE/OTA application does not enable a USB console, and its
MCUboot build has no USB recovery service. Fitting these parts provides the
hardware and USB power; USB serial/data functionality needs a corresponding
firmware build. The USB population itself has not yet been physically tested
in this project.
