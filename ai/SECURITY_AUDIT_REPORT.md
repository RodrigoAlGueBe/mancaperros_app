# SECURITY AUDIT REPORT - Mancaperros App Backend

**Fecha:** 2026-01-09
**Auditor:** Security Audit (Claude Opus 4.5)
**Proyecto:** mancaperros_app FastAPI Backend
**Ruta:** `C:/Users/Rodrigo/Desktop/proyectos/mancaperros_app/code/backend/mancaperros_app/`

---

## RESUMEN EJECUTIVO

Se ha realizado una auditoria de seguridad completa del backend FastAPI. Se han identificado varios problemas de seguridad que requieren atencion, clasificados por severidad.

| Severidad | Cantidad |
|-----------|----------|
| CRITICO   | 1        |
| ALTO      | 4        |
| MEDIO     | 5        |
| BAJO      | 3        |

---

## HALLAZGOS DETALLADOS

### [CRITICO] C-001: Tiempo de Expiracion de Token JWT Excesivo

**Archivo:** `config.py` (linea 80-85) y `app/core/config.py` (linea 80-85)

**Descripcion:**
El tiempo de expiracion de tokens JWT esta configurado en **180 minutos (3 horas)** por defecto, con un maximo permitido de **10080 minutos (1 semana)**. Esto representa un riesgo critico de seguridad ya que:
- Si un token es comprometido, el atacante tiene una ventana de 3 horas o mas para usarlo
- No cumple con las mejores practicas de OWASP que recomiendan tokens de corta duracion (15-30 minutos)

**Codigo Actual:**
```python
access_token_expire_minutes: int = Field(
    default=180,
    ge=1,
    le=10080,  # Max 1 week
    description="JWT access token expiration time in minutes"
)
```

**Correccion Recomendada:**
```python
access_token_expire_minutes: int = Field(
    default=30,  # 30 minutos - recomendacion OWASP
    ge=1,
    le=60,  # Max 1 hora
    description="JWT access token expiration time in minutes (recommended: 15-30)"
)
```

**Impacto:** Si un token es robado, el atacante puede acceder a la cuenta por periodos extendidos.

---

### [ALTO] A-001: Endpoints Sin Autenticacion Exponen Datos Sensibles

**Archivos:**
- `main.py` (lineas 349-366)
- `app/api/v1/endpoints/users.py` (lineas 79-124)

**Descripcion:**
Los siguientes endpoints NO requieren autenticacion y exponen informacion sensible de usuarios:

1. `GET /users/get_user_by_email/{user_email}` - Expone datos de cualquier usuario por email
2. `GET /get_users/` - Lista TODOS los usuarios registrados
3. `GET /exercise_plans/{exercise_plan_id}/rutines` - Expone rutinas sin verificar propiedad

**Codigo Vulnerable (main.py):**
```python
@app.get("/users/get_user_by_email/{user_email}")
def get_user_by_email(user_email, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, user_email=user_email)
    # NO HAY VERIFICACION DE AUTENTICACION
    return db_user

@app.get("/get_users/")
def get_all_users(db: Session = Depends(get_db)):
    db_users = crud.get_users(db=db)
    # NO HAY VERIFICACION DE AUTENTICACION
    return db_users
```

**Correccion Recomendada:**
```python
@app.get("/users/get_user_by_email/{user_email}")
def get_user_by_email(
    user_email: str,
    current_user: Annotated[models.User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    # Solo permitir acceso a datos propios o con rol admin
    if current_user.username != user_email and not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Forbidden")
    db_user = crud.get_user_by_email(db, user_email=user_email)
    return db_user

@app.get("/get_users/")
def get_all_users(
    current_user: Annotated[models.User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    # Solo administradores pueden listar usuarios
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Admin access required")
    return crud.get_users(db=db)
```

---

### [ALTO] A-002: Usuario de Prueba Hardcodeado en Produccion

**Archivo:** `crud.py` (lineas 10-16)

**Descripcion:**
Existe un diccionario `fake_users_db` con un usuario de prueba que incluye un hash de contrasena conocido. Esto representa un backdoor potencial.

**Codigo Vulnerable:**
```python
fake_users_db = {
    "johndoe": {
        "user_name": "johndoe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
    },
}
```

**Nota:** El hash `$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW` corresponde a la contrasena "secret" que es conocida publicamente en ejemplos de FastAPI.

**Correccion Recomendada:**
Eliminar completamente este diccionario del codigo de produccion:
```python
# ELIMINAR TODO ESTE BLOQUE EN PRODUCCION
# fake_users_db = { ... }
```

---

### [ALTO] A-003: SECRET_KEY con Valor por Defecto Inseguro

**Archivo:** `config.py` y `app/core/config.py` (linea 70-73)

**Descripcion:**
Aunque se lee de variables de entorno, existe un valor por defecto que podria usarse si no se configura correctamente.

**Codigo Actual:**
```python
secret_key: str = Field(
    default="CHANGE_ME_IN_PRODUCTION_USE_SECURE_RANDOM_KEY",
    description="Secret key for JWT token signing."
)
```

**Problema:**
- El validador emite solo un `warning`, no impide el inicio
- En produccion, si no se configura, se usara este valor conocido

**Correccion Recomendada:**
```python
@field_validator("secret_key")
@classmethod
def validate_secret_key(cls, v: str, info) -> str:
    """Fail if using default secret key in production."""
    if v == "CHANGE_ME_IN_PRODUCTION_USE_SECURE_RANDOM_KEY":
        # Verificar si estamos en produccion desde otra fuente
        import os
        env = os.getenv("ENVIRONMENT", "development")
        if env.lower() == "production":
            raise ValueError(
                "SECRET_KEY must be set in production! "
                "Generate with: openssl rand -hex 32"
            )
        import warnings
        warnings.warn(
            "Using default SECRET_KEY! This is insecure for production.",
            UserWarning
        )
    elif len(v) < 32:
        raise ValueError("SECRET_KEY must be at least 32 characters long")
    return v
```

---

### [ALTO] A-004: settings.py Usa Valor por Defecto Inseguro

**Archivo:** `settings.py` (linea 11)

**Descripcion:**
El archivo `settings.py` (legado) usa "default_secret_key" como valor por defecto si no existe la variable de entorno.

**Codigo Vulnerable:**
```python
SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")
```

**Correccion Recomendada:**
```python
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY environment variable is required")
```

O mejor, eliminar este archivo y usar solo `config.py` con pydantic-settings.

---

### [MEDIO] M-001: Configuracion CORS Demasiado Permisiva

**Archivo:** `config.py` (lineas 142-150)

**Descripcion:**
La configuracion CORS permite `*` para metodos y headers, lo cual es excesivamente permisivo.

**Codigo Actual:**
```python
cors_allow_methods: List[str] = Field(
    default=["*"],
    description="Allowed HTTP methods for CORS"
)

cors_allow_headers: List[str] = Field(
    default=["*"],
    description="Allowed HTTP headers for CORS"
)
```

**Correccion Recomendada:**
```python
cors_allow_methods: List[str] = Field(
    default=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    description="Allowed HTTP methods for CORS"
)

cors_allow_headers: List[str] = Field(
    default=["Authorization", "Content-Type", "Accept", "Origin", "X-Requested-With"],
    description="Allowed HTTP headers for CORS"
)
```

---

### [MEDIO] M-002: Validacion de Input Insuficiente en Endpoints

**Archivo:** `main.py`, `app/api/v1/endpoints/routines.py`

**Descripcion:**
Varios endpoints aceptan `dict` como parametro en lugar de schemas Pydantic validados:

```python
@app.post("/users/end_routine")
async def end_routine(..., exercises_summary:dict, ...):
    # exercises_summary no esta validado

@app.post("/exercise_plan_global_full")
async def create_exercise_plan_global_full(..., exercise_plan_global_full_dict:dict, ...):
    # exercise_plan_global_full_dict no esta validado
```

**Correccion Recomendada:**
Crear schemas Pydantic especificos:
```python
from pydantic import BaseModel, validator, constr

class ExerciseSummary(BaseModel):
    routine_group: constr(min_length=1, max_length=100)
    exercises: dict  # Mejor: crear un schema anidado especifico

    @validator('routine_group')
    def validate_routine_group(cls, v):
        # Validacion adicional
        if not v.replace("_", "").isalnum():
            raise ValueError("routine_group contains invalid characters")
        return v

@app.post("/users/end_routine")
async def end_routine(
    current_user: CurrentUser,
    exercises_summary: ExerciseSummary,  # Ahora validado
    db: DbSession
):
    ...
```

---

### [MEDIO] M-003: Enumeracion de Usuarios Posible

**Archivo:** `app/api/v1/endpoints/auth.py` (lineas 56-57)

**Descripcion:**
El endpoint de login revela si un usuario existe o no mediante mensajes de error diferentes:
- "No user found" - usuario no existe
- "Incorrect username or password" - usuario existe pero contrasena incorrecta

**Codigo Vulnerable:**
```python
if not user_db:
    raise HTTPException(status_code=400, detail="No user found")
# ...
if not user:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
    )
```

**Correccion Recomendada:**
```python
# Usar el mismo mensaje para ambos casos
error_message = "Invalid username or password"
if not user_db:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=error_message,
        headers={"WWW-Authenticate": "Bearer"},
    )
# ...
if not user:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=error_message,
        headers={"WWW-Authenticate": "Bearer"},
    )
```

---

### [MEDIO] M-004: Falta Rate Limiting en Endpoints Sensibles

**Descripcion:**
No existe rate limiting en endpoints criticos como:
- `/token` (login) - vulnerable a ataques de fuerza bruta
- `/users/` (registro) - vulnerable a spam de cuentas

**Correccion Recomendada:**
Implementar rate limiting con `slowapi`:

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/token")
@limiter.limit("5/minute")  # Max 5 intentos por minuto
async def login_for_access_token(request: Request, ...):
    ...

@app.post("/users/")
@limiter.limit("3/hour")  # Max 3 registros por hora desde misma IP
def create_user(request: Request, ...):
    ...
```

Agregar a `requirements.txt`:
```
slowapi>=0.1.9
```

---

### [MEDIO] M-005: Falta de Headers de Seguridad HTTP

**Descripcion:**
La aplicacion no configura headers de seguridad HTTP importantes.

**Correccion Recomendada:**
Agregar middleware para headers de seguridad:

```python
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response

app.add_middleware(SecurityHeadersMiddleware)
```

---

### [BAJO] B-001: Uso de datetime.utcnow() Deprecado

**Archivo:** `app/core/security.py` (lineas 71, 73)

**Descripcion:**
`datetime.utcnow()` esta deprecado en Python 3.12+. Usar `datetime.now(timezone.utc)`.

**Codigo Actual:**
```python
expire = datetime.utcnow() + expires_delta
```

**Correccion Recomendada:**
```python
from datetime import datetime, timezone

expire = datetime.now(timezone.utc) + expires_delta
```

---

### [BAJO] B-002: Codigo de Debug en Produccion

**Archivo:** `main.py` (linea 520)

**Descripcion:**
Existe un `print()` de debug que no deberia estar en produccion:
```python
print("********************" + str(type(active_exercise_plan.routine_group_order)))
```

**Correccion:**
Remover o reemplazar con logging apropiado:
```python
logger.debug(f"routine_group_order type: {type(active_exercise_plan.routine_group_order)}")
```

---

### [BAJO] B-003: Funciones de Prueba en Produccion

**Archivo:** `crud.py` (lineas 261-271)

**Descripcion:**
Existen funciones de prueba como `fake_decode_token`, `fake_hash_password` que no deberian estar en produccion.

**Correccion:**
Mover estas funciones a un modulo de tests o eliminarlas del codigo de produccion.

---

## DEPENDENCIAS - ESTADO DE SEGURIDAD

### Dependencias Actualizadas Correctamente

| Dependencia | Version | Estado | Notas |
|-------------|---------|--------|-------|
| python-jose | >=3.4.0 | OK | Resuelve CVE-2024-33663, CVE-2024-33664 |
| starlette | >=0.49.1 | OK | Resuelve CVE-2025-54121 (DoS) |
| fastapi | >=0.115.0 | OK | Version segura |
| SQLAlchemy | >=2.0.36 | OK | Parches de seguridad |
| bcrypt | >=4.2.0 | OK | Version actualizada |

### Recomendaciones Adicionales

Agregar al `requirements.txt`:
```
# Security monitoring
safety>=2.3.0           # Escaneo de vulnerabilidades
bandit>=1.7.0           # Analisis estatico de seguridad Python

# Rate limiting
slowapi>=0.1.9          # Rate limiting para FastAPI

# Security headers
secure>=0.3.0           # Headers de seguridad HTTP
```

---

## RESUMEN DE INYECCION SQL

**Estado: SEGURO**

El proyecto utiliza SQLAlchemy ORM correctamente, lo que previene inyeccion SQL:
- Todas las consultas usan el ORM de SQLAlchemy (`db.query()`, `.filter()`)
- Los parametros se pasan como argumentos, no concatenados en strings
- No se detectaron consultas SQL raw con interpolacion de variables

Ejemplo de codigo seguro encontrado:
```python
def get_user_by_email(db: Session, user_email: str):
    return db.query(models.User).filter(models.User.email == user_email).first()
```

---

## LISTA DE VERIFICACION PARA PRODUCCION

Antes de desplegar a produccion, verificar:

- [ ] `SECRET_KEY` es un valor aleatorio de 64 caracteres hexadecimales
- [ ] `DB_PASSWORD` ha sido cambiada y es segura
- [ ] `ENVIRONMENT=production`
- [ ] `DEBUG=false`
- [ ] `ACCESS_TOKEN_EXPIRE_MINUTES=30` (o menos)
- [ ] CORS solo permite origenes de produccion especificos
- [ ] Rate limiting esta habilitado
- [ ] Headers de seguridad HTTP estan configurados
- [ ] Usuarios de prueba han sido eliminados
- [ ] Logging en produccion no incluye datos sensibles
- [ ] HTTPS esta forzado en produccion

---

## PROXIMOS PASOS RECOMENDADOS

### Prioridad Inmediata (esta semana)
1. Reducir tiempo de expiracion de token JWT a 30 minutos
2. Agregar autenticacion a endpoints expuestos
3. Eliminar usuario de prueba hardcodeado
4. Implementar rate limiting

### Prioridad Alta (proximo sprint)
1. Unificar mensajes de error para prevenir enumeracion de usuarios
2. Crear schemas Pydantic para validacion de entrada
3. Agregar headers de seguridad HTTP
4. Configurar CORS de forma restrictiva para produccion

### Prioridad Media (siguiente mes)
1. Implementar refresh tokens para mejor manejo de sesiones
2. Agregar logging de seguridad centralizado
3. Implementar sistema de roles/permisos (RBAC)
4. Configurar monitoreo de seguridad (SIEM)

---

**Fin del Reporte de Auditoria de Seguridad**
