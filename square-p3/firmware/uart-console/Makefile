OUT := ../../../build/square-p3-uart-console
CFLAGS := -mcpu=cortex-m33 -mthumb -mfloat-abi=soft -Os -g3 -ffreestanding -fno-builtin -fno-unwind-tables -fno-asynchronous-unwind-tables -Wall -Wextra -Werror

.PHONY: all
all: $(OUT)/console.hex

$(OUT)/console.elf: main.c ../blinky/linker.ld
	mkdir -p $(OUT)
	arm-none-eabi-gcc $(CFLAGS) -nostdlib -Wl,--build-id=none,-Map,$(OUT)/console.map -T ../blinky/linker.ld main.c -o $@
	arm-none-eabi-size $@

$(OUT)/console.hex: $(OUT)/console.elf
	arm-none-eabi-objcopy -O ihex $< $@
