from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta
from pydantic import BaseModel

app = FastAPI()

# Clave secreta y algoritmo
SECRET_KEY = "HASRTHKAKS22235412566"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Definir esquema OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Modelos
class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    username: str

# Crear token JWT
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Endpoint para login y obtener token
@app.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Aquí deberías validar contra tu base de datos
    if form_data.username != "denis" or form_data.password != "1234":
        raise HTTPException(status_code=400, detail="Usuario o contraseña incorrectos")
    access_token = create_access_token(data={"sub": form_data.username})
    return {"access_token": access_token, "token_type": "bearer"}

# Dependencia para validar token
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        return User(username=username)
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

# Endpoint protegido
@app.get("/secure-data")
def secure_data(current_user: User = Depends(get_current_user)):
    return {"message": f"Hola {current_user.username}, accediste a datos seguros"}
