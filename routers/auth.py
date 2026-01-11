from fastapi import APIRouter, HTTPException
from schemas import LoginRequest, LoginResponse
import os

router = APIRouter()

OWNER_EMAIL = os.getenv("OWNER_EMAIL", "kane.soutoura.ks@gmail.com")
OWNER_PASSWORD = os.getenv("OWNER_PASSWORD", "Test")

@router.post("/login", response_model=LoginResponse)
def login(credentials: LoginRequest):
    """Login with hardcoded owner credentials"""
    if credentials.email == OWNER_EMAIL and credentials.password == OWNER_PASSWORD:
        return LoginResponse(
            success=True,
            message="Connexion réussie",
            user={"email": credentials.email}
        )
    else:
        raise HTTPException(
            status_code=401,
            detail="Seul le propriétaire a accès à cette section"
        )
