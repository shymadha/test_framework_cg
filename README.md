# 🧠 Agentic AI Framework – Setup & Usage Guide

## 🚀 Full Setup & Run Steps

### 1. Create a Python Virtual Environment
```bash
python -m venv venv
```

### Activate Virtual Environment

- Mac/Linux:
```bash
source venv/bin/activate
```

- Windows:
```bash
venv\Scripts\activate
```

---

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

---

### 3. Create .env File

Create a `.env` file in the root directory and add:

```env
API_KEY=""
JIRA_API_TOKEN=""
JIRA_USERNAME=""
JIRA_INSTANCE_URL=""
JIRA_PROJECT_KEY=""
```

---

### 4. Run the Framework
```bash
python framework/ui/ui_agentic_ai.py
```

---

### 5. Run a Test

Example:
```
cpu frequency test
```
<img width="822" height="432" alt="image" src="https://github.com/user-attachments/assets/223e42d2-8d22-4dad-9006-5b114777da76" />
---

### 6. Results

- Final Test Execution Report will be generated after the test run
<img width="822" height="393" alt="image" src="https://github.com/user-attachments/assets/9c010628-29d1-49cf-81b2-bc3b9e6a9853" />

## Note: Tests can only be executed when the machine is connected to a BeagleBone Board.

