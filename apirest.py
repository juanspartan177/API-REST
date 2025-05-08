from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()
@app.get("/")
def read_root():
    return {"Hello": "World"}   
# Simulador de base de datos
servicios_db = {}
tokens = {
    "admin-token": {"rol": "Administrador"},
    "orquestador-token": {"rol": "Orquestador"},
    "user-token": {"rol": "Usuario"}
}

# --- MODELOS ---
class Usuario(BaseModel):
    nombre_usuario: str
    contrasena: str

class AutorizacionRequest(BaseModel):
    recursos: List[str]
    rol_usuario: str

class Servicio(BaseModel):
    id: Optional[int]
    nombre: str
    descripcion: str
    endpoints: List[str]

class OrquestarRequest(BaseModel):
    servicio_destino: str
    parametros_adicionales: Optional[dict]

class ReglasRequest(BaseModel):
    reglas: dict

# --- FUNCIONES AUXILIARES ---
def get_rol(authorization: str = Header(...)):
    if authorization not in tokens:
        raise HTTPException(status_code=401, detail="Token inválido")
    return tokens[authorization]["rol"]

# --- ENDPOINTS ---

@app.post("/autenticar-usuario")
def autenticar(usuario: Usuario):
    if usuario.nombre_usuario == "admin" and usuario.contrasena == "1234":
        return {"token": "admin-token", "rol": "Administrador"}
    elif usuario.nombre_usuario == "orq" and usuario.contrasena == "1234":
        return {"token": "orquestador-token", "rol": "Orquestador"}
    elif usuario.nombre_usuario == "user" and usuario.contrasena == "1234":
        return {"token": "user-token", "rol": "Usuario"}
    else:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

@app.post("/autorizar-acceso")
def autorizar(req: AutorizacionRequest):
    if req.rol_usuario == "Administrador" or (req.rol_usuario == "Orquestador" and "orquestar" in req.recursos):
        return {"acceso": True}
    return {"acceso": False}

@app.post("/registrar-servicio")
def registrar(servicio: Servicio, rol: str = Depends(get_rol)):
    if rol != "Administrador":
        raise HTTPException(status_code=403, detail="Acceso denegado")
    servicio.id = len(servicios_db) + 1
    servicios_db[servicio.id] = servicio
    return {"mensaje": "Servicio registrado", "id": servicio.id}

@app.get("/informacion-servicio/{id}")
def obtener_info(id: int, rol: str = Depends(get_rol)):
    if id not in servicios_db:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    return servicios_db[id]

@app.post("/orquestar")
def orquestar(req: OrquestarRequest, rol: str = Depends(get_rol)):
    if rol not in ["Orquestador", "Administrador"]:
        raise HTTPException(status_code=403, detail="No autorizado para orquestar servicios")
    return {
        "mensaje": f"Orquestación ejecutada para {req.servicio_destino}",
        "parametros": req.parametros_adicionales
    }

@app.put("/actualizar-reglas-orquestacion")
def actualizar_reglas(req: ReglasRequest, rol: str = Depends(get_rol)):
    if rol != "Orquestador":
        raise HTTPException(status_code=403, detail="No autorizado para actualizar reglas")
    return {"mensaje": "Reglas de orquestación actualizadas", "reglas": req.reglas}
git log
