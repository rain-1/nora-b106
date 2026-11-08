/* Secure nRF5340 application core: LED + polled UART, no SDK or bootloader.
 * Register definitions checked against Nordic nrfx v3.2.0 MDK headers.
 */
#include <stdint.h>

#define REG32(address) (*(volatile uint32_t *)(address))
#define UART(offset) REG32(0x50008000u + (offset))
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

static void put_char(char value)
{
    /* EasyDMA requires a RAM source, even for strings stored in flash. */
    volatile char byte = value;
    UART(0x120) = 0; /* ENDTX */
    UART(0x544) = (uintptr_t)&byte;
    UART(0x548) = 1;
    __asm__ volatile ("dmb" ::: "memory");
    UART(0x008) = 1; /* STARTTX */
    while (!UART(0x120)) {
    }
}

static void put_string(const char *text)
{
    while (*text) {
        put_char(*text++);
    }
}

static void put_hex(uint32_t value)
{
    for (unsigned int shift = 32; shift; ) {
        shift -= 4;
        unsigned int digit = (value >> shift) & 15;
        put_char(digit < 10 ? '0' + digit : 'a' + digit - 10);
    }
}

static int equal(const char *left, const char *right)
{
    while (*left && *left == *right) {
        ++left;
        ++right;
    }
    return *left == *right;
}

void reset_handler(void)
{
    __asm__ volatile ("cpsid i");
    /* CPU-side keys must match the debugger-side reset keys on every boot. */
    REG32(0x50006544u) = 0x50fa50fau;
    REG32(0x5000654cu) = 0x50fa50fau;
    REG32(0xe000ed08u) = 0;
    REG32(0x5084250cu) = LED_BIT;
    REG32(0x50842750u) = 3; /* P0.20 output. */

    /* UART0: P0.24 TX, P1.06 RX, 115200 8N1, no flow control.
     * HFINT is sufficient for this bench test; no crystal setup is required.
     */
    REG32(0x50842508u) = 1u << 24; /* TX idle high before peripheral handover. */
    REG32(0x50842760u) = 3; /* P0.24 output. */
    REG32(0x50842f18u) = 12; /* P1.06 input, pull-up. */
    UART(0x508) = 0xffffffffu; /* RTS disconnected. */
    UART(0x50c) = 24;
    UART(0x510) = 0xffffffffu; /* CTS disconnected. */
    UART(0x514) = 32 + 6;
    UART(0x524) = 0x01d60000u;
    UART(0x56c) = 0;
    UART(0x500) = 8;

    volatile unsigned char received = 0;
    UART(0x534) = (uintptr_t)&received;
    UART(0x538) = 1;
    UART(0x200) = 1u << 5; /* ENDRX -> STARTRX, reuse single-byte buffer. */
    UART(0x110) = 0;
    __asm__ volatile ("dmb" ::: "memory");
    UART(0x000) = 1;

    /* Poll SysTick at 1 ms with the reset-default 64 MHz CPU clock. */
    REG32(0xe000e014u) = 64000 - 1;
    REG32(0xe000e018u) = 0;
    REG32(0xe000e010u) = 5; /* Processor clock, no interrupt. */
    unsigned int ticks = 0, blinking = 1, lit = 0, length = 0, overflow = 0;
    char line[32];
    put_string("\r\nNORA square-p3 UART console v1\r\n115200 8N1; type help then Enter.\r\nnora> ");
    for (;;) {
        if (REG32(0xe000e010u) & (1u << 16)) {
            if (++ticks >= 500) {
                ticks = 0;
                if (blinking) {
                    lit = !lit;
                    REG32(lit ? 0x50842508u : 0x5084250cu) = LED_BIT;
                }
            }
        }
        if (UART(0x124)) { /* Discard a malformed command after a line error. */
            UART(0x124) = 0;
            UART(0x480) = UART(0x480);
            overflow = 1;
        }
        if (!UART(0x110)) {
            continue;
        }
        unsigned char byte = received;
        UART(0x110) = 0;
        if (byte == '\r' || byte == '\n') {
            if (!length && !overflow) {
                continue; /* Ignore the LF half of CRLF. */
            }
            line[length] = 0;
            put_string("\r\n");
            if (overflow) {
                put_string("Input overflow/error; try again.\r\n");
            } else if (equal(line, "help")) {
                put_string("help  info  on  off  blink\r\n");
            } else if (equal(line, "info")) {
                put_string("NORA square-p3 UART console v1; nRF5340; ID ");
                put_hex(REG32(0x00ff0204u));
                put_char('-');
                put_hex(REG32(0x00ff0208u));
                put_string("\r\n");
            } else if (equal(line, "on") || equal(line, "off")) {
                blinking = 0;
                lit = equal(line, "on");
                REG32(lit ? 0x50842508u : 0x5084250cu) = LED_BIT;
                put_string(lit ? "LED on\r\n" : "LED off\r\n");
            } else if (equal(line, "blink")) {
                blinking = 1;
                ticks = 0;
                put_string("LED blinking\r\n");
            } else {
                put_string("Unknown command; type help.\r\n");
            }
            length = overflow = 0;
            put_string("nora> ");
        } else if (byte == 8 || byte == 127) {
            if (length) {
                --length;
            }
        } else if (byte >= 32 && byte < 127) {
            if (length < sizeof(line) - 1) {
                line[length++] = (char)byte;
            } else {
                overflow = 1;
            }
        }
    }
}
