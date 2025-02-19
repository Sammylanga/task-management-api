# Task Management API

## 🚀 Setup Environment

### 1️⃣ Create & Activate Virtual Environment
```sh
python -m venv venv
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate     # On Windows
```

### 2️⃣ Clone the Project & Install Dependencies
```sh
git clone https://github.com/your-repo/task-management-api.git
cd task_management
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### 3️⃣ Run Tests
```sh
python manage.py test
```
📌 This runs both unit tests (`users/test.py` and `tasks/test.py`) and integration tests (`tests/test_views.py`).

---

## 🛠️ Database Setup (PostgreSQL)

### 1️⃣ Verify if PostgreSQL is Running
```sh
brew services list  # Check status
brew services start postgresql  # Start PostgreSQL (if not running)
```

### 2️⃣ Log into PostgreSQL & Create a Database
```sh
psql -U postgres
```
Then, run:
```sql
CREATE DATABASE your_database_name;
CREATE ROLE your_database_user WITH LOGIN PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE your_database_name TO your_database_user;
```

### 3️⃣ Modify `DATABASES` in `settings.py`
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_database_name',
        'USER': 'your_database_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 4️⃣ Apply Migrations
```sh
python manage.py makemigrations
python manage.py migrate
```

---

## 🔑 Django Admin Setup

Create a superuser to access Django Admin:
```sh
python manage.py createsuperuser
```
📌 Provide the following details:
```sh
Username: admin
Email address: admin@gmail.com
Password: password123
Password (again): password123
```

---

## 🚀 Running the Server
```sh
python manage.py runserver
```

📌 Access the API at: `http://127.0.0.1:8000/`

---

## 🛠️ Testing APIs (Postman Collection)

You can test the API using Postman:

[![Run in Postman](https://run.pstmn.io/button.svg)](https://www.postman.com/altimetry-geoscientist-45514994/task-management-apis/collection/gm55p6h/task-management-apis?action=share&creator=22767547)

---

## 📜 Logs
Check logs for debugging:
- **Application Logs:** `logs/app.log`
- **Error Logs:** `logs/errors.log`

---



