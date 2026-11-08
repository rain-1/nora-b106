#include <zephyr/kernel.h>
#include <zephyr/dfu/mcuboot.h>
#include <zephyr/shell/shell.h>
#include <zephyr/storage/flash_map.h>
#include <zephyr/sys/reboot.h>

static int cmd_bootstatus(const struct shell *sh, size_t argc, char **argv)
{
    ARG_UNUSED(argc); ARG_UNUSED(argv);
    shell_print(sh, "OTA firmware %s; confirmed=%s; primary=0x%x secondary=0x%x",
                NORA_FIRMWARE_VERSION, boot_is_img_confirmed() ? "yes" : "no",
                DT_REG_ADDR(DT_NODELABEL(slot0_partition)), DT_REG_ADDR(DT_NODELABEL(slot1_partition)));
    return 0;
}

static int cmd_confirm(const struct shell *sh, size_t argc, char **argv)
{
    ARG_UNUSED(argc); ARG_UNUSED(argv);
    int err = boot_write_img_confirmed();
    if (err) {
        shell_error(sh, "Confirmation failed (%d)", err);
    } else {
        shell_print(sh, "Running image confirmed");
    }
    return err;
}

static int cmd_reboot(const struct shell *sh, size_t argc, char **argv)
{
    ARG_UNUSED(argc); ARG_UNUSED(argv);
    shell_print(sh, "Rebooting through MCUboot");
    k_msleep(50);
    sys_reboot(SYS_REBOOT_COLD);
    return 0;
}

SHELL_CMD_REGISTER(bootstatus, NULL, "Show OTA version and confirmation state", cmd_bootstatus);
SHELL_CMD_REGISTER(confirm, NULL, "Confirm the running test image", cmd_confirm);
SHELL_CMD_REGISTER(reboot, NULL, "Reboot through MCUboot", cmd_reboot);

static int cmd_otatest(const struct shell *sh, size_t argc, char **argv)
{
    ARG_UNUSED(argc); ARG_UNUSED(argv);
    int err = boot_request_upgrade(BOOT_UPGRADE_TEST);
    if (err) {
        shell_error(sh, "Test request failed (%d)", err);
    } else {
        shell_print(sh, "Secondary image requested for test; reboot to try it");
    }
    return err;
}
SHELL_CMD_REGISTER(otatest, NULL, "Request one test boot of an already staged image", cmd_otatest);
