OUT := ../../../build/square-p3-blinky
CFLAGS := -mcpu=cortex-m33 -mthumb -mfloat-abi=soft -Os -g3 -ffreestanding -fno-builtin -fno-unwind-tables -fno-asynchronous-unwind-tables -Wall -Wextra -Werror

.PHONY: all
all: $(OUT)/blinky.hex

$(OUT)/blinky.elf: main.c linker.ld
	mkdir -p $(OUT)
	arm-none-eabi-gcc $(CFLAGS) -nostdlib -Wl,--build-id=none,-Map,$(OUT)/blinky.map -T linker.ld main.c -o $@
	arm-none-eabi-size $@

$(OUT)/blinky.hex: $(OUT)/blinky.elf
	arm-none-eabi-objcopy -O ihex $< $@
