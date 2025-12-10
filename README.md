# E2EE Drive – FastAPI Backend (Google ID Token Auth)

Secure folder & file management backend with Google ID Token–based authentication.

## 🚀 Quick Start (Windows + PowerShell)

### 1️⃣ Allow PowerShell scripts (only once)
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser

### 2️⃣ Create & activate virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1

### 3️⃣ Install dependencies
pip install -r requirements.txt

### 4️⃣ Set required environment variables
$env:GOOGLE_CLIENT_ID="your-client-id.apps.googleusercontent.com"
$env:DATABASE_URL="sqlite:///./e2ee_drive.db"

### 5️⃣ Run the FastAPI server (main.py)
uvicorn main:app --reload --port 8000

Backend available at:
http://localhost:8000

---

## 📡 API Endpoints

### 🔐 Authentication Header (Required)
Authorization: Bearer <Google_ID_Token>

### 📁 Folder Management
POST /folders       - Create folder  
GET  /folders       - List child folders  
GET  /folders/all   - List all folders of user  

---

## 📝 Notes
- Google ID Token verification handled using google-auth.
- CORS allows http://localhost:3000.
- Works seamlessly with the Next.js frontend.

---

## 🗂 Example Project Structure
e2ee-drive-backend/
│   main.py
│   requirements.txt
│   README.md
│
├── routes/
│     folders.py
│     auth.py
│
├── models/
│     folder.py
│     user.py
│
└── utils/
      verify_google_token.py

---

## 🧰 Development Mode
uvicorn main:app --reload --port 8000
