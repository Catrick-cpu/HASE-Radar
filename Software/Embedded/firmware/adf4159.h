/**
 * @file adf4159.h
 * @brief ADF4159 FMCW PLL Driver — AERIS-10P Radar
 *
 * Controls the ADF4159 fractional-N PLL with built-in FMCW ramp generator.
 * Reference: ADF4159 datasheet Rev E, Analog Devices.
 *
 * AERIS-10P configuration:
 *   Reference: 10 MHz OCXO
 *   VCO: HMC733LP6CE (9.5-11 GHz)
 *   Chirp: 10.000 to 10.100 GHz in 1 ms sawtooth
 *   PFD frequency: 10 MHz (R=1)
 *   INT: 1000 (for 10.000 GHz at f_pfd=10MHz)
 *   FRAC: 0 (for exact 10.000 GHz start)
 *   DEV: ramp deviation for 100 MHz sweep
 */

#ifndef ADF4159_H
#define ADF4159_H

#include "stm32h7xx_hal.h"
#include <stdint.h>
#include <stdbool.h>

/* ─────────────────────────────────────────────────────────────────── */
/* ADF4159 Register Map (R0..R7, 32-bit each, 3 control bits [2:0])    */
/* ─────────────────────────────────────────────────────────────────── */

#define ADF4159_REG0   0x00   /* R0: INT, FRAC MSB, MUXOUT */
#define ADF4159_REG1   0x01   /* R1: FRAC LSB */
#define ADF4159_REG2   0x02   /* R2: R-counter, REF doubler/divider */
#define ADF4159_REG3   0x03   /* R3: Ramp clock, prescaler, sigma-delta */
#define ADF4159_REG4   0x04   /* R4: R4: CL_DIV, CP current, ramp mode */
#define ADF4159_REG5   0x05   /* R5: TX ramp rate, deviation word */
#define ADF4159_REG6   0x06   /* R6: Step word (frequency deviation per step) */
#define ADF4159_REG7   0x07   /* R7: Ramp delay, fast ramp, ramp enable */

/* ─────────────────────────────────────────────────────────────────── */
/* Bit Field Definitions (key bits only)                                */
/* ─────────────────────────────────────────────────────────────────── */

/* R0 bit fields */
#define ADF4159_R0_INT_SHIFT        15
#define ADF4159_R0_FRAC_MSB_SHIFT   3
#define ADF4159_R0_MUXOUT_SHIFT     27
#define ADF4159_R0_INT_MASK         0x0000FFF8UL
#define ADF4159_R0_FRAC_MSB_MASK    0x0FFF0000UL

/* R2 bit fields */
#define ADF4159_R2_R_SHIFT          15   /* R-counter */
#define ADF4159_R2_REF_DBL_SHIFT    25   /* REF doubler (0=disable) */
#define ADF4159_R2_REF_DIV2_SHIFT   26   /* REF divider (0=disable) */
#define ADF4159_R2_R_MASK           0x007F8000UL

/* R4 bit fields */
#define ADF4159_R4_RAMP_MODE_SHIFT  10   /* 0=sawtooth, 1=triangular, etc. */
#define ADF4159_R4_CLK_DIV_SHIFT    15
#define ADF4159_R4_CP_CURR_SHIFT    24
#define ADF4159_R4_RAMP_EN_SHIFT    31   /* 1=enable continuous ramp */

/* R7 bit fields */
#define ADF4159_R7_RAMP_EN_SHIFT    31
#define ADF4159_R7_FAST_RAMP_SHIFT  29
#define ADF4159_R7_TXDATA_INV_SHIFT 27

/* ─────────────────────────────────────────────────────────────────── */
/* Configuration Constants for AERIS-10P                                */
/* ─────────────────────────────────────────────────────────────────── */

#define ADF4159_REF_FREQ_HZ         10000000UL   /* 10 MHz OCXO */
#define ADF4159_R_COUNTER           1             /* PFD = 10 MHz */
#define ADF4159_PFD_FREQ_HZ         10000000UL   /* PFD frequency */
#define ADF4159_MOD                 4096          /* modulus */
#define ADF4159_CP_CURRENT_UA       1875          /* charge pump 1.875 mA */

/* Default chirp: 10.000 GHz to 10.100 GHz in 1 ms */
#define ADF4159_START_FREQ_HZ       10000000000ULL
#define ADF4159_STOP_FREQ_HZ        10100000000ULL
#define ADF4159_CHIRP_TIME_US       1000
#define ADF4159_RAMP_MODE_SAWTOOTH  0

/* INT for 10 GHz: N = f_vco / f_pfd = 10000000000 / 10000000 = 1000 */
#define ADF4159_INT_10GHz           1000
#define ADF4159_FRAC_10GHz          0

/* SPI GPIO */
#define ADF4159_SPI_PORT            hspi3          /* SPI3 on STM32H743 */
#define ADF4159_LE_GPIO_PORT        GPIOA
#define ADF4159_LE_GPIO_PIN         GPIO_PIN_15    /* PA15 = SPI3_NSS */
#define ADF4159_TXDATA_GPIO_PORT    GPIOC
#define ADF4159_TXDATA_GPIO_PIN     GPIO_PIN_2     /* PC2 = RAMP_EN */

/* ─────────────────────────────────────────────────────────────────── */
/* Data Structures                                                       */
/* ─────────────────────────────────────────────────────────────────── */

/** Ramp mode selection */
typedef enum {
    ADF4159_RAMP_SAWTOOTH_UP    = 0,
    ADF4159_RAMP_SAWTOOTH_DOWN  = 1,
    ADF4159_RAMP_TRIANGULAR     = 2,
    ADF4159_RAMP_DUAL_SAWTOOTH  = 3,
} ADF4159_RampMode_t;

/** Complete ADF4159 configuration */
typedef struct {
    uint64_t            freq_start_hz;     /* chirp start frequency [Hz] */
    uint64_t            freq_stop_hz;      /* chirp stop frequency [Hz] */
    uint32_t            chirp_time_us;     /* chirp duration [microseconds] */
    uint32_t            ref_freq_hz;       /* reference clock frequency [Hz] */
    uint16_t            r_counter;         /* reference divider (R) */
    ADF4159_RampMode_t  ramp_mode;         /* sawtooth / triangular */
    bool                ramp_enabled;      /* continuous ramp active */

    /* Computed register values (filled by ADF4159_ComputeRegisters) */
    uint32_t            reg[8];            /* R0..R7 register values */
    uint16_t            int_val;           /* integer N divider */
    uint32_t            frac_val;          /* fractional part */
    uint32_t            dev_word;          /* deviation word for ramp */
    uint16_t            clk_div;           /* clock divider for ramp */
    uint32_t            pfd_freq_hz;       /* PFD frequency */
} ADF4159_Config_t;

/** Error codes */
typedef enum {
    ADF4159_OK          = 0,
    ADF4159_ERR_SPI     = 1,
    ADF4159_ERR_PARAM   = 2,
    ADF4159_ERR_NO_LOCK = 3,
    ADF4159_ERR_RANGE   = 4,   /* frequency out of VCO range */
} ADF4159_Error_t;

/* ─────────────────────────────────────────────────────────────────── */
/* Function Prototypes                                                   */
/* ─────────────────────────────────────────────────────────────────── */

/**
 * @brief Initialize ADF4159 with AERIS-10P default settings
 * @param cfg    Pointer to ADF4159_Config_t (will be populated with defaults)
 * @param hspi   SPI handle (SPI3 on AERIS-10P)
 * @return ADF4159_OK on success
 */
ADF4159_Error_t ADF4159_Init(ADF4159_Config_t *cfg, SPI_HandleTypeDef *hspi);

/**
 * @brief Compute all register values from configuration
 * @param cfg    Pointer to ADF4159_Config_t
 * @return ADF4159_OK on success, ADF4159_ERR_RANGE if frequency out of bounds
 */
ADF4159_Error_t ADF4159_ComputeRegisters(ADF4159_Config_t *cfg);

/**
 * @brief Write all registers to ADF4159 (R7 first, R0 last per datasheet)
 * @param cfg    Pointer to computed ADF4159_Config_t
 * @param hspi   SPI handle
 * @return ADF4159_OK on success
 */
ADF4159_Error_t ADF4159_WriteAllRegisters(const ADF4159_Config_t *cfg,
                                           SPI_HandleTypeDef *hspi);

/**
 * @brief Write single register to ADF4159
 * @param reg_word  32-bit register value (includes 3-bit address in [2:0])
 * @param hspi      SPI handle
 * @return ADF4159_OK on success
 */
ADF4159_Error_t ADF4159_WriteRegister(uint32_t reg_word, SPI_HandleTypeDef *hspi);

/**
 * @brief Set chirp parameters (start/stop frequency, sweep time)
 * @param cfg           Pointer to config
 * @param start_hz      Start frequency [Hz]
 * @param stop_hz       Stop frequency [Hz]
 * @param sweep_time_us Sweep time [microseconds]
 * @param hspi          SPI handle
 * @return ADF4159_OK on success
 */
ADF4159_Error_t ADF4159_SetChirp(ADF4159_Config_t *cfg,
                                   uint64_t start_hz,
                                   uint64_t stop_hz,
                                   uint32_t sweep_time_us,
                                   SPI_HandleTypeDef *hspi);

/**
 * @brief Enable continuous FMCW ramp
 * @param hspi  SPI handle
 * @return ADF4159_OK on success
 */
ADF4159_Error_t ADF4159_EnableRamp(SPI_HandleTypeDef *hspi);

/**
 * @brief Disable FMCW ramp (CW output at start frequency)
 * @param hspi  SPI handle
 * @return ADF4159_OK on success
 */
ADF4159_Error_t ADF4159_DisableRamp(SPI_HandleTypeDef *hspi);

/**
 * @brief Check PLL lock status via MUXOUT GPIO
 * @return true if locked
 */
bool ADF4159_IsLocked(void);

/**
 * @brief Print current configuration to UART (for debugging)
 * @param cfg  Pointer to ADF4159_Config_t
 */
void ADF4159_PrintConfig(const ADF4159_Config_t *cfg);

#endif /* ADF4159_H */
