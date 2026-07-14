/**
 * @file adf4159.c
 * @brief ADF4159 FMCW PLL Driver Implementation — AERIS-10P Radar
 *
 * Key FMCW register calculations:
 *
 * PFD frequency: f_pfd = f_ref / R = 10e6 / 1 = 10 MHz
 *
 * For start frequency f_start = 10.000 GHz:
 *   N = f_start / f_pfd = 10000000000 / 10000000 = 1000.000
 *   INT = 1000, FRAC = 0
 *
 * For FMCW ramp (sawtooth from f_start to f_stop in T_ramp):
 *   CLK2 rate = f_pfd / CLK_DIV
 *   Each CLK2 tick: VCO frequency steps by DEV * f_pfd / MOD
 *   Total steps = CLK_DIV * MOD / (f_pfd * T_ramp) steps to go from f_start to f_stop
 *
 *   Simpler: DEV_WORD = (f_stop - f_start) * T_ramp * f_pfd^2 / (CLK2 * f_pfd * MOD)
 *
 * See ADF4159 datasheet Rev E, pages 19-25 for detailed register programming.
 */

#include "adf4159.h"
#include <stdio.h>
#include <string.h>
#include <math.h>

/* Private: pulse LE to write register */
static ADF4159_Error_t adf4159_latch(void) {
    HAL_GPIO_WritePin(ADF4159_LE_GPIO_PORT, ADF4159_LE_GPIO_PIN, GPIO_PIN_SET);
    HAL_Delay(1);
    HAL_GPIO_WritePin(ADF4159_LE_GPIO_PORT, ADF4159_LE_GPIO_PIN, GPIO_PIN_RESET);
    return ADF4159_OK;
}

/* ─────────────────────────────────────────────────────────────────── */

ADF4159_Error_t ADF4159_WriteRegister(uint32_t reg_word, SPI_HandleTypeDef *hspi) {
    /* ADF4159 SPI: 32-bit word, MSB first, CPOL=0 CPHA=0 */
    uint8_t buf[4];
    buf[0] = (reg_word >> 24) & 0xFF;
    buf[1] = (reg_word >> 16) & 0xFF;
    buf[2] = (reg_word >>  8) & 0xFF;
    buf[3] = (reg_word      ) & 0xFF;

    HAL_GPIO_WritePin(ADF4159_LE_GPIO_PORT, ADF4159_LE_GPIO_PIN, GPIO_PIN_RESET);
    HAL_StatusTypeDef status = HAL_SPI_Transmit(hspi, buf, 4, 50);
    if (status != HAL_OK) return ADF4159_ERR_SPI;

    /* LE pulse to latch */
    return adf4159_latch();
}

/* ─────────────────────────────────────────────────────────────────── */

ADF4159_Error_t ADF4159_ComputeRegisters(ADF4159_Config_t *cfg) {
    if (!cfg) return ADF4159_ERR_PARAM;

    uint64_t f_start = cfg->freq_start_hz;
    uint64_t f_stop  = cfg->freq_stop_hz;
    uint32_t f_pfd   = cfg->ref_freq_hz / cfg->r_counter;
    uint64_t bw      = f_stop - f_start;

    /* Check range */
    if (f_start < 9500000000ULL || f_stop > 11000000000ULL)
        return ADF4159_ERR_RANGE;

    cfg->pfd_freq_hz = f_pfd;

    /* INT for start frequency: N = f_start / f_pfd */
    cfg->int_val = (uint16_t)(f_start / f_pfd);

    /* FRAC for fractional part: FRAC = (f_start - INT*f_pfd) * MOD / f_pfd */
    uint64_t frac_num = (f_start - (uint64_t)cfg->int_val * f_pfd);
    cfg->frac_val = (uint32_t)(frac_num * ADF4159_MOD / f_pfd);

    /*
     * Ramp deviation calculation:
     * CLK_DIV: chosen so ramp steps are reasonable
     * Using CLK_DIV = 1 (CLK2 = f_pfd = 10 MHz)
     * Number of ramp steps in T_ramp:
     *   steps = f_pfd * T_ramp_s = 10e6 * 1e-3 = 10000 steps
     * Frequency step per CLK2 tick:
     *   delta_f = bw / steps = 100e6 / 10000 = 10 kHz per step
     * DEV word = delta_f * MOD / f_pfd = 10000 * 4096 / 10000000 = 4.096
     * DEV_WORD = round(delta_f * MOD / f_pfd) = 4
     * Actual step: 4 * 10e6 / 4096 = 9765.625 Hz
     * Actual sweep time for 100 MHz: 100e6 / 9765.625 = 10240 steps / 10 MHz = 1.024 ms
     * (Close enough — fine-tune CLK_DIV for exact timing)
     *
     * Better approach: use CLK_DIV to get integer steps
     * steps = bw / (f_pfd/MOD) = 100e6 / (10e6/4096) = 40960 steps
     * T_ramp = steps / f_pfd = 40960 / 10e6 = 4.096 ms (not 1 ms)
     * Use CLK_DIV = 4: CLK2 = 10e6/4 = 2.5 MHz
     * steps = 2.5e6 * 1e-3 = 2500 steps in 1 ms
     * delta_f = 100e6 / 2500 = 40000 Hz/step
     * DEV_WORD = 40000 * 4096 / 10e6 = 16.384 -> DEV_WORD = 16
     * Actual: 16 * 10e6 / 4096 = 39062.5 Hz/step
     * Total sweep: 2500 * 39062.5 = 97.65 MHz in 1 ms (close to 100 MHz)
     */
    cfg->clk_div  = 4;  /* CLK_DIV = 4 -> CLK2 = 2.5 MHz */
    uint32_t clk2_freq = f_pfd / cfg->clk_div;
    uint32_t n_steps = (uint32_t)((uint64_t)clk2_freq * cfg->chirp_time_us / 1000000UL);
    if (n_steps == 0) n_steps = 1;

    /* DEV_WORD = bw * MOD / (n_steps * f_pfd) */
    cfg->dev_word = (uint32_t)(bw * ADF4159_MOD / ((uint64_t)n_steps * f_pfd));
    if (cfg->dev_word == 0) cfg->dev_word = 1;

    /* ─── Build Register Words ────────────────────────────────────── */

    /* R0: INT[15:3] | FRAC_MSB[26:16] | MUXOUT[29:27] | addr=000 */
    /* FRAC is 25-bit total: MSB=12 bits in R0, LSB=13 bits in R1 */
    uint32_t frac_msb = (cfg->frac_val >> 13) & 0xFFF;
    uint32_t frac_lsb = cfg->frac_val & 0x1FFF;
    cfg->reg[0] = ((uint32_t)cfg->int_val << 15) |
                  (frac_msb << 3) |
                  0x00000000UL;  /* addr = 000 */
    /* MUXOUT = 0b110 = digital lock detect -> bits [29:27] */
    cfg->reg[0] |= (0x06UL << 27);

    /* R1: FRAC_LSB[15:3] | addr=001 */
    cfg->reg[1] = (frac_lsb << 3) | 0x00000001UL;

    /* R2: R-counter[21:15] | addr=010 */
    cfg->reg[2] = ((uint32_t)cfg->r_counter << 15) | 0x00000002UL;

    /* R3: CLK_DIV_MODE=01 (ramp), PRESCALER=0 (8/9), addr=011 */
    cfg->reg[3] = (0x01UL << 15) | /* CLK_DIV_MODE = ramp clock divider mode */
                  0x00000003UL;

    /* R4: CP_CURRENT[27:24]=0111 (2.5mA), CLK_DIV[26:15]=clk_div, RAMP_MODE[11:10]=sawtooth */
    cfg->reg[4] = (0x07UL << 24) |   /* CP current 2.5 mA */
                  ((uint32_t)cfg->clk_div << 15) |
                  ((uint32_t)cfg->ramp_mode << 10) |
                  0x00000004UL;

    /* R5: TX_RAMP_CLK=1 (use CLK2 for ramp), TX_DATA_INV=0, addr=101 */
    cfg->reg[5] = (0x01UL << 29) |   /* TX_RAMP_CLK = CLK2 */
                  0x00000005UL;

    /* R6: STEP_WORD (frequency deviation) = dev_word, addr=110 */
    cfg->reg[6] = (cfg->dev_word << 3) | 0x00000006UL;

    /* R7: RAMP_EN=0 initially, addr=111 */
    cfg->reg[7] = 0x00000007UL;

    return ADF4159_OK;
}

/* ─────────────────────────────────────────────────────────────────── */

ADF4159_Error_t ADF4159_WriteAllRegisters(const ADF4159_Config_t *cfg,
                                            SPI_HandleTypeDef *hspi) {
    /* ADF4159 requires R7 first, then R6..R0 (R0 last) */
    ADF4159_Error_t err;
    for (int8_t i = 7; i >= 0; i--) {
        err = ADF4159_WriteRegister(cfg->reg[i], hspi);
        if (err != ADF4159_OK) return err;
        HAL_Delay(1);
    }
    return ADF4159_OK;
}

/* ─────────────────────────────────────────────────────────────────── */

ADF4159_Error_t ADF4159_Init(ADF4159_Config_t *cfg, SPI_HandleTypeDef *hspi) {
    if (!cfg || !hspi) return ADF4159_ERR_PARAM;

    /* Load AERIS-10P defaults */
    memset(cfg, 0, sizeof(ADF4159_Config_t));
    cfg->freq_start_hz  = ADF4159_START_FREQ_HZ;
    cfg->freq_stop_hz   = ADF4159_STOP_FREQ_HZ;
    cfg->chirp_time_us  = ADF4159_CHIRP_TIME_US;
    cfg->ref_freq_hz    = ADF4159_REF_FREQ_HZ;
    cfg->r_counter      = ADF4159_R_COUNTER;
    cfg->ramp_mode      = ADF4159_RAMP_SAWTOOTH_UP;
    cfg->ramp_enabled   = false;

    /* Initialize LE GPIO low */
    HAL_GPIO_WritePin(ADF4159_LE_GPIO_PORT, ADF4159_LE_GPIO_PIN, GPIO_PIN_RESET);

    /* Compute registers */
    ADF4159_Error_t err = ADF4159_ComputeRegisters(cfg);
    if (err != ADF4159_OK) return err;

    /* Write to chip */
    err = ADF4159_WriteAllRegisters(cfg, hspi);
    if (err != ADF4159_OK) return err;

    /* Verify lock after 10 ms */
    HAL_Delay(10);
    if (!ADF4159_IsLocked()) {
        /* Not necessarily an error during init — VCO may need more time */
        /* Return OK but caller should check lock status */
    }

    return ADF4159_OK;
}

/* ─────────────────────────────────────────────────────────────────── */

ADF4159_Error_t ADF4159_SetChirp(ADF4159_Config_t *cfg,
                                   uint64_t start_hz, uint64_t stop_hz,
                                   uint32_t sweep_time_us, SPI_HandleTypeDef *hspi) {
    cfg->freq_start_hz = start_hz;
    cfg->freq_stop_hz  = stop_hz;
    cfg->chirp_time_us = sweep_time_us;

    ADF4159_Error_t err = ADF4159_ComputeRegisters(cfg);
    if (err != ADF4159_OK) return err;

    return ADF4159_WriteAllRegisters(cfg, hspi);
}

/* ─────────────────────────────────────────────────────────────────── */

ADF4159_Error_t ADF4159_EnableRamp(SPI_HandleTypeDef *hspi) {
    /* Set RAMP_EN bit in R7 */
    uint32_t r7 = (1UL << 31) | /* RAMP_EN */
                  0x00000007UL;  /* addr */
    return ADF4159_WriteRegister(r7, hspi);
}

/* ─────────────────────────────────────────────────────────────────── */

ADF4159_Error_t ADF4159_DisableRamp(SPI_HandleTypeDef *hspi) {
    /* Clear RAMP_EN in R7 */
    uint32_t r7 = 0x00000007UL;
    return ADF4159_WriteRegister(r7, hspi);
}

/* ─────────────────────────────────────────────────────────────────── */

bool ADF4159_IsLocked(void) {
    /* MUXOUT is connected to a GPIO input on STM32 (define pin in hardware config) */
    /* For now, read the MUXOUT signal (configured as digital lock detect) */
    /* TODO: define MUXOUT_GPIO_PORT and MUXOUT_GPIO_PIN in board configuration */
    /* Return true as placeholder — implement with actual GPIO read */
    return true;  /* GPIO_PIN_SET == HAL_GPIO_ReadPin(MUXOUT_GPIO_PORT, MUXOUT_GPIO_PIN) */
}

/* ─────────────────────────────────────────────────────────────────── */

void ADF4159_PrintConfig(const ADF4159_Config_t *cfg) {
    printf("ADF4159 Configuration:\r\n");
    printf("  Start:    %llu Hz (%.6f GHz)\r\n",
           (unsigned long long)cfg->freq_start_hz,
           (double)cfg->freq_start_hz / 1e9);
    printf("  Stop:     %llu Hz (%.6f GHz)\r\n",
           (unsigned long long)cfg->freq_stop_hz,
           (double)cfg->freq_stop_hz / 1e9);
    printf("  BW:       %llu Hz (%.1f MHz)\r\n",
           (unsigned long long)(cfg->freq_stop_hz - cfg->freq_start_hz),
           (double)(cfg->freq_stop_hz - cfg->freq_start_hz) / 1e6);
    printf("  Chirp:    %lu us\r\n", (unsigned long)cfg->chirp_time_us);
    printf("  f_pfd:    %lu Hz\r\n", (unsigned long)cfg->pfd_freq_hz);
    printf("  INT:      %u\r\n", cfg->int_val);
    printf("  FRAC:     %lu\r\n", (unsigned long)cfg->frac_val);
    printf("  CLK_DIV:  %u\r\n", cfg->clk_div);
    printf("  DEV_WORD: %lu\r\n", (unsigned long)cfg->dev_word);
    for (int i = 7; i >= 0; i--) {
        printf("  R%d:       0x%08lX\r\n", i, (unsigned long)cfg->reg[i]);
    }
}
