/* SPDX-License-Identifier: Apache-2.0 */
#include <errno.h>
#include <stdlib.h>
#include <string.h>
#include <zephyr/kernel.h>
#include <zephyr/drivers/adc.h>
#include <zephyr/drivers/gpio.h>
#include <zephyr/drivers/hwinfo.h>
#include <zephyr/retention/bootmode.h>
#include <zephyr/shell/shell.h>
#include <zephyr/sys/reboot.h>
#include <app_version.h>

#define USER DT_PATH(zephyr_user)
#define PIN_SPEC(i, ...) GPIO_DT_SPEC_GET_BY_IDX(USER, gpios, i),
static const struct gpio_dt_spec pins[] = {
    LISTIFY(DT_PROP_LEN(USER, gpios), PIN_SPEC, ())
};
static const char *const names[] = {"P0.24", "P1.06", "P0.20", "P0.07/AIN3"};
BUILD_ASSERT(ARRAY_SIZE(pins) == 4);
static const struct adc_dt_spec analog = ADC_DT_SPEC_GET(USER);

static int pin_index(const struct shell *sh, const char *arg)
{
    char *end;
    long number = strtol(arg, &end, 10);
    if (!arg[0] || *end || number < 3 || number > 6) {
        shell_error(sh, "Use a J3 GPIO pin number from 3 to 6.");
        return -EINVAL;
    }
    return (int)number - 3;
}

static int info(const struct shell *sh, size_t argc, char **argv)
{
    uint8_t id[16];
    ssize_t length = hwinfo_get_device_id(id, sizeof(id));
    ARG_UNUSED(argc); ARG_UNUSED(argv);
    shell_print(sh, "NORA-B106 Compact P2, firmware " APP_VERSION_STRING);
    shell_print(sh, "Application core only; LF clock RC; HFXO load 20 pF.");
    shell_print(sh, "Uptime: %lld ms", (long long)k_uptime_get());
    if (length > 0) {
        shell_fprintf(sh, SHELL_NORMAL, "Device ID: ");
        for (ssize_t i = 0; i < length; ++i) {
            shell_fprintf(sh, SHELL_NORMAL, "%02x", id[i]);
        }
        shell_print(sh, "");
    }
    return 0;
}

static int pinout(const struct shell *sh, size_t argc, char **argv)
{
    ARG_UNUSED(argc); ARG_UNUSED(argv);
    shell_print(sh, "J3 1=3V3, 2=GND. All GPIOs are 3.3 V only.");
    for (size_t i = 0; i < ARRAY_SIZE(pins); ++i) {
        shell_print(sh, "J3 %2u = %s", (unsigned)i + 3, names[i]);
    }
    return 0;
}

static int input(const struct shell *sh, size_t argc, char **argv)
{
    int i = pin_index(sh, argv[1]);
    gpio_flags_t flags = GPIO_INPUT;
    if (i < 0) { return i; }
    if (argc == 3) {
        if (!strcmp(argv[2], "up")) { flags |= GPIO_PULL_UP; }
        else if (!strcmp(argv[2], "down")) { flags |= GPIO_PULL_DOWN; }
        else if (strcmp(argv[2], "none")) {
            shell_error(sh, "Pull must be none, up or down.");
            return -EINVAL;
        }
    }
    int rc = gpio_pin_configure_dt(&pins[i], flags);
    if (rc) { shell_error(sh, "GPIO configure failed: %d", rc); }
    else { shell_print(sh, "J3 %d (%s) input", i + 3, names[i]); }
    return rc;
}

static int read_pin(const struct shell *sh, size_t argc, char **argv)
{
    ARG_UNUSED(argc);
    int i = pin_index(sh, argv[1]);
    if (i < 0) { return i; }
    int level = gpio_pin_get_dt(&pins[i]);
    if (level < 0) { shell_error(sh, "GPIO read failed: %d", level); return level; }
    shell_print(sh, "J3 %d (%s) = %d", i + 3, names[i], level);
    return 0;
}

static int write_pin(const struct shell *sh, size_t argc, char **argv)
{
    ARG_UNUSED(argc);
    int i = pin_index(sh, argv[1]);
    if (i < 0) { return i; }
    if (strcmp(argv[2], "0") && strcmp(argv[2], "1")) {
        shell_error(sh, "Output must be 0 or 1."); return -EINVAL;
    }
    int level = argv[2][0] - '0';
    int rc = gpio_pin_configure_dt(&pins[i], level ? GPIO_OUTPUT_ACTIVE : GPIO_OUTPUT_INACTIVE);
    if (rc) { shell_error(sh, "GPIO configure failed: %d", rc); }
    else { shell_print(sh, "J3 %d (%s) output %d", i + 3, names[i], level); }
    return rc;
}

static int read_adc(const struct shell *sh, size_t argc, char **argv)
{
    ARG_UNUSED(argc); ARG_UNUSED(argv);
    gpio_flags_t saved;
    int16_t sample;
    struct adc_sequence seq = {.buffer = &sample, .buffer_size = sizeof(sample)};
    int rc = gpio_pin_get_config_dt(&pins[3], &saved);
    if (rc) { return rc; }
    if (saved & GPIO_OUTPUT) {
        shell_error(sh, "Set J3 6 to input first: nora input 6 none"); return -EBUSY;
    }
    if (!adc_is_ready_dt(&analog)) { return -ENODEV; }
    rc = gpio_pin_configure_dt(&pins[3], GPIO_DISCONNECTED);
    if (rc) { return rc; }
    rc = adc_channel_setup_dt(&analog);
    if (!rc) { rc = adc_sequence_init_dt(&analog, &seq); }
    if (!rc) { rc = adc_read_dt(&analog, &seq); }
    int restore = gpio_pin_configure_dt(&pins[3], saved);
    if (rc || restore) {
        shell_error(sh, "ADC/read restore failed: %d/%d", rc, restore);
        return rc ? rc : restore;
    }
    int32_t mv = sample;
    rc = adc_raw_to_millivolts_dt(&analog, &mv);
    if (!rc) { shell_print(sh, "J3 6 (AIN3): %d raw, %d mV; keep input within 0..3V3", sample, (int)mv); }
    return rc;
}

static void reboot_work(struct k_work *work)
{
    ARG_UNUSED(work);
    sys_reboot(SYS_REBOOT_COLD);
}
K_WORK_DELAYABLE_DEFINE(reboot_job, reboot_work);

static int dfu(const struct shell *sh, size_t argc, char **argv)
{
    ARG_UNUSED(argc); ARG_UNUSED(argv);
    int rc = bootmode_set(BOOT_MODE_TYPE_BOOTLOADER);
    if (rc) { shell_error(sh, "Cannot request bootloader: %d", rc); return rc; }
    shell_print(sh, "Entering USB recovery; close this terminal and use usb_update.py.");
    k_work_reschedule(&reboot_job, K_MSEC(300));
    return 0;
}

static int reboot(const struct shell *sh, size_t argc, char **argv)
{
    ARG_UNUSED(argc); ARG_UNUSED(argv);
    shell_print(sh, "Rebooting; recovery window lasts 8 seconds before application starts.");
    k_work_reschedule(&reboot_job, K_MSEC(300));
    return 0;
}

SHELL_STATIC_SUBCMD_SET_CREATE(nora_commands,
    SHELL_CMD_ARG(info, NULL, "Firmware/device information", info, 1, 0),
    SHELL_CMD_ARG(pins, NULL, "J3 header pinout", pinout, 1, 0),
    SHELL_CMD_ARG(input, NULL, "<J3 pin> [none|up|down]", input, 2, 1),
    SHELL_CMD_ARG(read, NULL, "<J3 pin>", read_pin, 2, 0),
    SHELL_CMD_ARG(write, NULL, "<J3 pin> <0|1>", write_pin, 3, 0),
    SHELL_CMD_ARG(adc, NULL, "Read J3 6 / P0.07 / AIN3", read_adc, 1, 0),
    SHELL_CMD_ARG(dfu, NULL, "Enter USB firmware recovery", dfu, 1, 0),
    SHELL_CMD_ARG(reboot, NULL, "Normal reboot", reboot, 1, 0),
    SHELL_SUBCMD_SET_END
);
SHELL_CMD_REGISTER(nora, &nora_commands, "NORA-B106 bench commands", NULL);

int main(void)
{
    /* Leave all exposed GPIOs as floating inputs until explicitly commanded.
     * The shell handlers run in thread context and never touch SWD/reset pins. */
    for (size_t i = 0; i < ARRAY_SIZE(pins); ++i) {
        if (gpio_is_ready_dt(&pins[i])) {
            (void)gpio_pin_configure_dt(&pins[i], GPIO_INPUT);
        }
    }
    return 0;
}
