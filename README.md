# 🔐 Secure File Sharing System

A secure file-sharing platform that allows two types of users — **OPS Users** and **Client Users** — to interact via file upload and download workflows with access restrictions and encryption.

---

## 🚀 Features

- OPS Users:
  - Login
  - Upload `.pptx`, `.docx`, and `.xlsx` files

- Client Users:
  - Signup (returns secure encrypted URL)
  - Email verification
  - Login
  - Download files using a secure one-time encrypted link
  - List all uploaded files

- Role-based Access Control
- Token-based Authentication
- File uploads saved locally under `/uploads/`
- Secure download links encrypted with expiry

---

## 📁 Folder Structure

.
├── app
│ ├── init.py
│ ├── main.py
│ ├── models.py
│ ├── database.py
│ ├── schemas.py
│ ├── auth.py
│ └── routers
│ └── user.py
├── uploads/ini
│ └── [uploaded files]
├── Secure File Sharing APIs.postman_collection.json
└── README.md


---

## 🔑 Authentication

- Users login using their email and password.
- A Bearer token is issued which must be sent in the `Authorization` header for protected endpoints.
- Token includes role (`ops` or `client`) for access control.

---

## 🔁 Postman Collection

Postman dump included:  
`Secure File Sharing APIs.postman_collection.json`

✅ Organized into folders:
- `Ops User`
- `Client User`

Each request includes:
- Correct body (raw JSON or form-data)
- Headers
- Bearer token authorization

---

### ⚠️ Note on Postman Method Labels

When creating requests in Postman, sometimes:
- It **defaults to GET** when you click “Add Request”
- Even after changing to `POST` in the request method dropdown, the **label in the sidebar still shows GET**
- Renaming the request does **not change** the method label shown in the sidebar

This is **only a cosmetic issue** and **does not affect the functionality** of the exported Postman collection.

✅ In your exported `.postman_collection.json`, the correct method (`POST`, `GET`, etc.) is saved internally — so the API behavior is accurate.

---

## 📝 How to Run Locally

1. Clone the repo  
```bash
git clone https://github.com/yourusername/secure-file-sharing.git
cd secure-file-sharing
```
2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```
3. Install dependencies
```bash
pip install -r requirements.txt
```
4. Run the server
```bash
uvicorn app.main:app --reload
```
The API will run at: http://127.0.0.1:8000

✉️ Email Verification
For now, email verification is mocked through a simple /verify-email?email=... endpoint. This simulates clicking a verification link sent to the user’s email. In production, this would send a real email.