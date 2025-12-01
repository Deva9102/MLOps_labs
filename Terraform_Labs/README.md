# Terraform GCP Lab – Timezone Converter App

This lab uses **Terraform** to create a small **GCP** setup and automatically run a **Flask timezone converter** on a VM.

## What Terraform Creates

Defined in `main.tf`:

- **Compute Engine VM** `terraform-vm`
  - `e2-micro`, Debian 11, in `us-central1-a`
  - Tag: `timezone-app`
  - Startup script that:
    - Installs Python + pip
    - Installs `Flask` and `pytz`
    - Writes `/opt/timezone_app/timezone_web.py`
    - Runs `python3 timezone_web.py` on port **8080**
- **Firewall rule** `allow-http-8080`
  - Network: `default`
  - Allows TCP **8080** from `0.0.0.0/0`
  - Targets VMs with tag `timezone-app`
- **Storage bucket**
  - `terraform-lab-bucket-devadarshini-12345` in `us-central1`
  - `force_destroy = true` (lab only)

Terraform also defines outputs:

- `vm_external_ip` – external IP of the VM  
- `app_url` – `http://<external-ip>:8080` for the Flask app

## Project Layout

```text
Terraform_Labs/
├── app/
│   ├── timezone_helper.py   # CLI timezone converter
│   └── timezone_web.py      # Flask timezone converter
├── main.tf                  # Terraform config (VM, firewall, bucket, startup script, outputs)
├── .terraform.lock.hcl      # Provider lock file
└── requirements.txt         # Flask + pytz for local use
```

(State files, `.terraform/`, `.venv/`, etc. are ignored by `.gitignore`.)

## How to Run

From the repo root:

```bash
cd MLOps_labs/Terraform_Labs
```

(State files, `.terraform/`, `.venv/`, etc. are ignored by `.gitignore`.)

## How to Run

From the repo root:

    cd MLOps_labs/Terraform_Labs

### Authenticate to GCP

Either user auth:

    gcloud auth application-default login
    gcloud config set project YOUR_PROJECT_ID

Or export a service-account key:

    export GOOGLE_APPLICATION_CREDENTIALS="/path/to/key.json"

Make sure `provider "google"` in `main.tf` has the correct `project` ID.

### Terraform workflow

    terraform init
    terraform plan
    terraform apply

After `apply` you should see something like:

    Outputs:
    app_url        = "http://<EXTERNAL_IP>:8080"
    vm_external_ip = "<EXTERNAL_IP>"

### Open the app

Visit `app_url` in the browser and use the form to convert between timezones.

### Destroy when done

    terraform destroy

This removes the VM, firewall rule, and bucket.

## CLI Helper (Optional)

Run the CLI converter:

    cd Terraform_Labs/app
    python3 -m venv .venv && source .venv/bin/activate
    pip install -r ../requirements.txt
    python3 timezone_helper.py

## Extra Enhancements I Added

On top of the basic lab requirements, this repo also:

- Adds a **startup script** that installs Python, Flask, and `pytz` and runs a **Flask timezone converter** on port `8080`.
- Creates a **firewall rule** to allow HTTP traffic on `8080` only to the tagged VM (`timezone-app`).
- Exposes a **Terraform output** `app_url` so the browser link appears directly after `terraform apply`.
- Includes:
  - `app/timezone_web.py` – Flask web app for timezone conversion.
  - `app/timezone_helper.py` – CLI version of the same converter.
  - `requirements.txt` – to run the app locally in a virtualenv.
