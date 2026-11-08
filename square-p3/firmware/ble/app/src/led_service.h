#ifndef NORA_LED_SERVICE_H
#define NORA_LED_SERVICE_H

#include <stdint.h>

enum led_mode { LED_OFF = 0, LED_ON = 1, LED_BLINK = 2 };
#define LED_INTERVAL_MIN_MS 50
#define LED_INTERVAL_MAX_MS 5000

struct led_state {
    uint8_t mode;
    uint8_t lit;
    uint16_t interval_ms;
};

int led_control_init(void);
int led_set_mode(uint8_t mode);
int led_set_interval(uint16_t interval_ms);
struct led_state led_snapshot(void);

#endif
