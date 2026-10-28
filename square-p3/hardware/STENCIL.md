# Solder-paste stencil

The PCB already includes solder mask (the permanent green coating). The separate
thin sheet used to deposit paste is a **solder-paste stencil**. It must be removed
before reflow/hot-plate heating. Use the **F.Paste** artwork, not F.Mask.

## First choice: small frameless steel

For this 49.5 mm square board, start with a **100 × 100 mm custom frameless**
stainless stencil, top side only. This leaves about 25 mm of handling/taping
margin around each edge. A **0.12 mm** thickness is a reasonable prototype
starting point, not a u-blox guaranteed assembly specification; the paste and
reflow process still need checking. Avoid automatic aperture changes to U1:
request the supplied paste apertures 1:1, following u-blox's starting guidance.
If the stencil supplier proposes a different thickness/aperture treatment,
review it rather than assuming an automatic change is correct.

In JLCPCB's stencil options, look for **no frame**, **customized size: Yes**,
100 × 100 mm, top only. Check the actual cut-sheet dimensions in the quote.
Choose no fiducials for manual visual alignment; the board's THT pads and holes
are not extra paste apertures. Include:

`fabrication/gerbers/nora-minimal-F_Paste.gtp`

Suggested remark: “Please follow F.Paste only, preserve the supplied apertures
1:1, and ignore differences between solder-mask and solder-paste layers.”

JLCPCB supports customized frameless sizes. Its current help says stencils up
to 280 × 280 mm can ship with PCBs, while larger ones can require a separate
parcel. This does **not** guarantee the same economy shipping option or charge:
compare your basket after choosing the small sheet, before paying. A stencil
that costs little can still increase packed dimensions and shipping charges.

Sources:
- [JLCPCB order instructions](https://jlcpcb.com/help/article/instructions-for-stencil-order)
- [JLCPCB combined PCB/stencil shipping](https://jlcpcb.com/help/article/smt-stencil-and-pcb-shipped-together)
- [JLCPCB custom frameless stencils](https://jlcpcb.com/blog/how-to-choose-a-smt-stencil/)
- [u-blox integration manual §6.9](https://content.u-blox.com/sites/default/files/NORA-B1_SIM_UBX-20027617.pdf)

## DIY options at the hackspace

A printed stencil is possible in principle, but dimensional accuracy, a flat
underside, clean openings and paste release matter more than whether the model
prints. Inspect every deposit before placing U1. Too thick a sheet deposits too
much paste and can bridge the hidden pads. A successful coarse-pitch stencil
print does not establish that this module's hidden pads can be assembled well.

For an ordinary 0.4 mm-nozzle FDM machine, a printed **board holder/alignment
jig** is the more useful first print. I would choose a small steel stencil for
the module rather than add nozzle/first-layer experiments to first-board bring-up.
Resin can make finer features, but it still needs process trials and the printer
is not currently set up. No printed stencil is qualified or supplied here.

If the hackspace has a suitably precise laser cutter, a thin laser-cut Mylar or
polyimide stencil is another prototype option; check the material and cutter
settings with the operator. Supply the paste artwork at 1:1 scale, verify its
apertures and test paste transfer on a spare bare PCB before placing a module.
An aluminium stencil cut by hand or a blob of paste over the whole module area
is a poor starting point for an 82-pad hidden-land module.

For printing paste, support the bare board flat, fix it against two edges,
align/tape the stencil, squeegee once and lift it vertically. Inspect for missing
or bridged deposits before placing parts. Reflow all SMD components in the
module's permitted reflow process; iron-solder the USB plug/headers afterwards.
