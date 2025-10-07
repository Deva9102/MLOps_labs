# Airflow Lab – Random Forest on Breast Cancer (CSV)

A minimal Airflow project that trains a **RandomForestClassifier** on the classic **Breast Cancer Wisconsin (diagnostic)** dataset, logs evaluation metrics, saves the trained model, and emails a simple “Success!” notice when the run finishes.

## Project layout

# Airflow Lab – Random Forest on Breast Cancer (CSV)

A minimal Airflow project that trains a **RandomForestClassifier** on the classic **Breast Cancer Wisconsin (diagnostic)** dataset, logs evaluation metrics, saves the trained model, and emails a simple “Success!” notice when the run finishes.

## Project layout

Lab_3/
├─ dags/
│ ├─ my_dag.py
│ ├─ data/
│ │ └─ breast_cancer.csv
│ ├─ model/
│ │ └─ model.sav # created after first successful run
│ ├─ src/
│ │ ├─ model_development.py
│ │ └─ success_email.py
│ └─ templates/
│ ├─ success.html
│ └─ failure.html
└─ requirements.txt

---

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

3. Configure SMTP Connection for Email
The DAG includes a success email notification step, which requires an Airflow connection named email_smtp.

Via Airflow UI

Navigate to Admin → Connections → +.

Set the following fields:

Conn Id: email_smtp

Conn Type: SMTP

Host: smtp.gmail.com (Example)

Port: 587

Login: your_email@gmail.com

Password: your_app_password (For Gmail, you must use an App Password, not your primary account password.)

Extra: {"timeout": 30} (Optional)

Via Airflow CLI (Example)

airflow connections add email_smtp \
  --conn-type SMTP \
  --conn-host smtp.gmail.com \
  --conn-login your_email@gmail.com \
  --conn-password 'your_app_password' \
  --conn-port 587

4. Running the DAG
Start Airflow Services

Open two separate terminals for the Webserver and the Scheduler.

Start Webserver:

airflow webserver --port 8080

Start Scheduler (in a new terminal):

airflow scheduler

Trigger the DAG

You can trigger the DAG using the CLI or the Webserver UI.

CLI Trigger:

airflow dags trigger Airflow_Lab3_new2

UI Trigger: Open http://localhost:8080, find the DAG named Airflow_Lab3_new2, and click the Trigger DAG button.

5. Where to See Results
Metrics

Check the task logs for the calculated model performance metrics:

Location: DAG → last run → task build_save_model_task → Logs.

Example Output:

Metrics -> accuracy: 0.9415, precision: 0.9450, recall: 0.9626
Saved model: dags/model/model.sav

Email

A simple “Success!” email will be sent to the address configured in success_email.py if the DAG completes successfully and the email_smtp connection is correct.

6. Customization
Model : Used RandomForestClassifier(...)in dags/src/model_development.py.

More Metrics/Artifacts: Compute and use print(...) or a logging statement within the build_model(...) function to output additional metrics.

Different Dataset: Placed a new CSV file (breast_cancer.csv) in dags/data/ and adjust the load_data(...) function in dags/src/data_processing.py to handle the new format.

