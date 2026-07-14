/**
 * @file phase_shifter.c
 * @brief HMC647ALP5E Digital Phase Shifter Driver Implementation — AERIS-10P
 */

#include "phase_shifter.h"
#include <math.h>
#include <string.h>

/* Private helper: assert CS low */
static void ps_cs_low(uint8_t bus) {
    if (bus == PS_BUS_TX)
        HAL_GPIO_WritePin(PS_TX_CS_GPIO_PORT, PS_TX_CS_GPIO_PIN, GPIO_PIN_RESET);
    else
        HAL_GPIO_WritePin(PS_RX_CS_GPIO_PORT, PS_RX_CS_GPIO_PIN, GPIO_PIN_RESET);
}

/* Private helper: assert CS high (latches all phase shifters simultaneously) */
static void ps_cs_high(uint8_t bus) {
    if (bus == PS_BUS_TX)
        HAL_GPIO_WritePin(PS_TX_CS_GPIO_PORT, PS_TX_CS_GPIO_PIN, GPIO_PIN_SET);
    else
        HAL_GPIO_WritePin(PS_RX_CS_GPIO_PORT, PS_RX_CS_GPIO_PIN, GPIO_PIN_SET);
}

/* Private helper: microsecond delay */
static void ps_delay_us(uint32_t us) {
    /* Use DWT cycle counter for accurate delay on Cortex-M7 */
    uint32_t start = DWT->CYCCNT;
    uint32_t cycles = us * (HAL_RCC_GetHCLKFreq() / 1000000UL);
    while ((DWT->CYCCNT - start) < cycles) {}
}

/* ─────────────────────────────────────────────────────────────────── */

PS_Error_t PS_Init(PS_System_t *sys, SPI_HandleTypeDef *hspi1, SPI_HandleTypeDef *hspi2) {
    if (!sys || !hspi1 || !hspi2) return PS_ERR_PARAM;

    sys->hspi_tx = hspi1;
    sys->hspi_rx = hspi2;

    /* Initialize TX array elements */
    for (uint8_t i = 0; i < PS_ELEMENTS_PER_BUS; i++) {
        PS_Element_t *e = &sys->tx.elements[i];
        e->bus           = PS_BUS_TX;
        e->chain_pos     = i;
        e->row           = i / PS_ARRAY_COLS;
        e->col           = i % PS_ARRAY_COLS;
        e->phase_degrees = 0.0f;
        e->phase_code    = 0;
        e->cal_offset_deg = 0.0f;
    }
    sys->tx.steering_az_deg = 0.0f;
    sys->tx.steering_el_deg = 0.0f;
    sys->tx.cal_loaded = false;

    /* Initialize RX array elements */
    for (uint8_t i = 0; i < PS_ELEMENTS_PER_BUS; i++) {
        PS_Element_t *e = &sys->rx.elements[i];
        e->bus           = PS_BUS_RX;
        e->chain_pos     = i;
        e->row           = i / PS_ARRAY_COLS;
        e->col           = i % PS_ARRAY_COLS;
        e->phase_degrees = 0.0f;
        e->phase_code    = 0;
        e->cal_offset_deg = 0.0f;
    }
    sys->rx.steering_az_deg = 0.0f;
    sys->rx.steering_el_deg = 0.0f;
    sys->rx.cal_loaded = false;

    /* Ensure CS lines are high (inactive) */
    ps_cs_high(PS_BUS_TX);
    ps_cs_high(PS_BUS_RX);

    /* Set broadside beam (all phases = 0) */
    return PS_SetBroadside(sys);
}

/* ─────────────────────────────────────────────────────────────────── */

uint8_t PS_DegreesToCode(float degrees) {
    /* Normalize to [0, 360) */
    while (degrees < 0.0f)    degrees += 360.0f;
    while (degrees >= 360.0f) degrees -= 360.0f;

    /* Convert: code = round(degrees / PS_LSB_DEGREES) mod 64 */
    uint8_t code = (uint8_t)((degrees / PS_LSB_DEGREES) + 0.5f) & PS_MAX_CODE;
    return code;
}

/* ─────────────────────────────────────────────────────────────────── */

float PS_CodeToDegrees(uint8_t code) {
    return (float)(code & PS_MAX_CODE) * PS_LSB_DEGREES;
}

/* ─────────────────────────────────────────────────────────────────── */

void PS_SetElementPhase(PS_Element_t *elem, float degrees) {
    /* Apply calibration offset if available */
    float corrected = degrees + elem->cal_offset_deg;
    elem->phase_degrees = degrees;
    elem->phase_code    = PS_DegreesToCode(corrected);
}

/* ─────────────────────────────────────────────────────────────────── */

float PS_ComputeElementPhase(uint8_t row, uint8_t col, float az_deg, float el_deg) {
    /*
     * Phase gradient for beam steering:
     * phi(i,j) = (2*pi/lambda) * d * (i*sin(az) + j*sin(el))
     *
     * With d = lambda/2 (element spacing = PS_ELEMENT_SPACING_MM = lambda/2):
     * phi(i,j) = pi * (i*sin(az) + j*sin(el))  [radians]
     *          = 180 * (i*sin(az) + j*sin(el))  [degrees]
     *
     * Center element (1.5, 1.5) is reference (phase = 0 for broadside).
     * Element index relative to center:
     *   i_rel = row - 1.5
     *   j_rel = col - 1.5
     */
    float pi = 3.14159265f;
    float az_rad = az_deg * pi / 180.0f;
    float el_rad = el_deg * pi / 180.0f;

    float i_rel = (float)row - 1.5f;
    float j_rel = (float)col - 1.5f;

    float phase_deg = 180.0f * (i_rel * sinf(az_rad) + j_rel * sinf(el_rad));

    /* Normalize to [0, 360) */
    while (phase_deg < 0.0f)    phase_deg += 360.0f;
    while (phase_deg >= 360.0f) phase_deg -= 360.0f;

    return phase_deg;
}

/* ─────────────────────────────────────────────────────────────────── */

PS_Error_t PS_SetBroadside(PS_System_t *sys) {
    for (uint8_t i = 0; i < PS_ELEMENTS_PER_BUS; i++) {
        PS_SetElementPhase(&sys->tx.elements[i], 0.0f);
        PS_SetElementPhase(&sys->rx.elements[i], 0.0f);
    }
    sys->tx.steering_az_deg = 0.0f;
    sys->tx.steering_el_deg = 0.0f;
    sys->rx.steering_az_deg = 0.0f;
    sys->rx.steering_el_deg = 0.0f;
    return PS_UpdateBoth(sys);
}

/* ─────────────────────────────────────────────────────────────────── */

PS_Error_t PS_SetSteering(PS_System_t *sys, float az_deg, float el_deg) {
    /* Clamp steering angles */
    if (az_deg < -45.0f) az_deg = -45.0f;
    if (az_deg > +45.0f) az_deg = +45.0f;
    if (el_deg < -45.0f) el_deg = -45.0f;
    if (el_deg > +45.0f) el_deg = +45.0f;

    /* Compute phase for each TX element */
    for (uint8_t i = 0; i < PS_ELEMENTS_PER_BUS; i++) {
        PS_Element_t *e = &sys->tx.elements[i];
        float phase = PS_ComputeElementPhase(e->row, e->col, az_deg, el_deg);
        PS_SetElementPhase(e, phase);
    }
    sys->tx.steering_az_deg = az_deg;
    sys->tx.steering_el_deg = el_deg;

    /* Compute phase for each RX element (same steering) */
    for (uint8_t i = 0; i < PS_ELEMENTS_PER_BUS; i++) {
        PS_Element_t *e = &sys->rx.elements[i];
        float phase = PS_ComputeElementPhase(e->row, e->col, az_deg, el_deg);
        PS_SetElementPhase(e, phase);
    }
    sys->rx.steering_az_deg = az_deg;
    sys->rx.steering_el_deg = el_deg;

    return PS_UpdateBoth(sys);
}

/* ─────────────────────────────────────────────────────────────────── */

PS_Error_t PS_UpdateAll(PS_System_t *sys, uint8_t bus) {
    PS_Array_t       *array = (bus == PS_BUS_TX) ? &sys->tx : &sys->rx;
    SPI_HandleTypeDef *hspi = (bus == PS_BUS_TX) ? sys->hspi_tx : sys->hspi_rx;

    /* Build SPI data buffer: 16 bytes, one per phase shifter.
     * Daisy-chain order: element 15 first, element 0 last.
     * HMC647A expects 8-bit SPI word, MSB first.
     * Only lower 6 bits [5:0] are used (B5..B0).
     */
    uint8_t spi_data[PS_ELEMENTS_PER_BUS];
    for (uint8_t i = 0; i < PS_ELEMENTS_PER_BUS; i++) {
        /* Chain position 0 is last in physical chain, receives last byte */
        /* Byte 0 in buffer -> sent first -> arrives at element 15 */
        spi_data[i] = array->elements[PS_ELEMENTS_PER_BUS - 1 - i].phase_code & PS_MAX_CODE;
    }

    /* Assert CS low (enable serial input) */
    ps_cs_low(bus);

    /* Transmit all 16 bytes */
    HAL_StatusTypeDef status = HAL_SPI_Transmit(hspi, spi_data,
                                                  PS_ELEMENTS_PER_BUS, 100);

    /* Rising edge of CS latches all phase values simultaneously */
    ps_cs_high(bus);

    /* Wait for phase to settle (2 µs) */
    ps_delay_us(PS_SETTLE_US);

    return (status == HAL_OK) ? PS_OK : PS_ERR_SPI;
}

/* ─────────────────────────────────────────────────────────────────── */

PS_Error_t PS_UpdateBoth(PS_System_t *sys) {
    PS_Error_t err;
    err = PS_UpdateAll(sys, PS_BUS_TX);
    if (err != PS_OK) return err;
    err = PS_UpdateAll(sys, PS_BUS_RX);
    return err;
}

/* ─────────────────────────────────────────────────────────────────── */

PS_Error_t PS_LoadCalibration(PS_System_t *sys,
                               const float cal_data_tx[PS_ELEMENTS_PER_BUS][PS_MAX_CODE + 1],
                               const float cal_data_rx[PS_ELEMENTS_PER_BUS][PS_MAX_CODE + 1]) {
    if (!sys || !cal_data_tx || !cal_data_rx) return PS_ERR_PARAM;

    memcpy(sys->tx.cal_table, cal_data_tx,
           sizeof(float) * PS_ELEMENTS_PER_BUS * (PS_MAX_CODE + 1));
    memcpy(sys->rx.cal_table, cal_data_rx,
           sizeof(float) * PS_ELEMENTS_PER_BUS * (PS_MAX_CODE + 1));

    sys->tx.cal_loaded = true;
    sys->rx.cal_loaded = true;

    return PS_OK;
}
