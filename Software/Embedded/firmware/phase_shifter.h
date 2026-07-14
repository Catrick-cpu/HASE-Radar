/**
 * @file phase_shifter.h
 * @brief HMC647ALP5E Digital Phase Shifter Driver — AERIS-10P Radar
 *
 * Controls 32 HMC647A 6-bit digital phase shifters via SPI daisy-chain.
 * TX array: 16 shifters on SPI1 bus
 * RX array: 16 shifters on SPI2 bus
 *
 * HMC647A bit weights:
 *   Bit 5 (MSB): 180.0 degrees
 *   Bit 4:        90.0 degrees
 *   Bit 3:        45.0 degrees
 *   Bit 2:        22.5 degrees
 *   Bit 1:        11.25 degrees
 *   Bit 0 (LSB):   5.625 degrees
 *   Total range: 0 to 354.375 degrees in 64 steps
 */

#ifndef PHASE_SHIFTER_H
#define PHASE_SHIFTER_H

#include "stm32h7xx_hal.h"
#include <stdint.h>
#include <stdbool.h>

/* ─────────────────────────────────────────────────────────────────── */
/* Configuration                                                         */
/* ─────────────────────────────────────────────────────────────────── */

#define PS_ELEMENTS_PER_BUS     16      /* 16 phase shifters per SPI bus */
#define PS_TOTAL_ELEMENTS       32      /* 16 TX + 16 RX */
#define PS_BITS                 6       /* 6-bit control word */
#define PS_MAX_CODE             63      /* maximum code (0x3F) */
#define PS_LSB_DEGREES          5.625f  /* degrees per LSB */
#define PS_FULL_SCALE_DEG       360.0f  /* full-scale range */
#define PS_SETTLE_US            2       /* settling time after update */

/* SPI bus selection */
#define PS_BUS_TX               0
#define PS_BUS_RX               1

/* GPIO pins for chip-select (active LOW) */
#define PS_TX_CS_GPIO_PORT      GPIOA
#define PS_TX_CS_GPIO_PIN       GPIO_PIN_4   /* SPI1_NSS */
#define PS_RX_CS_GPIO_PORT      GPIOB
#define PS_RX_CS_GPIO_PIN       GPIO_PIN_12  /* SPI2_NSS */

/* GPIO for latch-enable (same as CS for HMC647A) */
/* HMC647A: phase latches on rising edge of CS/LE */

/* Physical constants for beamforming */
#define PS_ELEMENT_SPACING_MM   15.0f   /* mm, lambda/2 at 10 GHz */
#define PS_WAVELENGTH_MM        29.85f  /* mm at 10.05 GHz center */
#define PS_ARRAY_ROWS           4
#define PS_ARRAY_COLS           4

/* ─────────────────────────────────────────────────────────────────── */
/* Data Structures                                                       */
/* ─────────────────────────────────────────────────────────────────── */

/** Error codes for phase shifter operations */
typedef enum {
    PS_OK              = 0,
    PS_ERR_SPI         = 1,   /* SPI communication error */
    PS_ERR_TIMEOUT     = 2,   /* operation timed out */
    PS_ERR_PARAM       = 3,   /* invalid parameter */
    PS_ERR_CAL_MISSING = 4,   /* calibration table not loaded */
} PS_Error_t;

/** Configuration for a single phase shifter element */
typedef struct {
    uint8_t  bus;             /* PS_BUS_TX or PS_BUS_RX */
    uint8_t  chain_pos;       /* position in daisy chain (0=first, 15=last) */
    uint8_t  row;             /* array row index [0..3] */
    uint8_t  col;             /* array column index [0..3] */
    float    phase_degrees;   /* commanded phase [0..360) */
    uint8_t  phase_code;      /* 6-bit SPI code [0..63] */
    float    cal_offset_deg;  /* calibration correction offset */
} PS_Element_t;

/** Configuration for a complete 4x4 array */
typedef struct {
    PS_Element_t elements[PS_ELEMENTS_PER_BUS];
    float        steering_az_deg;   /* current beam azimuth */
    float        steering_el_deg;   /* current beam elevation */
    bool         cal_loaded;        /* calibration table available */
    float        cal_table[PS_ELEMENTS_PER_BUS][PS_MAX_CODE + 1]; /* phase correction per element/code */
} PS_Array_t;

/** Complete phased array system (TX + RX) */
typedef struct {
    PS_Array_t   tx;     /* transmit array */
    PS_Array_t   rx;     /* receive array */
    SPI_HandleTypeDef *hspi_tx;   /* SPI handle for TX bus */
    SPI_HandleTypeDef *hspi_rx;   /* SPI handle for RX bus */
} PS_System_t;

/* ─────────────────────────────────────────────────────────────────── */
/* Function Prototypes                                                   */
/* ─────────────────────────────────────────────────────────────────── */

/**
 * @brief Initialize phase shifter system
 * @param sys   Pointer to PS_System_t structure
 * @param hspi1 SPI handle for TX array (SPI1)
 * @param hspi2 SPI handle for RX array (SPI2)
 * @return PS_OK on success
 */
PS_Error_t PS_Init(PS_System_t *sys, SPI_HandleTypeDef *hspi1, SPI_HandleTypeDef *hspi2);

/**
 * @brief Set all phase shifters for broadside beam (all phases = 0)
 * @param sys   Pointer to PS_System_t
 * @return PS_OK on success
 */
PS_Error_t PS_SetBroadside(PS_System_t *sys);

/**
 * @brief Set beam steering angles for both TX and RX arrays
 * @param sys      Pointer to PS_System_t
 * @param az_deg   Azimuth steering angle in degrees [-45..+45]
 * @param el_deg   Elevation steering angle in degrees [-45..+45]
 * @return PS_OK on success
 */
PS_Error_t PS_SetSteering(PS_System_t *sys, float az_deg, float el_deg);

/**
 * @brief Set phase of a single element
 * @param elem     Pointer to PS_Element_t
 * @param degrees  Desired phase [0..360)
 */
void PS_SetElementPhase(PS_Element_t *elem, float degrees);

/**
 * @brief Convert phase in degrees to 6-bit code
 * @param degrees  Phase [0..360)
 * @return 6-bit code [0..63]
 */
uint8_t PS_DegreesToCode(float degrees);

/**
 * @brief Convert 6-bit code to phase in degrees
 * @param code  [0..63]
 * @return phase in degrees
 */
float PS_CodeToDegrees(uint8_t code);

/**
 * @brief Update all phase shifters on one SPI bus via daisy-chain
 * @param sys  Pointer to PS_System_t
 * @param bus  PS_BUS_TX or PS_BUS_RX
 * @return PS_OK on success, PS_ERR_SPI on failure
 */
PS_Error_t PS_UpdateAll(PS_System_t *sys, uint8_t bus);

/**
 * @brief Update both TX and RX arrays simultaneously
 * @param sys  Pointer to PS_System_t
 * @return PS_OK on success
 */
PS_Error_t PS_UpdateBoth(PS_System_t *sys);

/**
 * @brief Load calibration table from flash
 * @param sys         Pointer to PS_System_t
 * @param cal_data_tx Pointer to TX calibration data (16 x 64 floats)
 * @param cal_data_rx Pointer to RX calibration data (16 x 64 floats)
 * @return PS_OK on success
 */
PS_Error_t PS_LoadCalibration(PS_System_t *sys,
                               const float cal_data_tx[PS_ELEMENTS_PER_BUS][PS_MAX_CODE + 1],
                               const float cal_data_rx[PS_ELEMENTS_PER_BUS][PS_MAX_CODE + 1]);

/**
 * @brief Apply calibration correction to a phase command
 * @param elem       Pointer to element
 * @param degrees    Desired phase (corrected output written back)
 * @return corrected phase code
 */
uint8_t PS_ApplyCalibration(const PS_Element_t *elem, float degrees);

/**
 * @brief Compute phase gradient for given steering angle
 * @param row      Element row index [0..3]
 * @param col      Element col index [0..3]
 * @param az_deg   Azimuth angle [deg]
 * @param el_deg   Elevation angle [deg]
 * @return phase [0..360) in degrees
 */
float PS_ComputeElementPhase(uint8_t row, uint8_t col, float az_deg, float el_deg);

#endif /* PHASE_SHIFTER_H */
