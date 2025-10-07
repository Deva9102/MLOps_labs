# Airflow Lab – Random Forest on Breast Cancer

A minimal Airflow project that trains a **RandomForestClassifier** on the classic **Breast Cancer Wisconsin (diagnostic)** dataset, logs evaluation metrics, saves the trained model, and emails a simple “Success!” notice when the run finishes.


## Project Layout

```
Lab_3/
├─ dags/
│  ├─ my_dag.py
│  ├─ data/
│  │  └─ breast_cancer.csv
│  ├─ model/
│  │  └─ model.sav            
│  ├─ src/
│  │  ├─ model_development.py
│  │  └─ success_email.py
│  └─ templates/
│     ├─ success.html
│     └─ failure.html
└─ requirements.txt
```

> Make sure all of the above lives under your **`$AIRFLOW_HOME/dags/`** folder, or update `dags_folder` in `airflow.cfg`.

## What it does

1. **Load CSV** (`breast_cancer.csv`)
2. **Preprocess & split** (train/test with standard scaling)
3. **Train** a Random Forest
4. **Log metrics** (Accuracy, Precision, Recall) to task logs
5. **Save model** to `dags/model/model.sav`
6. **Email** a simple success message via an Airflow SMTP connection (`email_smtp`)

---

## Prerequisites

- Python 3.10+
- Apache Airflow (tested with 2.x)
- Ability to create an SMTP connection in Airflow (e.g., Gmail app password or any SMTP server)

## DAG Location

Ensure the project's DAG file (my_dag.py) and associated source code (dags/src/) are located under the $AIRFLOW_HOME/dags directory. If you place them elsewhere, you must update the dags_folder setting in your airflow.cfg file.

---

## Quickstart

### 1) Environment

```bash
# Python 3.10+ recommended
python3 -m venv airflow_venv
source airflow_venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

**Example `requirements.txt`:**
```txt
apache-airflow==2.9.2
pandas>=2.0.0
numpy>=1.24.0
scikit-learn>=1.3.0
joblib>=1.3.0
```

### 2) Initialize Airflow

```bash
# Optional, if not set globally:
export AIRFLOW_HOME=~/airflow

airflow db init

# Create an admin user (edit values as needed):
airflow users create   --username admin   --firstname Admin   --lastname User   --role Admin   --email you@example.com
```

### 3) Configure SMTP Connection (for success email)

This project expects an Airflow **Connection** with Conn Id **`email_smtp`**.

**Via UI:**
- Go to **Admin → Connections → +**
- **Conn Id**: `email_smtp`  
- **Conn Type**: `SMTP`  
- **Host**: `smtp.gmail.com` (example)  
- **Port**: `587`  
- **Login**: `your_email@gmail.com`  
- **Password**: *Gmail App Password* (not your primary password)  
- **Extra (optional)**:
  ```json
  {"timeout": 30}
  ```

**Via CLI:**
```bash
airflow connections add email_smtp   --conn-type SMTP   --conn-host smtp.gmail.com   --conn-login your_email@gmail.com   --conn-password 'your_app_password'   --conn-port 587
```

> Use **Port 587** with STARTTLS. If you use 465 (SSL), you may hit `SSLError: WRONG_VERSION_NUMBER`.

---

## Running

Open two terminals:

**Terminal A – Webserver**
```bash
source airflow_venv/bin/activate
airflow webserver --port 8080
```

**Terminal B – Scheduler**
```bash
source airflow_venv/bin/activate
airflow scheduler
```

Trigger the DAG:

**CLI**
```bash
airflow dags trigger Airflow_Lab3_new2
```

**UI**  
Visit `http://localhost:8080`, find **`Airflow_Lab3_new2`**, click **Trigger DAG**.

---

## Where to See Results

### Metrics
- UI → DAGs → **Airflow_Lab3_new2** → Last Run → Task **`build_save_model_task`** → **Logs**
- Example:
  ```
  Metrics -> accuracy: 0.9415, precision: 0.9450, recall: 0.9626
  Saved model: dags/model/model.sav
  ```

### Model Artifact
- Saved to: `dags/model/model.sav`

### Email
- On success, a simple HTML “Success!” email is sent using **`email_smtp`** to the recipient defined in `src/success_email.py`.

### 6. Customization
Model : Used RandomForestClassifier(...)in dags/src/model_development.py.

More Metrics/Artifacts: Compute and use print(...) or a logging statement within the build_model(...) function to output additional metrics.

Different Dataset: Placed a new CSV file (breast_cancer.csv) in dags/data/ and adjust the load_data(...) function in dags/src/data_processing.py to handle the new format.
