ENTRY(reset_handler)
MEMORY
{
    FLASH (rx) : ORIGIN = 0x00000000, LENGTH = 4K
    RAM (rw) : ORIGIN = 0x20000000, LENGTH = 64K
}
_stack_top = ORIGIN(RAM) + LENGTH(RAM);
SECTIONS
{
    .vectors : { KEEP(*(.vectors)) } > FLASH
    .text : { *(.text*) *(.rodata*) } > FLASH
    .data : { *(.data*) } > RAM AT > FLASH
    .bss (NOLOAD) : { *(.bss*) *(COMMON) } > RAM
    /DISCARD/ : { *(.comment*) *(.ARM.exidx*) *(.ARM.extab*) }
}
/* This tiny reset handler intentionally needs no C runtime initialization. */
ASSERT(SIZEOF(.data) == 0, "Initialized RAM requires startup code")
ASSERT(SIZEOF(.bss) == 0, "Zero-initialized RAM requires startup code")
