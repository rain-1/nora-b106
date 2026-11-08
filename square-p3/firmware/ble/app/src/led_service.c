#include "led_service.h"

#include <errno.h>
#include <zephyr/kernel.h>
#include <zephyr/bluetooth/gatt.h>
#include <zephyr/drivers/gpio.h>
#include <zephyr/sys/byteorder.h>

/* Service ...0001; mode ...0002; interval ...0003; status ...0004. */
#define LED_UUID(number) BT_UUID_128_ENCODE(0x7b1e0000u + (number), 0x8e2f, 0x4f4a, 0x9d6c, 0x3a5b7c9d0100)
static const struct bt_uuid_128 service_uuid = BT_UUID_INIT_128(LED_UUID(1));
static const struct bt_uuid_128 mode_uuid = BT_UUID_INIT_128(LED_UUID(2));
static const struct bt_uuid_128 interval_uuid = BT_UUID_INIT_128(LED_UUID(3));
static const struct bt_uuid_128 state_uuid = BT_UUID_INIT_128(LED_UUID(4));

static const struct gpio_dt_spec led = GPIO_DT_SPEC_GET(DT_ALIAS(led0), gpios);
static struct k_work_delayable led_work;
static K_MUTEX_DEFINE(led_lock);
static struct led_state state = { .mode = LED_BLINK, .interval_ms = 500 };
static bool ready;

static int apply_output(uint8_t lit)
{
    int err = gpio_pin_set_dt(&led, lit);
    if (!err) {
        state.lit = lit;
    }
    return err;
}

static void update_led(struct k_work *work)
{
    ARG_UNUSED(work);
    k_mutex_lock(&led_lock, K_FOREVER);
    if (state.mode == LED_BLINK) {
        apply_output(!state.lit);
        k_work_reschedule(&led_work, K_MSEC(state.interval_ms));
    }
    k_mutex_unlock(&led_lock);
}

int led_control_init(void)
{
    if (!gpio_is_ready_dt(&led)) {
        return -ENODEV;
    }
    int err = gpio_pin_configure_dt(&led, GPIO_OUTPUT_INACTIVE);
    if (err) {
        return err;
    }
    k_mutex_lock(&led_lock, K_FOREVER);
    k_work_init_delayable(&led_work, update_led);
    ready = true;
    k_work_reschedule(&led_work, K_NO_WAIT);
    k_mutex_unlock(&led_lock);
    return 0;
}

int led_set_mode(uint8_t mode)
{
    if (mode > LED_BLINK) {
        return -EINVAL;
    }
    k_mutex_lock(&led_lock, K_FOREVER);
    int err = ready ? 0 : -EAGAIN;
    if (!err) {
        err = apply_output(mode != LED_OFF);
    }
    if (!err) {
        state.mode = mode;
        if (mode == LED_BLINK) {
            k_work_reschedule(&led_work, K_MSEC(state.interval_ms));
        } else {
            /* A callback already waiting on the mutex will see the new mode. */
            k_work_cancel_delayable(&led_work);
        }
    }
    k_mutex_unlock(&led_lock);
    return err;
}

int led_set_interval(uint16_t interval_ms)
{
    if (interval_ms < LED_INTERVAL_MIN_MS || interval_ms > LED_INTERVAL_MAX_MS) {
        return -EINVAL;
    }
    k_mutex_lock(&led_lock, K_FOREVER);
    if (!ready) {
        k_mutex_unlock(&led_lock);
        return -EAGAIN;
    }
    state.interval_ms = interval_ms;
    if (state.mode == LED_BLINK) {
        k_work_reschedule(&led_work, K_MSEC(interval_ms));
    }
    k_mutex_unlock(&led_lock);
    return 0;
}

struct led_state led_snapshot(void)
{
    k_mutex_lock(&led_lock, K_FOREVER);
    struct led_state snapshot = state;
    k_mutex_unlock(&led_lock);
    return snapshot;
}

static ssize_t read_mode(struct bt_conn *conn, const struct bt_gatt_attr *attr,
                         void *buf, uint16_t len, uint16_t offset)
{
    struct led_state snapshot = led_snapshot();
    return bt_gatt_attr_read(conn, attr, buf, len, offset, &snapshot.mode, 1);
}

static ssize_t read_interval(struct bt_conn *conn, const struct bt_gatt_attr *attr,
                             void *buf, uint16_t len, uint16_t offset)
{
    uint8_t value[2];
    sys_put_le16(led_snapshot().interval_ms, value);
    return bt_gatt_attr_read(conn, attr, buf, len, offset, value, sizeof(value));
}

static ssize_t read_state(struct bt_conn *conn, const struct bt_gatt_attr *attr,
                          void *buf, uint16_t len, uint16_t offset)
{
    struct led_state snapshot = led_snapshot();
    uint8_t value[4] = { snapshot.mode, snapshot.lit };
    sys_put_le16(snapshot.interval_ms, &value[2]);
    return bt_gatt_attr_read(conn, attr, buf, len, offset, value, sizeof(value));
}

static ssize_t write_mode(struct bt_conn *conn, const struct bt_gatt_attr *attr,
                          const void *buf, uint16_t len, uint16_t offset, uint8_t flags)
{
    ARG_UNUSED(conn); ARG_UNUSED(attr); ARG_UNUSED(flags);
    if (offset) {
        return BT_GATT_ERR(BT_ATT_ERR_INVALID_OFFSET);
    }
    if (len != 1) {
        return BT_GATT_ERR(BT_ATT_ERR_INVALID_ATTRIBUTE_LEN);
    }
    uint8_t mode = *(const uint8_t *)buf;
    if (mode > LED_BLINK) {
        return BT_GATT_ERR(BT_ATT_ERR_VALUE_NOT_ALLOWED);
    }
    if (led_set_mode(mode)) {
        return BT_GATT_ERR(BT_ATT_ERR_UNLIKELY);
    }
    printk("BLE LED mode=%u\n", mode);
    return len;
}

static ssize_t write_interval(struct bt_conn *conn, const struct bt_gatt_attr *attr,
                              const void *buf, uint16_t len, uint16_t offset, uint8_t flags)
{
    ARG_UNUSED(conn); ARG_UNUSED(attr); ARG_UNUSED(flags);
    if (offset) {
        return BT_GATT_ERR(BT_ATT_ERR_INVALID_OFFSET);
    }
    if (len != 2) {
        return BT_GATT_ERR(BT_ATT_ERR_INVALID_ATTRIBUTE_LEN);
    }
    uint16_t interval_ms = sys_get_le16(buf);
    if (interval_ms < LED_INTERVAL_MIN_MS || interval_ms > LED_INTERVAL_MAX_MS) {
        return BT_GATT_ERR(BT_ATT_ERR_VALUE_NOT_ALLOWED);
    }
    if (led_set_interval(interval_ms)) {
        return BT_GATT_ERR(BT_ATT_ERR_UNLIKELY);
    }
    printk("BLE LED interval=%u ms\n", interval_ms);
    return len;
}

BT_GATT_SERVICE_DEFINE(led_service,
    BT_GATT_PRIMARY_SERVICE(&service_uuid),
    BT_GATT_CHARACTERISTIC(&mode_uuid.uuid, BT_GATT_CHRC_READ | BT_GATT_CHRC_WRITE,
        BT_GATT_PERM_READ | BT_GATT_PERM_WRITE, read_mode, write_mode, NULL),
    BT_GATT_CUD("LED mode: 00 off, 01 on, 02 blink", BT_GATT_PERM_READ),
    BT_GATT_CHARACTERISTIC(&interval_uuid.uuid, BT_GATT_CHRC_READ | BT_GATT_CHRC_WRITE,
        BT_GATT_PERM_READ | BT_GATT_PERM_WRITE, read_interval, write_interval, NULL),
    BT_GATT_CUD("Blink interval ms: uint16 little-endian, 50..5000", BT_GATT_PERM_READ),
    BT_GATT_CHARACTERISTIC(&state_uuid.uuid, BT_GATT_CHRC_READ,
        BT_GATT_PERM_READ, read_state, NULL, NULL),
    BT_GATT_CUD("State: mode, lit, interval low byte, interval high byte", BT_GATT_PERM_READ)
);
