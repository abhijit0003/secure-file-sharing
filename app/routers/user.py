from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Path
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os, shutil

from .. import models, schemas, auth, database

router = APIRouter(tags=["Users"])

get_db = database.get_db

# ------------------ SIGNUP ------------------
@router.post("/signup", response_model=schemas.ShowUser)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    user_exist = db.query(models.User).filter(models.User.email == user.email).first()
    if user_exist:
        raise HTTPException(status_code=400, detail="User already exists")
    
    hashed_pw = auth.hash_password(user.password)
    db_user = models.User(email=user.email, password=hashed_pw, role=user.role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


# ------------------ LOGIN ------------------
@router.post("/login", response_model=schemas.Token)
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not db_user or not auth.verify_password(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token_data = {"sub": db_user.email, "role": db_user.role}
    access_token = auth.create_access_token(data=token_data)

    return {"access_token": access_token, "token_type": "bearer"}


# ------------------ UPLOAD FILE (OPS only) ------------------
@router.post("/upload-file")
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    if current_user.role != "ops":
        raise HTTPException(status_code=403, detail="Only OPS users can upload files")

    allowed_extensions = ["pptx", "docx", "xlsx"]
    file_extension = file.filename.split(".")[-1]
    if file_extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"Only {', '.join(allowed_extensions)} files allowed")

    upload_folder = "uploads"
    os.makedirs(upload_folder, exist_ok=True)
    file_path = os.path.join(upload_folder, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    new_file = models.File(
        filename=file.filename,
        user_id=current_user.id
    )
    db.add(new_file)
    db.commit()
    db.refresh(new_file)

    return {"message": "File uploaded successfully", "file_id": new_file.id}


# ------------------ GET DOWNLOAD LINK ------------------
@router.get("/download-file/{file_id}")
def get_download_link(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    if current_user.role != "client":
        raise HTTPException(status_code=403, detail="Only client users can download files")

    file = db.query(models.File).filter(models.File.id == file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    token = auth.create_download_token(file_id=file_id, user_email=current_user.email)
    download_url = f"http://127.0.0.1:8000/secure-download/{token}"

    return {
        "download_link": download_url,
        "message": "success"
    }


# ------------------ SECURE DOWNLOAD ------------------
@router.get("/secure-download/{token}")
def secure_download_file(
    token: str,
    db: Session = Depends(get_db)
):
    try:
        payload = auth.jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        email = payload.get("email")
        file_id = payload.get("file_id")
    except:
        raise HTTPException(status_code=400, detail="Invalid or expired download link")

    user = db.query(models.User).filter(models.User.email == email).first()
    if not user or user.role != "client" or not user.is_verified:
        raise HTTPException(status_code=403, detail="Unauthorized access")

    file = db.query(models.File).filter(models.File.id == file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    file_path = os.path.join("uploads", file.filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")

    return FileResponse(path=file_path, filename=file.filename)


# ------------------ VERIFY EMAIL ------------------
@router.get("/verify-email")
def verify_email(email: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_verified = True
    db.commit()

    return {"message": "Email verified successfully"}


# ------------------ LIST FILES ------------------
@router.get("/list-files")
def list_uploaded_files(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    if current_user.role != "client":
        raise HTTPException(status_code=403, detail="Only client users can view files")

    files = db.query(models.File).all()
    return [{"id": f.id, "filename": f.filename, "uploaded_by": f.user_id} for f in files]