from models import db
from sqlalchemy.orm import sessionmaker, Session
from fastapi import Depends, HTTPException
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from models import Usuario
from main import SECRET_KEY, ALGORITHM, oauth2_schema

def pegar_sessao():
    try:
        Session = sessionmaker(bind=db)
        session = Session()
        yield session
    finally:
        session.close()

def verificar_token(token: str = Depends(oauth2_schema), session: Session = Depends(pegar_sessao)):
    try:
        # jwt.decode já valida a expiração (exp) e lança ExpiredSignatureError
        dic_info = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id_usuario = int(dic_info.get("sub"))
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    usuario = session.query(Usuario).filter(Usuario.id == id_usuario).first()
    if usuario is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return usuario