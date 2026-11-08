#include <zephyr/kernel.h>
#include <errno.h>
#include <zephyr/bluetooth/bluetooth.h>
#include <zephyr/bluetooth/conn.h>
#include <zephyr/shell/shell.h>
#include <zephyr/shell/shell_string_conv.h>
#include <zephyr/sys/atomic.h>
#include <stdio.h>
#include <string.h>
#include <hal/nrf_ficr.h>
#include "led_service.h"
#if defined(CONFIG_MCUMGR_TRANSPORT_BT)
#include <zephyr/mgmt/mcumgr/transport/smp_bt.h>
#endif

#ifndef NORA_FIRMWARE_VERSION
#define NORA_FIRMWARE_VERSION "LED-v2"
#endif

static atomic_t advertising;
static atomic_t connected;
static atomic_t bluetooth_ready;
static struct k_work_delayable advertising_work;
static char device_name[24];

static int start_advertising(void)
{
    const struct bt_data data[] = {
        BT_DATA_BYTES(BT_DATA_FLAGS, BT_LE_AD_GENERAL | BT_LE_AD_NO_BREDR),
#if defined(CONFIG_MCUMGR_TRANSPORT_BT)
        BT_DATA_BYTES(BT_DATA_UUID128_ALL, SMP_BT_SVC_UUID_VAL),
#else
        BT_DATA(BT_DATA_NAME_COMPLETE, device_name, strlen(device_name)),
#endif
    };
#if defined(CONFIG_MCUMGR_TRANSPORT_BT)
    const struct bt_data scan_response[] = {
        BT_DATA(BT_DATA_NAME_COMPLETE, device_name, strlen(device_name)),
    };
#endif
    int err = bt_le_adv_start(BT_LE_ADV_PARAM(BT_LE_ADV_OPT_CONN | BT_LE_ADV_OPT_USE_IDENTITY,
        BT_GAP_ADV_FAST_INT_MIN_2, BT_GAP_ADV_FAST_INT_MAX_2, NULL),
        data, ARRAY_SIZE(data),
#if defined(CONFIG_MCUMGR_TRANSPORT_BT)
        scan_response, ARRAY_SIZE(scan_response));
#else
        NULL, 0);
#endif
    if (!err || err == -EALREADY) {
        atomic_set(&advertising, 1);
        printk("Advertising as %s; connect for LED control\n", device_name);
        return 0;
    }
    return err;
}

static void restart_advertising(struct k_work *work)
{
    ARG_UNUSED(work);
    if (atomic_get(&connected) || !atomic_get(&bluetooth_ready)) {
        return;
    }
    int err = start_advertising();
    if (err) {
        printk("Advertising restart pending (%d)\n", err);
        k_work_reschedule(&advertising_work, K_MSEC(500));
    }
}

static void on_connected(struct bt_conn *conn, uint8_t err)
{
    ARG_UNUSED(conn);
    atomic_set(&advertising, 0);
    if (err) {
        printk("Bluetooth connection failed (%u)\n", err);
        return;
    }
    atomic_set(&connected, 1);
    printk("Bluetooth connected; LED service ready\n");
}

static void on_disconnected(struct bt_conn *conn, uint8_t reason)
{
    ARG_UNUSED(conn);
    atomic_set(&connected, 0);
    printk("Bluetooth disconnected (%u)\n", reason);
}

static void on_recycled(void)
{
    /* A connection object is free again: it is now safe to advertise. */
    if (atomic_get(&bluetooth_ready)) {
        k_work_reschedule(&advertising_work, K_NO_WAIT);
    }
}

BT_CONN_CB_DEFINE(connection_callbacks) = {
    .connected = on_connected,
    .disconnected = on_disconnected,
    .recycled = on_recycled,
};

static int cmd_info(const struct shell *sh, size_t argc, char **argv)
{
    ARG_UNUSED(argc); ARG_UNUSED(argv);
    shell_print(sh, "NORA Dragon BLE v2; ID %08x-%08x", NRF_FICR->INFO.DEVICEID[0],
                NRF_FICR->INFO.DEVICEID[1]);
    shell_print(sh, "Firmware version: %s", NORA_FIRMWARE_VERSION);
    shell_print(sh, "Name: %s; advertising: %s", device_name,
                atomic_get(&advertising) ? "active" : "not active");
    shell_print(sh, "Connection: %s; LED service: 7b1e0001-8e2f-4f4a-9d6c-3a5b7c9d0100",
                atomic_get(&connected) ? "connected" : "disconnected");
    bt_addr_le_t addresses[CONFIG_BT_ID_MAX];
    size_t count = ARRAY_SIZE(addresses);
    bt_id_get(addresses, &count);
    if (count) {
        char text[BT_ADDR_LE_STR_LEN];
        bt_addr_le_to_str(&addresses[0], text, sizeof(text));
        shell_print(sh, "Bluetooth identity: %s", text);
    }
    return 0;
}

static int cmd_led(const struct shell *sh, size_t argc, char **argv)
{
    ARG_UNUSED(argc);
    int mode = !strcmp(argv[0], "on") ? LED_ON : !strcmp(argv[0], "off") ? LED_OFF : LED_BLINK;
    int err = led_set_mode(mode);
    if (err) {
        shell_error(sh, "LED unavailable (%d)", err);
        return err;
    }
    shell_print(sh, "LED %s", mode == LED_ON ? "on" : mode == LED_OFF ? "off" : "blinking");
    return 0;
}

static int cmd_state(const struct shell *sh, size_t argc, char **argv)
{
    ARG_UNUSED(argc); ARG_UNUSED(argv);
    struct led_state state = led_snapshot();
    shell_print(sh, "LED mode=%u lit=%u interval=%u ms", state.mode, state.lit, state.interval_ms);
    return 0;
}

static int cmd_interval(const struct shell *sh, size_t argc, char **argv)
{
    ARG_UNUSED(argc);
    int err = 0;
    unsigned long interval = shell_strtoul(argv[1], 10, &err);
    if (err || interval < LED_INTERVAL_MIN_MS || interval > LED_INTERVAL_MAX_MS) {
        shell_error(sh, "Interval must be 50..5000 ms");
        return -EINVAL;
    }
    err = led_set_interval((uint16_t)interval);
    if (err) {
        shell_error(sh, "LED unavailable (%d)", err);
        return err;
    }
    shell_print(sh, "LED interval=%lu ms", interval);
    return 0;
}

SHELL_CMD_REGISTER(info, NULL, "Show board ID and Bluetooth status", cmd_info);
SHELL_CMD_REGISTER(on, NULL, "Turn test LED on", cmd_led);
SHELL_CMD_REGISTER(off, NULL, "Turn test LED off", cmd_led);
SHELL_CMD_REGISTER(blink, NULL, "Blink test LED", cmd_led);
SHELL_CMD_REGISTER(state, NULL, "Read LED mode, output and interval", cmd_state);
SHELL_CMD_ARG_REGISTER(interval, NULL, "Set blink interval: interval 50..5000", cmd_interval, 2, 0);

int main(void)
{
    if (led_control_init()) {
        printk("ERROR: LED GPIO unavailable\n");
        return -1;
    }
    k_work_init_delayable(&advertising_work, restart_advertising);
    snprintf(device_name, sizeof(device_name), "NORA Dragon %04X",
             (unsigned int)(NRF_FICR->INFO.DEVICEID[0] & 0xffff));
    printk("NORA Dragon BLE: starting host and network controller\n");
    int err = bt_enable(NULL);
    if (err) {
        printk("ERROR: Bluetooth initialization failed (%d)\n", err);
        return err;
    }
    err = bt_set_name(device_name);
    if (err) {
        printk("ERROR: Bluetooth name failed (%d)\n", err);
        return err;
    }
    atomic_set(&bluetooth_ready, 1);
    err = start_advertising();
    if (err) {
        printk("ERROR: Advertising failed (%d)\n", err);
        k_work_reschedule(&advertising_work, K_MSEC(500));
    }
    printk("UART commands: info, on, off, blink, interval <ms>, state\n");
    return 0;
}
