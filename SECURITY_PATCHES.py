"""
SECURITY PATCHES - Mancaperros App
==================================

Este archivo contiene los parches de seguridad que deben aplicarse manualmente
a los archivos del proyecto. Sigue las instrucciones para cada seccion.

Fecha de Auditoria: 2026-01-09
"""

# =============================================================================
# PATCH 1: Reducir tiempo de expiracion de token JWT (CRITICO)
# =============================================================================
# Archivo: config.py Y app/core/config.py
# Ubicacion: Linea ~80-85
#
# BUSCAR ESTE CODIGO:
PATCH1_BEFORE = '''
    access_token_expire_minutes: int = Field(
        default=180,
        ge=1,
        le=10080,  # Max 1 week
        description="JWT access token expiration time in minutes"
    )
'''

# REEMPLAZAR POR ESTE CODIGO:
PATCH1_AFTER = '''
    access_token_expire_minutes: int = Field(
        default=30,  # SECURITY: Reduced to 30 minutes (OWASP recommendation)
        ge=1,
        le=60,  # SECURITY: Max 1 hour for security best practices
        description="JWT access token expiration time in minutes (recommended: 15-30)"
    )
'''

# =============================================================================
# PATCH 2: Eliminar usuario de prueba hardcodeado (ALTO)
# =============================================================================
# Archivo: crud.py
# Ubicacion: Linea ~10-16
#
# ELIMINAR COMPLETAMENTE ESTE BLOQUE:
PATCH2_DELETE = '''
fake_users_db = {   #Rod 20/08/2023 added fake user for testing propouses
    "johndoe": {
        "user_name": "johndoe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
    },
}
'''

# =============================================================================
# PATCH 3: Mejorar validacion de SECRET_KEY (ALTO)
# =============================================================================
# Archivo: config.py Y app/core/config.py
# Ubicacion: Buscar el validador @field_validator("secret_key")
#
# BUSCAR ESTE CODIGO:
PATCH3_BEFORE = '''
    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Warn if using default secret key."""
        if v == "CHANGE_ME_IN_PRODUCTION_USE_SECURE_RANDOM_KEY":
            import warnings
            warnings.warn(
                "Using default SECRET_KEY! This is insecure. "
                "Set SECRET_KEY environment variable with: openssl rand -hex 32",
                UserWarning,
                stacklevel=2
            )
        return v
'''

# REEMPLAZAR POR ESTE CODIGO:
PATCH3_AFTER = '''
    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Validate secret key is secure."""
        import os
        if v == "CHANGE_ME_IN_PRODUCTION_USE_SECURE_RANDOM_KEY":
            env = os.getenv("ENVIRONMENT", "development")
            if env.lower() == "production":
                raise ValueError(
                    "SECRET_KEY must be set in production! "
                    "Generate with: openssl rand -hex 32"
                )
            import warnings
            warnings.warn(
                "Using default SECRET_KEY! This is insecure for production.",
                UserWarning,
                stacklevel=2
            )
        elif len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v
'''

# =============================================================================
# PATCH 4: Agregar autenticacion a endpoints expuestos (ALTO)
# =============================================================================
# Archivo: main.py
#
# CAMBIAR ESTE ENDPOINT (linea ~349-356):
PATCH4A_BEFORE = '''
@app.get("/users/get_user_by_email/{user_email}")
def get_user_by_email(user_email, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, user_email=user_email)

    if not db_user:
        raise HTTPException(status_code=400, detail="Email not registered")

    return db_user
'''

# REEMPLAZAR POR:
PATCH4A_AFTER = '''
@app.get("/users/get_user_by_email/{user_email}")
def get_user_by_email(
    user_email: str,
    current_user: Annotated[models.User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """Get user by email - requires authentication."""
    # Solo permitir acceso a datos propios
    if current_user.username != user_email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user's data"
        )
    db_user = crud.get_user_by_email(db, user_email=user_email)

    if not db_user:
        raise HTTPException(status_code=400, detail="Email not registered")

    return db_user
'''

# CAMBIAR ESTE ENDPOINT (linea ~359-366):
PATCH4B_BEFORE = '''
@app.get("/get_users/")
def get_all_users(db: Session = Depends(get_db)):
    db_users = crud.get_users(db=db)

    if not db_users:
        raise HTTPException(status_code=400, detail="Not users in aplication registered yet")

    return db_users
'''

# REEMPLAZAR POR (o mejor, eliminar este endpoint si no es necesario):
PATCH4B_AFTER = '''
# ADVERTENCIA: Este endpoint deberia requerir autenticacion de administrador
# Por ahora, se agrega autenticacion basica. Implementar roles para produccion.
@app.get("/get_users/")
def get_all_users(
    current_user: Annotated[models.User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """Get all users - REQUIRES ADMIN ROLE (TODO: implement role check)."""
    # TODO: Agregar verificacion de rol de administrador
    # if not is_admin(current_user):
    #     raise HTTPException(status_code=403, detail="Admin access required")
    db_users = crud.get_users(db=db)

    if not db_users:
        raise HTTPException(status_code=400, detail="Not users in aplication registered yet")

    return db_users
'''

# =============================================================================
# PATCH 5: Prevenir enumeracion de usuarios (MEDIO)
# =============================================================================
# Archivo: app/api/v1/endpoints/auth.py
#
# BUSCAR (lineas 56-67):
PATCH5_BEFORE = '''
    if not user_db:
        raise HTTPException(status_code=400, detail="No user found")

    # Authenticate user
    user = crud.authenticate_user(db, form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
'''

# REEMPLAZAR POR (usar mismo mensaje para ambos casos):
PATCH5_AFTER = '''
    # Use same error message to prevent user enumeration
    auth_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not user_db:
        raise auth_error

    # Authenticate user
    user = crud.authenticate_user(db, form_data.username, form_data.password)

    if not user:
        raise auth_error
'''

# =============================================================================
# PATCH 6: Configurar CORS de forma mas restrictiva (MEDIO)
# =============================================================================
# Archivo: config.py Y app/core/config.py
#
# BUSCAR:
PATCH6_BEFORE = '''
    cors_allow_methods: List[str] = Field(
        default=["*"],
        description="Allowed HTTP methods for CORS"
    )

    cors_allow_headers: List[str] = Field(
        default=["*"],
        description="Allowed HTTP headers for CORS"
    )
'''

# REEMPLAZAR POR:
PATCH6_AFTER = '''
    cors_allow_methods: List[str] = Field(
        default=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        description="Allowed HTTP methods for CORS"
    )

    cors_allow_headers: List[str] = Field(
        default=["Authorization", "Content-Type", "Accept", "Origin", "X-Requested-With"],
        description="Allowed HTTP headers for CORS"
    )
'''

# =============================================================================
# PATCH 7: Corregir settings.py (ALTO)
# =============================================================================
# Archivo: settings.py
#
# BUSCAR (linea 11):
PATCH7_BEFORE = '''
SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")
'''

# REEMPLAZAR POR:
PATCH7_AFTER = '''
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    import warnings
    warnings.warn(
        "SECRET_KEY not set! Using insecure default. "
        "Set SECRET_KEY environment variable for production.",
        UserWarning
    )
    SECRET_KEY = "INSECURE_DEFAULT_FOR_DEVELOPMENT_ONLY"
'''

# =============================================================================
# PATCH 8: Eliminar print de debug (BAJO)
# =============================================================================
# Archivo: main.py
# Ubicacion: linea ~520
#
# ELIMINAR O COMENTAR:
PATCH8_DELETE = '''
print("********************" + str(type(active_exercise_plan.routine_group_order)))
'''

# =============================================================================
# CODIGO NUEVO A AGREGAR
# =============================================================================

# AGREGAR EN main.py despues de los imports:
NEW_CODE_SECURITY_HEADERS = '''
# ============= SECURITY MIDDLEWARE =============
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers to all responses."""
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        # Enable XSS filter
        response.headers["X-XSS-Protection"] = "1; mode=block"
        # Only send referrer for same-origin
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        # Enable HSTS (uncomment for production with HTTPS)
        # response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

# Agregar despues de crear app:
# app.add_middleware(SecurityHeadersMiddleware)
'''

# AGREGAR en requirements.txt para rate limiting:
NEW_REQUIREMENTS = '''
# Security - Rate Limiting
slowapi>=0.1.9

# Security - Scanning (development/CI)
safety>=2.3.0
bandit>=1.7.0
'''

# =============================================================================
# INSTRUCCIONES FINALES
# =============================================================================
"""
ORDEN DE APLICACION RECOMENDADO:

1. CRITICO - Aplicar PATCH 1 (tiempo de token)
2. ALTO - Aplicar PATCH 2 (eliminar usuario prueba)
3. ALTO - Aplicar PATCH 3 (validacion SECRET_KEY)
4. ALTO - Aplicar PATCH 4A y 4B (autenticacion endpoints)
5. ALTO - Aplicar PATCH 7 (settings.py)
6. MEDIO - Aplicar PATCH 5 (enumeracion usuarios)
7. MEDIO - Aplicar PATCH 6 (CORS restrictivo)
8. BAJO - Aplicar PATCH 8 (eliminar debug)
9. NUEVO - Agregar SecurityHeadersMiddleware
10. NUEVO - Agregar dependencias de seguridad

VERIFICACION POST-APLICACION:
- Ejecutar tests unitarios
- Verificar que login funciona correctamente
- Verificar que tokens expiran a los 30 minutos
- Verificar CORS en desarrollo
- Escanear con: safety check -r requirements.txt
- Analizar con: bandit -r . -x ./mancaperros_env

PARA PRODUCCION:
- Verificar que SECRET_KEY esta configurado como variable de entorno
- Verificar que DB_PASSWORD esta configurado como variable de entorno
- Configurar CORS_ORIGINS solo con dominios de produccion
- Habilitar HTTPS y headers HSTS
"""

if __name__ == "__main__":
    print("Este archivo contiene parches de seguridad.")
    print("Revisar el contenido y aplicar manualmente los cambios necesarios.")
    print("Ver SECURITY_AUDIT_REPORT.md para detalles completos.")
