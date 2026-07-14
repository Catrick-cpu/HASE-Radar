##############################################################################
# AERIS-10P Radar Firmware Makefile
# Target: STM32H743ZIT6 @ 480 MHz
# Toolchain: arm-none-eabi-gcc (GCC ARM Embedded, v12+)
#
# Usage:
#   make           # Build firmware (debug)
#   make release   # Build firmware (optimized, no debug info)
#   make flash     # Flash via ST-Link (requires OpenOCD or STM32CubeProgrammer)
#   make clean     # Remove build artifacts
#   make size      # Show flash/RAM usage
##############################################################################

# Project name
TARGET = AERIS_firmware

# Build directory
BUILD_DIR = build

# Target MCU
MCU = cortex-m7

# FPU
FPU = fpv5-d16
FLOAT_ABI = hard

# Toolchain prefix
CROSS_COMPILE = arm-none-eabi-
CC      = $(CROSS_COMPILE)gcc
CXX     = $(CROSS_COMPILE)g++
AS      = $(CROSS_COMPILE)gcc -x assembler-with-cpp
LD      = $(CROSS_COMPILE)gcc
OBJCOPY = $(CROSS_COMPILE)objcopy
OBJDUMP = $(CROSS_COMPILE)objdump
SIZE    = $(CROSS_COMPILE)size

##############################################################################
# Source Files
##############################################################################

# Application sources
C_SOURCES = \
  main.c \
  phase_shifter.c \
  adf4159.c \
  Drivers/STM32H7xx_HAL_Driver/Src/stm32h7xx_hal.c \
  Drivers/STM32H7xx_HAL_Driver/Src/stm32h7xx_hal_rcc.c \
  Drivers/STM32H7xx_HAL_Driver/Src/stm32h7xx_hal_rcc_ex.c \
  Drivers/STM32H7xx_HAL_Driver/Src/stm32h7xx_hal_gpio.c \
  Drivers/STM32H7xx_HAL_Driver/Src/stm32h7xx_hal_dma.c \
  Drivers/STM32H7xx_HAL_Driver/Src/stm32h7xx_hal_spi.c \
  Drivers/STM32H7xx_HAL_Driver/Src/stm32h7xx_hal_spi_ex.c \
  Drivers/STM32H7xx_HAL_Driver/Src/stm32h7xx_hal_adc.c \
  Drivers/STM32H7xx_HAL_Driver/Src/stm32h7xx_hal_adc_ex.c \
  Drivers/STM32H7xx_HAL_Driver/Src/stm32h7xx_hal_uart.c \
  Drivers/STM32H7xx_HAL_Driver/Src/stm32h7xx_hal_uart_ex.c \
  Drivers/STM32H7xx_HAL_Driver/Src/stm32h7xx_hal_pcd.c \
  Drivers/STM32H7xx_HAL_Driver/Src/stm32h7xx_hal_pcd_ex.c \
  Drivers/STM32H7xx_HAL_Driver/Src/stm32h7xx_hal_cortex.c \
  Drivers/STM32H7xx_HAL_Driver/Src/stm32h7xx_hal_pwr.c \
  Drivers/STM32H7xx_HAL_Driver/Src/stm32h7xx_hal_pwr_ex.c \
  Drivers/STM32H7xx_HAL_Driver/Src/stm32h7xx_hal_tim.c \
  Middlewares/ST/STM32_USB_Device_Library/Core/Src/usbd_core.c \
  Middlewares/ST/STM32_USB_Device_Library/Core/Src/usbd_ctlreq.c \
  Middlewares/ST/STM32_USB_Device_Library/Core/Src/usbd_ioreq.c \
  Middlewares/ST/STM32_USB_Device_Library/Class/CDC/Src/usbd_cdc.c \
  USB_DEVICE/App/usb_device.c \
  USB_DEVICE/App/usbd_cdc_if.c \
  USB_DEVICE/Target/usbd_conf.c \
  Core/Src/system_stm32h7xx.c \
  Core/Src/stm32h7xx_it.c \
  Core/Src/sysmem.c \
  Core/Src/syscalls.c

# Assembly sources (startup)
ASM_SOURCES = \
  startup_stm32h743zitx.s

##############################################################################
# Include Paths
##############################################################################

C_INCLUDES = \
  -ICore/Inc \
  -IDrivers/STM32H7xx_HAL_Driver/Inc \
  -IDrivers/STM32H7xx_HAL_Driver/Inc/Legacy \
  -IDrivers/CMSIS/Device/ST/STM32H7xx/Include \
  -IDrivers/CMSIS/Include \
  -IMiddlewares/ST/STM32_USB_Device_Library/Core/Inc \
  -IMiddlewares/ST/STM32_USB_Device_Library/Class/CDC/Inc \
  -IUSB_DEVICE/App \
  -IUSB_DEVICE/Target \
  -I.

##############################################################################
# Preprocessor Defines
##############################################################################

C_DEFS = \
  -DUSE_HAL_DRIVER \
  -DSTM32H743xx \
  -DAERIS_FIRMWARE_VERSION=\"1.0.0\"

##############################################################################
# Compiler Flags
##############################################################################

CPU = -mcpu=$(MCU) -mthumb -mfpu=$(FPU) -mfloat-abi=$(FLOAT_ABI)

# Debug build (default)
DEBUG_FLAGS = -g3 -ggdb -O1 -DDEBUG

# Release build
RELEASE_FLAGS = -O2 -DNDEBUG

# Common flags
COMMON_FLAGS = $(CPU) -Wall -Wextra -Wno-unused-parameter \
               -ffunction-sections -fdata-sections -fstack-usage \
               -MMD -MP

CFLAGS  = $(COMMON_FLAGS) $(C_DEFS) $(C_INCLUDES) $(DEBUG_FLAGS) -std=gnu11
ASFLAGS = $(CPU) -Wall -fdata-sections -ffunction-sections

##############################################################################
# Linker Configuration
##############################################################################

LDSCRIPT = STM32H743ZITx_FLASH.ld

LDFLAGS = $(CPU) \
          -specs=nano.specs \
          -T$(LDSCRIPT) \
          -Wl,--gc-sections \
          -Wl,-Map=$(BUILD_DIR)/$(TARGET).map,--cref \
          -lc -lm -lnosys

##############################################################################
# Build Objects
##############################################################################

OBJECTS  = $(addprefix $(BUILD_DIR)/,$(C_SOURCES:.c=.o))
OBJECTS += $(addprefix $(BUILD_DIR)/,$(ASM_SOURCES:.s=.o))

##############################################################################
# Targets
##############################################################################

.PHONY: all release flash flash-stm32cubeprogrammer clean size gdb

all: $(BUILD_DIR)/$(TARGET).elf $(BUILD_DIR)/$(TARGET).bin
	@echo ""
	@echo "  ====================================="
	@echo "  AERIS-10P Firmware build complete"
	@echo "  ====================================="
	$(SIZE) $(BUILD_DIR)/$(TARGET).elf

release: CFLAGS = $(COMMON_FLAGS) $(C_DEFS) $(C_INCLUDES) $(RELEASE_FLAGS) -std=gnu11
release: all

$(BUILD_DIR)/$(TARGET).elf: $(OBJECTS)
	@mkdir -p $(dir $@)
	$(LD) $(OBJECTS) $(LDFLAGS) -o $@

$(BUILD_DIR)/$(TARGET).bin: $(BUILD_DIR)/$(TARGET).elf
	$(OBJCOPY) -O binary $< $@

$(BUILD_DIR)/$(TARGET).hex: $(BUILD_DIR)/$(TARGET).elf
	$(OBJCOPY) -O ihex $< $@

$(BUILD_DIR)/%.o: %.c
	@mkdir -p $(dir $@)
	$(CC) -c $(CFLAGS) $< -o $@

$(BUILD_DIR)/%.o: %.s
	@mkdir -p $(dir $@)
	$(AS) -c $(ASFLAGS) $< -o $@

-include $(OBJECTS:.o=.d)

clean:
	rm -rf $(BUILD_DIR)
	@echo "Cleaned build directory."

size: $(BUILD_DIR)/$(TARGET).elf
	$(SIZE) --format=berkeley $<

# Flash using OpenOCD (ST-Link V2/V3)
flash: $(BUILD_DIR)/$(TARGET).bin
	openocd \
	  -f interface/stlink.cfg \
	  -f target/stm32h7x.cfg \
	  -c "program $(BUILD_DIR)/$(TARGET).bin verify reset exit 0x08000000"

# Flash using STM32CubeProgrammer CLI
flash-stm32cubeprogrammer: $(BUILD_DIR)/$(TARGET).elf
	STM32_Programmer_CLI \
	  -c port=SWD freq=4000 reset=HWrst \
	  -d $(BUILD_DIR)/$(TARGET).elf \
	  -v -hardRst

# Launch GDB session for debugging
gdb: $(BUILD_DIR)/$(TARGET).elf
	openocd -f interface/stlink.cfg -f target/stm32h7x.cfg &
	arm-none-eabi-gdb -ex "target extended-remote :3333" \
	                  -ex "monitor reset halt" \
	                  -ex "load" \
	                  -ex "monitor reset init" \
	                  $(BUILD_DIR)/$(TARGET).elf
