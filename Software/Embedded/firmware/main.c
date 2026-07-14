/**
 * @file main.c
 * @brief AERIS-10P Radar Main Firmware — STM32H743ZIT6
 *
 * System:  480 MHz Cortex-M7, FPU, ICACHE/DCACHE enabled
 * Purpose: FMCW chirp generation, phased array control, ADC acquisition, USB data streaming
 *
 * Build with: make all  (see Makefile)
 * Flash with: make flash (requires ST-Link V3 or STLINK-V2)
 *
 * USB CDC-ACM protocol:
 *   Packet: [0xAA][0x55][uint16 len][uint8 cmd][payload][uint8 checksum]
 *   Commands:
 *     0x01 PING -> 0x02 PONG (connectivity test)
 *     0x10 SET_BEAM [float az][float el] -> sets beam steering
 *     0x11 SET_CHIRP [uint64 f_start][uint64 f_stop][uint32 t_us]
 *     0x20 START_CAPTURE [uint32 n_samples] -> streams ADC data
 *     0x21 DATA_PACKET [uint32 seq][uint16[] samples] (sent by firmware)
 *     0x30 GET_STATUS -> 0x31 STATUS [uint8 flags][float az][float el][float tx_pwr_dbm]
 *     0x40 SET_PA_ENABLE [uint8 en] -> enable/disable PA
 *     0x50 REBOOT -> software reset
 */

#include "stm32h7xx_hal.h"
#include "usb_device.h"
#include "usbd_cdc_if.h"
#include "phase_shifter.h"
#include "adf4159.h"
#include <string.h>
#include <stdio.h>
#include <math.h>

/* ─────────────────────────────────────────────────────────────────── */
/* Defines & Constants                                                   */
/* ─────────────────────────────────────────────────────────────────── */

#define FIRMWARE_VERSION        "1.0.0"
#define ADC_BUFFER_SIZE         8192        /* samples per capture (1 s at 8 kSPS) */
#define USB_PACKET_HEADER_LEN  5
#define USB_TX_BUF_SIZE        512
#define TEMP_SHUTDOWN_CELSIUS  70.0f
#define PA_ENABLE_GPIO_PORT    GPIOC
#define PA_ENABLE_GPIO_PIN     GPIO_PIN_0
#define LNA_ENABLE_GPIO_PORT   GPIOC
#define LNA_ENABLE_GPIO_PIN    GPIO_PIN_1
#define LED_OK_GPIO_PORT       GPIOC
#define LED_OK_GPIO_PIN        GPIO_PIN_3
#define LED_TX_GPIO_PORT       GPIOC
#define LED_TX_GPIO_PIN        GPIO_PIN_4

/* USB protocol commands */
#define CMD_PING               0x01
#define CMD_PONG               0x02
#define CMD_SET_BEAM           0x10
#define CMD_SET_CHIRP          0x11
#define CMD_START_CAPTURE      0x20
#define CMD_DATA_PACKET        0x21
#define CMD_GET_STATUS         0x30
#define CMD_STATUS             0x31
#define CMD_SET_PA_ENABLE      0x40
#define CMD_REBOOT             0x50

/* ─────────────────────────────────────────────────────────────────── */
/* Global Handles and State                                              */
/* ─────────────────────────────────────────────────────────────────── */

extern SPI_HandleTypeDef hspi1;   /* TX phase shifter bus */
extern SPI_HandleTypeDef hspi2;   /* RX phase shifter bus */
extern SPI_HandleTypeDef hspi3;   /* ADF4159 PLL */
extern SPI_HandleTypeDef hspi4;   /* ADS8661 ADC */
extern ADC_HandleTypeDef hadc1;   /* Internal ADC for temperature monitor */

static PS_System_t   ps_sys;
static ADF4159_Config_t pll_cfg;

static uint16_t adc_buffer[ADC_BUFFER_SIZE];
static volatile uint32_t adc_sample_count = 0;
static volatile bool capture_active = false;
static volatile bool pa_enabled = false;
static float current_az_deg = 0.0f;
static float current_el_deg = 0.0f;
static float pa_heatsink_temp_c = 25.0f;

/* USB transmit buffer */
static uint8_t usb_tx_buf[USB_TX_BUF_SIZE];

/* ─────────────────────────────────────────────────────────────────── */
/* Private Function Prototypes                                           */
/* ─────────────────────────────────────────────────────────────────── */

static void System_Init(void);
static void Process_USB_Command(uint8_t *data, uint16_t len);
static void Send_USB_Packet(uint8_t cmd, const uint8_t *payload, uint16_t payload_len);
static uint8_t Compute_Checksum(const uint8_t *data, uint16_t len);
static void Read_Heatsink_Temperature(void);
static void Handle_Overtemperature(void);
static uint16_t ADC_ReadSingleSample(void);
static void Start_ADC_Capture(uint32_t n_samples);
static void LED_OK_Toggle(void);

/* ─────────────────────────────────────────────────────────────────── */
/* Main Entry Point                                                      */
/* ─────────────────────────────────────────────────────────────────── */

int main(void) {
    HAL_Init();
    SystemClock_Config();  /* Configure 480 MHz PLL from 25 MHz HSE */

    /* Enable DWT cycle counter for microsecond timing */
    CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
    DWT->CYCCNT = 0;
    DWT->CTRL  |= DWT_CTRL_CYCCNTENA_Msk;

    /* Enable I/D cache for performance */
    SCB_EnableICache();
    SCB_EnableDCache();

    /* Initialize HAL peripherals */
    MX_GPIO_Init();
    MX_DMA_Init();
    MX_SPI1_Init();   /* TX phase shifters: CPOL=0 CPHA=0, 10 MHz */
    MX_SPI2_Init();   /* RX phase shifters: same */
    MX_SPI3_Init();   /* ADF4159: 1 MHz */
    MX_SPI4_Init();   /* ADS8661 ADC: 1 MHz */
    MX_ADC1_Init();   /* Internal temperature / NTC */
    MX_USB_DEVICE_Init();
    MX_USART1_UART_Init();  /* Debug UART 115200 */

    /* System initialization: PLL, phase shifters, default beam */
    System_Init();

    printf("AERIS-10P Firmware v%s ready.\r\n", FIRMWARE_VERSION);
    printf("STM32H743 @ 480 MHz, USB CDC ready.\r\n");

    uint32_t tick_1hz = HAL_GetTick();
    uint32_t tick_led = HAL_GetTick();
    uint32_t tick_temp = HAL_GetTick();

    while (1) {
        uint32_t now = HAL_GetTick();

        /* 1 Hz tasks */
        if (now - tick_1hz >= 1000) {
            tick_1hz = now;
            Read_Heatsink_Temperature();
            if (pa_heatsink_temp_c > TEMP_SHUTDOWN_CELSIUS) {
                Handle_Overtemperature();
            }
        }

        /* LED heartbeat at 0.5 Hz (blink every 1000 ms) */
        if (now - tick_led >= 1000) {
            tick_led = now;
            LED_OK_Toggle();
        }

        /* ADC capture: if active, collect samples and send via USB */
        if (capture_active && adc_sample_count < ADC_BUFFER_SIZE) {
            adc_buffer[adc_sample_count++] = ADC_ReadSingleSample();
            if (adc_sample_count >= ADC_BUFFER_SIZE) {
                /* Send complete buffer as DATA_PACKET */
                uint8_t hdr[4];
                hdr[0] = (adc_sample_count >> 24) & 0xFF;
                hdr[1] = (adc_sample_count >> 16) & 0xFF;
                hdr[2] = (adc_sample_count >>  8) & 0xFF;
                hdr[3] = (adc_sample_count      ) & 0xFF;
                /* Send in chunks (USB FS max packet = 64 bytes) */
                /* TODO: implement chunked USB transfer */
                capture_active = false;
                HAL_GPIO_WritePin(LED_TX_GPIO_PORT, LED_TX_GPIO_PIN, GPIO_PIN_RESET);
            }
        }

        /* USB receive handled by callback CDC_Receive_FS in usbd_cdc_if.c */
        /* which calls Process_USB_Command */
    }
}

/* ─────────────────────────────────────────────────────────────────── */
/* System Initialization                                                 */
/* ─────────────────────────────────────────────────────────────────── */

static void System_Init(void) {
    /* 1. Initialize ADF4159 FMCW PLL */
    ADF4159_Error_t pll_err = ADF4159_Init(&pll_cfg, &hspi3);
    if (pll_err == ADF4159_OK) {
        printf("ADF4159 initialized. Chirp: %.3f-%.3f GHz in %lu us\r\n",
               (double)pll_cfg.freq_start_hz / 1e9,
               (double)pll_cfg.freq_stop_hz  / 1e9,
               (unsigned long)pll_cfg.chirp_time_us);
    } else {
        printf("ADF4159 init FAILED (err=%d)\r\n", pll_err);
    }

    /* 2. Initialize phase shifter arrays */
    PS_Error_t ps_err = PS_Init(&ps_sys, &hspi1, &hspi2);
    if (ps_err == PS_OK) {
        printf("Phase shifters initialized. Broadside beam set.\r\n");
    } else {
        printf("Phase shifter init FAILED (err=%d)\r\n", ps_err);
    }

    /* 3. Enable LNA bias (but NOT PA yet — PA requires explicit enable command) */
    HAL_GPIO_WritePin(LNA_ENABLE_GPIO_PORT, LNA_ENABLE_GPIO_PIN, GPIO_PIN_SET);
    printf("LNA enabled.\r\n");

    /* 4. PA disabled by default (safety) */
    HAL_GPIO_WritePin(PA_ENABLE_GPIO_PORT, PA_ENABLE_GPIO_PIN, GPIO_PIN_RESET);
    pa_enabled = false;
    printf("PA disabled (use CMD_SET_PA_ENABLE to enable).\r\n");

    /* 5. Enable FMCW ramp */
    ADF4159_EnableRamp(&hspi3);
    printf("FMCW ramp enabled.\r\n");

    /* 6. OK LED on */
    HAL_GPIO_WritePin(LED_OK_GPIO_PORT, LED_OK_GPIO_PIN, GPIO_PIN_SET);
}

/* ─────────────────────────────────────────────────────────────────── */
/* USB Command Processing                                                */
/* Called from USB CDC receive callback                                  */
/* ─────────────────────────────────────────────────────────────────── */

static void Process_USB_Command(uint8_t *data, uint16_t len) {
    if (len < USB_PACKET_HEADER_LEN) return;

    /* Verify header magic */
    if (data[0] != 0xAA || data[1] != 0x55) return;

    uint16_t payload_len = ((uint16_t)data[2] << 8) | data[3];
    uint8_t  cmd = data[4];

    if (len < (uint16_t)(5 + payload_len + 1)) return;  /* too short */

    uint8_t  *payload   = &data[5];
    uint8_t  rx_cksum   = data[5 + payload_len];
    uint8_t  calc_cksum = Compute_Checksum(data, 5 + payload_len);
    if (rx_cksum != calc_cksum) return;  /* checksum mismatch */

    switch (cmd) {
        case CMD_PING:
            Send_USB_Packet(CMD_PONG, NULL, 0);
            break;

        case CMD_SET_BEAM: {
            /* payload: [float32 az_deg][float32 el_deg] (8 bytes) */
            if (payload_len < 8) break;
            float az, el;
            memcpy(&az, &payload[0], 4);
            memcpy(&el, &payload[4], 4);
            PS_SetSteering(&ps_sys, az, el);
            current_az_deg = az;
            current_el_deg = el;
            printf("Beam -> az=%.1f el=%.1f\r\n", (double)az, (double)el);
            break;
        }

        case CMD_SET_CHIRP: {
            /* payload: [uint64 f_start][uint64 f_stop][uint32 t_us] (20 bytes) */
            if (payload_len < 20) break;
            uint64_t f_start, f_stop;
            uint32_t t_us;
            memcpy(&f_start, &payload[0],  8);
            memcpy(&f_stop,  &payload[8],  8);
            memcpy(&t_us,    &payload[16], 4);
            ADF4159_SetChirp(&pll_cfg, f_start, f_stop, t_us, &hspi3);
            ADF4159_EnableRamp(&hspi3);
            printf("Chirp: %.3f-%.3f GHz, %lu us\r\n",
                   (double)f_start/1e9, (double)f_stop/1e9, (unsigned long)t_us);
            break;
        }

        case CMD_START_CAPTURE: {
            /* payload: [uint32 n_samples] (4 bytes) */
            if (payload_len < 4) break;
            uint32_t n;
            memcpy(&n, &payload[0], 4);
            Start_ADC_Capture(n);
            break;
        }

        case CMD_GET_STATUS: {
            uint8_t status_payload[13];
            uint8_t flags = pa_enabled ? 0x01 : 0x00;
            if (ADF4159_IsLocked()) flags |= 0x02;
            status_payload[0] = flags;
            memcpy(&status_payload[1], &current_az_deg, 4);
            memcpy(&status_payload[5], &current_el_deg, 4);
            memcpy(&status_payload[9], &pa_heatsink_temp_c, 4);
            Send_USB_Packet(CMD_STATUS, status_payload, 13);
            break;
        }

        case CMD_SET_PA_ENABLE: {
            if (payload_len < 1) break;
            pa_enabled = (payload[0] != 0);
            HAL_GPIO_WritePin(PA_ENABLE_GPIO_PORT, PA_ENABLE_GPIO_PIN,
                              pa_enabled ? GPIO_PIN_SET : GPIO_PIN_RESET);
            HAL_GPIO_WritePin(LED_TX_GPIO_PORT, LED_TX_GPIO_PIN,
                              pa_enabled ? GPIO_PIN_SET : GPIO_PIN_RESET);
            printf("PA %s\r\n", pa_enabled ? "ENABLED" : "disabled");
            break;
        }

        case CMD_REBOOT:
            HAL_Delay(100);
            NVIC_SystemReset();
            break;

        default:
            printf("Unknown CMD 0x%02X\r\n", cmd);
            break;
    }
}

/* ─────────────────────────────────────────────────────────────────── */
/* USB Packet Transmission                                               */
/* ─────────────────────────────────────────────────────────────────── */

static void Send_USB_Packet(uint8_t cmd, const uint8_t *payload, uint16_t payload_len) {
    if (2 + payload_len + 1 > USB_TX_BUF_SIZE) return;

    usb_tx_buf[0] = 0xAA;
    usb_tx_buf[1] = 0x55;
    usb_tx_buf[2] = (payload_len >> 8) & 0xFF;
    usb_tx_buf[3] = (payload_len     ) & 0xFF;
    usb_tx_buf[4] = cmd;
    if (payload && payload_len > 0) {
        memcpy(&usb_tx_buf[5], payload, payload_len);
    }
    uint8_t cksum = Compute_Checksum(usb_tx_buf, 5 + payload_len);
    usb_tx_buf[5 + payload_len] = cksum;

    CDC_Transmit_FS(usb_tx_buf, 5 + payload_len + 1);
}

/* ─────────────────────────────────────────────────────────────────── */
/* Checksum: XOR of all bytes                                            */
/* ─────────────────────────────────────────────────────────────────── */

static uint8_t Compute_Checksum(const uint8_t *data, uint16_t len) {
    uint8_t cksum = 0;
    for (uint16_t i = 0; i < len; i++) cksum ^= data[i];
    return cksum;
}

/* ─────────────────────────────────────────────────────────────────── */
/* Temperature Monitoring (NTC on PA heatsink via STM32 ADC)            */
/* ─────────────────────────────────────────────────────────────────── */

static void Read_Heatsink_Temperature(void) {
    /* TODO: read NTC thermistor via ADC1 channel */
    /* NTC: 10kOhm at 25°C, B=3950K */
    /* Simple approximation: ADC_raw -> voltage -> resistance -> temperature */
    /* For now: placeholder */
    pa_heatsink_temp_c = 30.0f;  /* Replace with actual NTC calculation */
}

static void Handle_Overtemperature(void) {
    /* Emergency shutdown: disable PA */
    HAL_GPIO_WritePin(PA_ENABLE_GPIO_PORT, PA_ENABLE_GPIO_PIN, GPIO_PIN_RESET);
    pa_enabled = false;
    HAL_GPIO_WritePin(LED_TX_GPIO_PORT, LED_TX_GPIO_PIN, GPIO_PIN_RESET);
    printf("OVERTEMP: PA disabled! Temp=%.1f C\r\n", (double)pa_heatsink_temp_c);
}

/* ─────────────────────────────────────────────────────────────────── */
/* ADC Capture via ADS8661 (SPI4)                                       */
/* ─────────────────────────────────────────────────────────────────── */

static uint16_t ADC_ReadSingleSample(void) {
    /* ADS8661 SPI read: 24-bit transaction
     * Send: [0x00 0x00 0x00] with CS asserted
     * Receive: [status|MSB][LSB][don't care]
     * Data = received_word >> 4 (12-bit in 16-bit MSB justified)
     * Wait: /BUSY goes low after conversion, then read
     */
    uint8_t tx_buf[3] = {0x00, 0x00, 0x00};
    uint8_t rx_buf[3] = {0x00};

    HAL_GPIO_WritePin(GPIOE, GPIO_PIN_11, GPIO_PIN_RESET);  /* CS low */
    HAL_SPI_TransmitReceive(&hspi4, tx_buf, rx_buf, 3, 10);
    HAL_GPIO_WritePin(GPIOE, GPIO_PIN_11, GPIO_PIN_SET);    /* CS high */

    /* Extract 16-bit sample from received bytes */
    uint16_t sample = ((uint16_t)rx_buf[0] << 8) | rx_buf[1];
    return sample;
}

static void Start_ADC_Capture(uint32_t n_samples) {
    if (n_samples > ADC_BUFFER_SIZE) n_samples = ADC_BUFFER_SIZE;
    adc_sample_count = 0;
    capture_active   = true;
    HAL_GPIO_WritePin(LED_TX_GPIO_PORT, LED_TX_GPIO_PIN, GPIO_PIN_SET);
    printf("Capture started: %lu samples\r\n", (unsigned long)n_samples);
}

static void LED_OK_Toggle(void) {
    HAL_GPIO_TogglePin(LED_OK_GPIO_PORT, LED_OK_GPIO_PIN);
}
