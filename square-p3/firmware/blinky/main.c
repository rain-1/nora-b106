/* Standalone secure nRF5340 application-core smoke test. No SDK required. */
#include <stdint.h>

#define REG32(address) (*(volatile uint32_t *)(address))
#define LED_BIT (1u << 20)

extern uint32_t _stack_top;
void reset_handler(void);
static void fault_handler(void);

__attribute__((section(".vectors"), used))
const uintptr_t vectors[16] = {
    (uintptr_t)&_stack_top, (uintptr_t)reset_handler,
    (uintptr_t)fault_handler, (uintptr_t)fault_handler,
    (uintptr_t)fault_handler, (uintptr_t)fault_handler,
    (uintptr_t)fault_handler, (uintptr_t)fault_handler,
    0, 0, 0, (uintptr_t)fault_handler,
    (uintptr_t)fault_handler, 0,
    (uintptr_t)fault_handler, (uintptr_t)fault_handler,
};

static void fault_handler(void)
{
    for (;;) {
        __asm__ volatile ("nop");
    }
}

/* Deliberately approximate timing; no crystal/clock setup is needed. */
static void delay(void)
{
    for (volatile uint32_t count = 0; count < 4000000u; ++count) {
        __asm__ volatile ("nop");
    }
}

void reset_handler(void)
{
    __asm__ volatile ("cpsid i");
    /* Keep secure/non-secure SWD open after power-on; no UICR writes. */
    REG32(0x50006544u) = 0x50fa50fau;
    REG32(0x5000654cu) = 0x50fa50fau;
    REG32(0xe000ed08u) = 0; /* Secure vector table at application flash base. */
    REG32(0x5084250cu) = LED_BIT; /* P0 OUTCLR. */
    REG32(0x50842750u) = 3; /* P0.20: output, input disconnected, standard drive. */
    for (;;) {
        REG32(0x50842508u) = LED_BIT; /* OUTSET. */
        delay();
        REG32(0x5084250cu) = LED_BIT;
        delay();
    }
}
