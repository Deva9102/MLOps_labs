# Structured Logging & Dataset Quality Checker

This lab implements a **dataset quality checker** with a **logging setup**.

Given a CSV file, the tool:

- runs a set of **data quality checks** (missing values, numeric ranges, constant columns, etc.),
- prints a **friendly summary** to the console.
- writes a **JSON-structured log file**.

---

## What This Lab Demonstrates

- Separation of concerns:
  - `log_setup.py` handles **logging configuration**.
  - `data_quality.py` handles **data validation logic**.
  - `cli.py` provides a **command-line interface**.
- Dual logging:
  - Human-readable logs to the **console**.
  - Machine-readable **JSON logs** to `logs/data_quality.log`.
- Dataset quality checks that are realistic for ML pipelines:
  - Missing values
  - Numeric ranges & negative values
  - Constant columns
  - High-cardinality categoricals
  - Configurable out-of-range rules

---

## How to Run the Lab 

Follow these steps from the root of the repository (`MLOps_labs`) to set up and run the Data Quality Checker.

---

### 1. Set Up the Environment

Use a **virtual environment** to manage dependencies.

```bash
# Create the virtual environment
python -m venv .venv

# Activate the environment
# Windows:
.venv\Scripts\activate

# macOS / Linux:
source .venv/bin/activate
```

---

### 2. Install Dependencies

Install the required Python packages for the logging lab using the `requirements.txt` file located inside the `Logging_Labs` directory.

```bash
pip install -r Logging_Labs/requirements.txt
```

---

### 3. Run the Dataset Quality Checker

From inside the Logging_Labs folder, run the CLI on the sample dataset:
```bash
cd Logging_Labs
python -m src.cli examples/sample_dataset.csv
```
---

## Project Layout

```text
Logging_Labs/
  examples/
    sample_dataset.csv
    sample_dataset.quality_summary.json 
  logs/
    .gitkeep                              # real log file created at runtime
  src/
    __init__.py
    cli.py                              
    data_quality.py                     
    log_setup.py                 
  .gitignore
  requirements.txt

```
