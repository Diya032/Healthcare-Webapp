# Healthcare-Webapp

## Problem Statement

### Use Case Overview
Develop a **cloud-native healthcare application** that automates patient appointment bookings and notifications.  
The system will support **new patient enrollment**, allow upload of **previous medical history**, and enable patients to view doctors’ schedules.

### Key Requirements
- **Users**: Patients and healthcare providers should securely view, book, and manage appointments.  
- **Clinical Data**: Appointment records, patient details (with privacy), and medical files management.  
- **Reminders**: Automatic notifications via email or SMS for upcoming appointments.  

---

## Project Implementation Details

### Architecture
- **Monolithic** structure:
  - `app/` folder contains:
    - `core/`, `crud/`, `routers/`, `schema/`, `main.py`
  - `requirements.txt` at root
- Unlike **microservices** (separate repo/service per domain), all code is centralized in one repo.

### Tech Stack
- **Backend**: FastAPI  
- **Frontend**: HTML, CSS, Java (for Axios requests to backend)  

### Deployment
- **GitHub Branches**
  - `staging`: Staging branch for deployment  
  - `pre-staging`: Clean local dev branch  
  - `add-keyvault/appt/prestaging`: Deployment-ready branch with CORS & Azure Key Vault changes  
  - `main`: Reserved for production (locked & clean, no direct commits)  

- **Deployment Method**: Local Git → Azure App Service remote  
- **Protections**:  
  - `main` & `staging` are locked (require PR review, no direct pushes)  

### Branches Overview
- `appt/prestaging`: Appointment booking + notification logic  
- `add-keyvault/appt/prestaging`: CORS middleware + Azure Key Vault integration  
- `cors-fix`: Local testing for CORS (patient, medical history, auth endpoints)  
- `blol-upload-di`: (typo of blob) Upload medical documents + Document Intelligence background tasks  
- Other small feature branches → already merged  

---

## Azure Usage

- **Components**:
  - Azure App Service (Frontend + Backend)  
  - Azure SQL Database + Server  
  - Azure Communication Service  
  - Azure Storage Account (Blob container)  
  - Azure Document Intelligence  

- **Current workflow**: Azure Portal for deployment  
- **Future scope**: Infrastructure as Code (Terraform)  

---

## Run Commands

Run locally:
```bash
uvicorn app.main:app --reload --log-level debug
````

Test locally:

* API health → [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
* Swagger UI → [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* OpenAPI JSON → [http://127.0.0.1:8000/openapi.json](http://127.0.0.1:8000/openapi.json)
* OpenAPI Viewer → [Swagger Editor Next](https://editor-next.swagger.io/)

Azure startup command:

```bash
gunicorn -w 1 -k uvicorn.workers.UvicornWorker app.main:app \
  --bind 0.0.0.0:${PORT} \
  --log-level debug \
  --capture-output \
  --timeout 120
```

---

## Deployment (Local Git → Azure)

1. Add Azure remote:

```bash
git remote add azure https://<app-name>.scm.centralindia-01.azurewebsites.net:443/<repo>.git
```

2. Verify remote:

```bash
git remote -v
```

3. Push local staging branch → Azure’s master branch:

```bash
git push azure staging:master
```

Note: Azure uses `master` internally, even if GitHub uses `main`.

---

## Blob Upload Testing

Example with `curl` (frontend normally handles upload, this simulates backend-side):

```bash
curl -X PUT -T "path/to/local/file.pdf" ^
  -H "x-ms-blob-type: BlockBlob" ^
  "https://<account>.blob.core.windows.net/<container>/<blob>?<sas_token>"
```

---

## Requirements Management

* Option 1: Freeze dependencies:

```bash
pip freeze > requirements.txt
```

* Option 2: Define exact versions in `requirements.txt` (preferred, used in `staging` branch).

---

## Documentation / Future Reference

* **PPT**: (link available in repo/docs)
* **Notion**: [Healthcare-Webapp Documentation](https://www.notion.so/Healthcare-Webapp-Github-Documentation-266ff227f5df80da8a49d70007450730?source=copy_link)

---


```
