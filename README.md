# War Predictor

War Predictor is a research project that explores whether macroeconomic and sociodemographic indicators can signal the approach of an interstate war.
It builds a supervised dataset from historical conflicts and World Bank indicators and fits an OLS linear regression to predict the target variable:

> years_before_the_war — how many years remain before the outbreak of a specific war.

The model can then be applied to country-year panels to estimate proximity to conflict for a pair of countries.

---

## Table of Contents

- Motivation
- How It Works (Pipeline)
- Data Sources
- Repository Layout
- Model
- Key Variables
- Installation
- Quick Start
- Reproducing the Dataset
- Evaluating Accuracy
- Limitations & Caveats
- Roadmap
- License & Attribution

---

## Motivation

The central question is predictability: can macro indicators (growth, inflation, military burden, trade openness, demographics, etc.) provide an advance signal that a dyad is moving toward war?
This project constructs an empirical pipeline to align country-level indicators with known wars and their start years, fit a transparent OLS model, and test how well such a simple model backcasts the timeline to conflict.

---

## How It Works (Pipeline)

1) War list
   - A curated CSV (csv_of_wars.txt) lists 28 conflicts with columns: war, combatant1, combatant2, year_of_start.

2) Year windows
   - For each conflict, the pipeline creates windows like t-10 ... t-1 relative to the start year t to define training labels years_before_the_war in {10,...,1}.

3) World Bank indicators
   - Country CSVs (from WDI) are filtered to the above windows and merged into unified, per-country training frames.
   - Raw data: big data/ and 2023 data/WDICSV.csv
   - Filtered per country: filtered data/
   - Aligned, clean training sets: Formated and Na filtered/, FINAL NA FREE/
   - Unified OLS matrix: unified dataframe for ols/Final_unified_data.csv (549 rows, 13 columns), and fully NA-free version FINAL NA FREE/FINAL_Na_free_dataset.csv (132 rows, 12 columns).

4) Feature selection
   - Indicators are selected via a combination of filtering and manual curation (handy_picked_variables.txt).
   - Some noisy/scarce indicators are excluded (e.g., Energy use is dropped due to missingness after 2014–15).

5) Model fitting
   - Using statsmodels OLS (OLS(y, X)), where y = years_before_the_war and X are the selected indicators.
   - The coefficients are used for prediction; an OLS summary can be written to OLS_results.txt.

6) Prediction
   - The main entry points in war_Predictor_2.py are:
     * War_Predictor_2(year, country1, country2) -> predicts proximity for a dyad in a given year.
     * Internally calls War_Predictor_X_Year_CORRECTED(...) to read {country}.csv from data for predictions/{year}/, assemble the feature vector, and apply the learned coefficients.
     * By design, it averages predictions for both sides of the dyad and applies an empirical offset (about -3.7) observed during calibration.

7) Backtesting
   - test_the_model(conflicts) iterates over all rows in csv_of_wars.txt, runs predictions, and writes Prediction_accuracy_of_War_Predictor.csv with model residuals (closer to 0 is better).

---

## Data Sources

- World Development Indicators (WDI), World Bank — macroeconomic, demographic, and financial indicators per country and year.
- War list — manually compiled mapping of historical interstate conflicts to their participants and start years.

See: 2023 data/WDICSV.csv, big data/, countries/, and intermediate folders noted above.

---

## Repository Layout

```
war Predictor/
├─ war_Predictor_2.py                 # main Python pipeline + model + evaluation
├─ war_Predictor__OLD_VERSION.py      # earlier iteration (kept for reference)
├─ war_Predictor_2.r                  # alternative experiments in R
├─ csv_of_wars.txt                    # list of 28 conflicts with start years
├─ handy_picked_variables.txt         # curated list of indicators
├─ OLS_results.txt                    # optional OLS summary output
├─ Prediction_accuracy_of_War_Predictor.csv # produced by evaluation
├─ data for predictions/              # per-year folders with {Country}.csv
├─ filtered data/                     # per-country filtered WDI exports
├─ big data/                          # raw WDI per-country CSVs
├─ 2023 data/WDICSV.csv               # the WDI bulk dump (2023)
├─ unified dataframe for ols/
│  └─ Final_unified_data.csv          # model matrix (with NaNs)
├─ FINAL NA FREE/FINAL_Na_free_dataset.csv  # NA-free training matrix
├─ Formated and Na filtered/          # cleaned intermediate datasets
└─ (additional notes .txt files)      # build notes, NA stats, etc.
```

The project includes a large number of CSVs (many thousands) because each country/year gets its own prepared file for fast lookup during prediction.

---

## Model

- Type: OLS linear regression (statsmodels.api.OLS).
- Target: years_before_the_war.
- Features: a handpicked subset of WDI indicators (see below).
- Training matrices:
  - unified dataframe for ols/Final_unified_data.csv — 549 x 13 with missingness.
  - FINAL NA FREE/FINAL_Na_free_dataset.csv — 132 x 12, NA-free for robust fitting.
- Prediction combination: per-dyad prediction = mean of both countries’ predictions - 3.7 (empirical offset; see code comment in War_Predictor_X_Year_CORRECTED).

You can optionally write the OLS summary to OLS_results.txt (disabled in code by default).

---

## Key Variables

From handy_picked_variables.txt (selection used in the final runs):

- Literacy rate, adult total (% of people ages 15+)
- Military expenditure (% of GDP)
- GDP growth (annual %)
- GDP per capita growth (annual %)
- Real interest rate (%)
- Central government debt, total (% of GDP)
- Population, female (% of total population)
- Age dependency ratio (% of working-age population)
- Trade (% of GDP)
- Energy imports, net (% of energy use) (often dropped due to post-2015 gaps)
- Unemployment, male (% of male labor force) (national estimate)
- CPIA gender equality rating (1=low to 6=high)
- Inflation, GDP deflator (annual %)
- Urban population (% of total population)
- Official exchange rate (LCU per US$, period average)

The code constructs included_vars by taking the training matrix columns and discarding explicitly excluded variables when necessary.

---

## Installation

Python: 3.10+ recommended.

Minimal requirements (the pinned environment in requierements.txt is broader than needed):

```bash
pip install numpy pandas statsmodels wbdata
```

- tkinter is imported but not essential for headless runs.
- If you plan to rebuild the WDI layer from scratch, wbdata will help (already included above).

A larger pinned set of packages is provided in requierements.txt (note the filename spelling).

---

## Quick Start

1) Clone / unpack this repository and ensure current directory is "war Predictor/".
2) Ensure per-year prediction data exists under "data for predictions/<YEAR>/{Country}.csv". The repo already contains many prepared years.
3) Run the main script to produce the evaluation CSV:

```bash
python war_Predictor_2.py
```

This will read csv_of_wars.txt, run backtests across wars, and write:

```
Prediction_accuracy_of_War_Predictor.csv
```

### Programmatic usage

```python
from war_Predictor_2 import War_Predictor_2

# Example: predict proximity for the 2003 dyad (United States vs Iraq)
pred = War_Predictor_2("2003", "United States", "Iraq")
print("Predicted years before war (dyad-level):", pred)
```

The function looks inside data for predictions/2003/United States.csv and .../Iraq.csv, assembles the feature vectors, applies OLS coefficients, averages both predictions, then subtracts the offset (approx -3.7).

---

## Reproducing the Dataset

To rebuild the end-to-end pipeline (if starting from raw WDI):

1) Prepare war windows
   - Use csv_of_wars.txt to compute for each dyad the t-10 ... t-1 windows and label years_before_the_war accordingly.

2) Filter country CSVs
   - filter_country_data(country, the_path, ...) in war_Predictor_2.py trims each country’s WDI to:
     * Only Indicators of interest.
     * Only Years of interest (globally, or per-conflict window).
   - Save to filtered data/ one file per country.

3) Unify model matrix
   - Merge filtered frames into unified dataframe for ols/Final_unified_data.csv.
   - Optionally create an NA-free subset in FINAL NA FREE/FINAL_Na_free_dataset.csv for stable OLS training.

4) Fit OLS
   - In code, y = final_data["years_before_the_war"] and X = final_data[included_vars], then OLS(y, X).fit().
   - Persist coefficients (the code keeps them in memory and uses them directly for prediction).

5) Assemble per-year prediction panels
   - For each YEAR, build data for predictions/YEAR/{Country}.csv with the same included_vars.
   - These are used by War_Predictor_2(year, country1, country2) at inference time.

---

## Evaluating Accuracy

Run:

```bash
python war_Predictor_2.py
```

This calls test_the_model(conflicts):
- Iterates all rows in csv_of_wars.txt.
- For each conflict, computes a prediction for its start year and dyad.
- Writes residuals (reported as 0 - prediction) to Prediction_accuracy_of_War_Predictor.csv.
- Rows may be "Na" if a year/country panel is missing (e.g., 1960-1961 are intentionally skipped in this code path to save rebuild time).

---

## Limitations & Caveats

- Causality vs correlation: OLS offers correlation, not causality. Interpret coefficients carefully.
- Feature leakage: Pay attention to indicator definitions (e.g., realized-year statistics could inadvertently leak information if compiled ex-post). Here we constrain windows to pre-war years, but the source publication process can still introduce issues.
- Missing data: Some indicators (e.g., Energy use) are sparse after 2014-15, reducing usable sample size. The project keeps both a full matrix (with NaNs) and an NA-free subset.
- Static coefficients: The model is fit once on historical windows; it is not a rolling/expanding forecast model.
- Country naming: Names must match World Bank conventions (e.g., Vietnam -> Viet Nam). See in-code notes for manual name normalization.
- Offset: The final dyad score subtracts approx 3.7 based on calibration; adjust if you change features or training matrices.

---

## Roadmap

- Switch to regularized regression (Ridge/LASSO/Elastic-Net) for better stability under multicollinearity.
- Add time-series cross-validation (rolling windows) and out-of-sample tests by war cohort.
- Upgrade to a dyadic panel with interaction terms and lag structures (e.g., deltas of indicators).
- Automate country name normalization.
- Package as a CLI with argparse (e.g., predict --year 2003 --a "United States" --b "Iraq").
- Optional web UI for interactive exploration.

---

## License & Attribution

- License: add your preferred license (e.g., MIT).
- Data: World Development Indicators © The World Bank.
- Citation: If you use this code or data, please cite the World Bank WDI and this repository.

---

### Maintainer

- Author: Turan Isgandarli, Dachi Gomiashvili, Isabella Levkovic, Rasul Karimov
- Project: War Predictor — empirical exploration of macro indicators as early signals of interstate conflict.
