# Crypto Signal Engine V1

3 aÅŸamalÄ± (Step1 -> Step2 -> Step3) kripto sinyal sistemi.

## AmaÃ§

V1, her coin iÃ§in sÄ±rasÄ±yla:

1. **Step 1 (Fundamental/Interest/On-chain)**
2. **Step 2 (Technical Entry Suitability)**
3. **Step 3 (Market Regime/Risk Veto)**

Ã§alÄ±ÅŸtÄ±rÄ±r ve sonunda tek bir karar Ã¼retir:

- `REJECTED_STEP1`
- `REJECTED_STEP2`
- `REJECTED_STEP3`
- `PASSED_ALL`

## Tamamlanan V1 Mimari

- **Config + .env**: merkezi eÅŸik/aÄŸÄ±rlÄ±k yÃ¶netimi (`app/config/settings.py`)
- **Provider clientâ€™lar**:
  - Santiment
  - CryptoQuant
  - CCXT (universe + OHLCV + opsiyonel derivatives metrikleri)
- **Universe builder**: USDT Ã¶ncelikli, leveraged/garbage filtreleri, fallback semboller
- **Step 1**:
  - veri toplama + normalize + score + confidence + pass/fail
- **Step 2**:
  - trend, momentum, volatilite/structure, hacim, entry logic
  - fallback ve eksik teknik veri takibi
- **Step 3**:
  - BTC regime (EMA/ADX/slope)
  - volatility danger (ATR/drawdown)
  - risk-on/risk-off breadth proxy
  - opsiyonel funding/open-interest adapter + fallback
- **Full pipeline orchestration**:
  - `app/pipeline/full_v1_runner.py`
- **Raporlama**:
  - Step1 raporu: `app/reports/writer.py`
  - Full V1 raporu: `app/reports/full_v1_writer.py`

## Step Ã–zeti

### Step 1 (Fundamental/Interest/On-chain)

Kaynaklar: Santiment + CryptoQuant.

Ã‡Ä±ktÄ±lar:

- `step1_score`
- `confidence_score`
- `step1_pass`
- `reasoning`
- `missing_metrics`

### Step 2 (Technical Filter)

Kaynak: CCXT OHLCV.

Kontroller:

- Trend: MA hizasÄ±, fiyat/MA iliÅŸkisi, slope, ADX
- Momentum: RSI, MACD, Stoch
- Volatilite/structure: ATR, Bollinger width, overextension/noisy setup
- Hacim: volume ratio ve breakout hacim desteÄŸi
- Entry: breakout, trend continuation, reversal-support koÅŸullarÄ±

Ã‡Ä±ktÄ±lar:

- `step2_score`
- `step2_pass`
- `technical_reasoning`
- `technical_snapshot`
- `technical_flags`
- `missing_technical_data`

### Step 3 (Market Regime / Risk Veto)

Temel yaklaÅŸÄ±m:

- BTC rejimi kÃ¶tÃ¼/danger ise veto
- market breadth ve opsiyonel derivatives ile risk gÃ¼veni ayarÄ±

Ã‡Ä±ktÄ±lar:

- `step3_pass`
- `regime_status` (`BULLISH`/`NEUTRAL`/`BEARISH`/`DANGER`)
- `regime_reasoning`
- `regime_snapshot`
- `unavailable_risk_metrics`
- `fallback_used`

## Final AkÄ±ÅŸ

Her coin iÃ§in:

1. Step1 fail -> `REJECTED_STEP1`, `reject_stage=STEP1`
2. Step1 pass -> Step2
3. Step2 fail -> `REJECTED_STEP2`, `reject_stage=STEP2`
4. Step2 pass -> Step3
5. Step3 fail -> `REJECTED_STEP3`, `reject_stage=STEP3`
6. Hepsi pass -> `PASSED_ALL`, `reject_stage=NONE`

## Kurulum

```bash
python -m pip install -r requirements.txt
```

`.env.example` dosyasÄ±nÄ± `.env` olarak kopyalayÄ±p API anahtarlarÄ±nÄ± girin:

- `SANTIMENT_API_KEY`
- `CRYPTOQUANT_API_KEY`

## Ã‡alÄ±ÅŸtÄ±rma

### Sadece Step1

```bash
python scripts/run_step1_scan.py
```

Opsiyonel:

```bash
python scripts/run_step1_scan.py --universe-size 50 --output-dir logs
```

### Full V1 (Step1+Step2+Step3)

```bash
python scripts/run_full_v1_scan.py
```

Opsiyonel:

```bash
python scripts/run_full_v1_scan.py --universe-size 50 --output-dir logs --exchange binance
```

## Ãœretilen Ã‡Ä±ktÄ±lar

### Step1 scan

- `step1_scan_<run_id>.log`
- `step1_results_<run_id>.json`
- `step1_results_<run_id>.csv`
- `step1_summary_<run_id>.json`

### Full V1 scan

- `full_v1_scan_<run_id>.log` (log adÄ± runtime logger Ã¼zerinden)
- `full_v1_results_<run_id>.json`
- `full_v1_results_<run_id>.csv`
- `full_v1_summary_<run_id>.json`

## AlanlarÄ±n Yorumu

- `final_decision`:
  - coinâ€™in en son durumu
- `reject_stage`:
  - coinâ€™in hangi adÄ±mda elendiÄŸi (`STEP1/STEP2/STEP3/NONE`)
- `regime_status`:
  - market rejim etiketi
- `fallback_used_step2` / `fallback_used_step3`:
  - ilgili adÄ±mda fallback devreye girmiÅŸ mi

## Testler

```bash
python -m pytest -q
```

Kapsam:

- mevcut Step1 testleri
- Step2 logic testleri (mock OHLCV)
- Step3 logic testleri (mock BTC regime + fallback)
- Full pipeline geÃ§iÅŸ ve rapor testleri

## V1 LimitasyonlarÄ±

- Teknik ve rejim sinyalleri deterministic kural tabanlÄ±dÄ±r; alpha Ã¼retimi garanti etmez.
- Derivatives tarafÄ±nda funding/open-interest availability exchangeâ€™e baÄŸlÄ±dÄ±r.
- Breadth proxy basit tutulmuÅŸtur; V2â€™de daha gÃ¼Ã§lÃ¼ piyasa breadth/rotation metrikleri planlanÄ±r.

## V2 Yol HaritasÄ±

- GeliÅŸmiÅŸ risk bÃ¼tÃ§esi ve pozisyon boyutlama
- Daha zengin derivatives/liquidation data adapterâ€™larÄ±
- Rejimde Ã§oklu timeframe ve daha iyi market breadth faktÃ¶rleri
- Backtest/forward-test ve parameter calibration katmanÄ±


