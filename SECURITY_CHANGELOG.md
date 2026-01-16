# 🔒 Security Changelog - Mancaperros App

## Resumen Ejecutivo

Este documento detalla las mejoras de seguridad criticas implementadas durante la **Semana 1** del proyecto de hardening de seguridad. Se identificaron y corrigieron multiples vulnerabilidades que podrian haber comprometido la aplicacion y los datos de los usuarios.

---

## 📅 Fecha de Cambios

| Campo | Valor |
|-------|-------|
| **Fecha de implementacion** | 2026-01-08 |
| **Version anterior** | 0.x (sin versionado de seguridad) |
| **Version actual** | 1.0.0-security |
| **Autor** | Equipo de Desarrollo |
| **Revision de seguridad** | Semana 1 - Hardening inicial |

---

## ⚠️ Vulnerabilidades Encontradas

### 1. Credenciales Hardcodeadas (CRITICO)

| Severidad | Ubicacion | Descripcion |
|-----------|-----------|-------------|
| **CRITICA** | `database.py` | URL de conexion a base de datos con credenciales en texto plano |
| **CRITICA** | `main.py` | SECRET_KEY para JWT hardcodeada en el codigo fuente |
| **ALTA** | `crud.py` | Usuario de prueba `fake_users_db` con credenciales expuestas |

**Riesgo**: Cualquier persona con acceso al repositorio (incluso si es privado) podria obtener acceso completo a la base de datos de produccion y generar tokens JWT validos.

**Referencia OWASP**: [A07:2021 - Identification and Authentication Failures](https://owasp.org/Top10/A07_2021-Identification_and_Authentication_Failures/)

---

### 2. Dependencias con Vulnerabilidades Conocidas (CVEs)

| Dependencia | Version Anterior | CVE | Severidad | Descripcion |
|-------------|------------------|-----|-----------|-------------|
| `starlette` | < 0.49.1 | [CVE-2025-54121](https://nvd.nist.gov/vuln/detail/CVE-2025-54121) | **Alta** | Vulnerabilidad de Denegacion de Servicio (DoS) |
| `python-jose` | < 3.4.0 | [CVE-2024-33663](https://nvd.nist.gov/vuln/detail/CVE-2024-33663) | **Alta (7.5)** | Vulnerabilidad en verificacion de firmas JWT |
| `python-jose` | < 3.4.0 | [CVE-2024-33664](https://nvd.nist.gov/vuln/detail/CVE-2024-33664) | **Media (5.3)** | Divulgacion de informacion en manejo de errores |
| `SQLAlchemy` | < 2.0.36 | N/A | **Media** | Multiples parches de seguridad acumulados |

**Riesgo**:
- DoS: Atacantes podrian causar indisponibilidad del servicio
- JWT: Posible bypass de autenticacion mediante firmas manipuladas
- SQLAlchemy: Potenciales vulnerabilidades de inyeccion SQL

---

### 3. Endpoints sin Autenticacion (ALTA)

| Endpoint | Metodo | Problema |
|----------|--------|----------|
| `/get_users/` | GET | Listado completo de usuarios sin autenticacion |
| `/users/get_user_by_email/{email}` | GET | Acceso a informacion de cualquier usuario |
| `/exercise_plans/{id}/rutines` | GET | Acceso a datos sin validacion de pertenencia |

**Riesgo**: Enumeracion de usuarios, robo de datos personales, IDOR (Insecure Direct Object Reference).

**Referencia OWASP**: [A01:2021 - Broken Access Control](https://owasp.org/Top10/A01_2021-Broken_Access_Control/)

---

### 4. Tiempo de Expiracion de Token Excesivo (MEDIA)

| Configuracion | Valor Anterior | Problema |
|---------------|----------------|----------|
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 180 minutos (3 horas) | Ventana de ataque prolongada |

**Riesgo**: Si un token es robado, el atacante tiene 3 horas para realizar acciones maliciosas.

---

### 5. Ausencia de Tests de Seguridad (MEDIA)

No existia ninguna suite de tests para validar:
- Autenticacion correcta/incorrecta
- Autorizacion de endpoints
- Validacion de tokens
- Manejo de errores

---

## ✅ Vulnerabilidades Corregidas

### 1. Sistema de Configuracion Centralizado

**Archivo creado**: `config.py`

```python
# Antes (INSEGURO)
SECRET_KEY = "my-secret-key-hardcoded"
DATABASE_URL = "mysql://root:password123@host:3306/db"

# Despues (SEGURO)
from config import settings
secret = settings.secret_key        # Desde variable de entorno
db_url = settings.database_url      # Construida dinamicamente
```

**Caracteristicas implementadas**:
- ✅ Pydantic Settings para validacion automatica
- ✅ Lectura de variables desde `.env` y entorno
- ✅ Valores por defecto seguros
- ✅ Validadores personalizados que advierten sobre configuraciones inseguras
- ✅ Soporte para multiples entornos (development, staging, production)

---

### 2. Eliminacion de Credenciales del Codigo

**Archivo modificado**: `database.py`

```python
# Antes
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:xxxxx@yamanote.proxy.rlwy.net:3306/mancaperros"

# Despues
from config import settings
engine = create_engine(settings.database_url)
```

**Archivo modificado**: `main.py`

```python
# Antes
SECRET_KEY = "asdjfasfklj123..."
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 180

# Despues
from config import settings
# Usa settings.secret_key, settings.algorithm, settings.access_token_expire_minutes
```

---

### 3. Actualizacion de Dependencias

**Archivo modificado**: `requirements.txt`

| Dependencia | Version Anterior | Version Nueva | Cambio |
|-------------|------------------|---------------|--------|
| `fastapi` | sin especificar | `>=0.115.0` | Mejoras de seguridad |
| `starlette` | < 0.49.1 | `>=0.49.1` | Correccion CVE-2025-54121 |
| `python-jose` | < 3.4.0 | `>=3.4.0` | Correccion CVE-2024-33663/33664 |
| `SQLAlchemy` | < 2.0.36 | `>=2.0.36` | Parches de seguridad |
| `bcrypt` | sin especificar | `>=4.2.0` | Mejoras de performance |
| `pydantic-settings` | no instalado | `>=2.6.0` | Nuevo requerimiento |
| `pytest` | no instalado | `>=8.0.0` | Suite de testing |
| `pytest-asyncio` | no instalado | `>=0.24.0` | Tests async |
| `httpx` | no instalado | `>=0.27.0` | Cliente de test |

**Backup creado**: `requirements.txt.backup`

---

### 4. Autenticacion en Endpoints Expuestos

**Endpoints protegidos**:

```python
# Antes
@app.get("/get_users/")
def get_all_users(db: Session = Depends(get_db)):
    ...

# Despues
@app.get("/get_users/")
def get_all_users(
    current_user: Annotated[models.User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    ...
```

| Endpoint | Estado |
|----------|--------|
| `/get_users/` | ✅ Ahora requiere autenticacion |
| `/users/get_user_by_email/{email}` | ✅ Ahora requiere autenticacion |
| `/exercise_plans/{id}/rutines` | ✅ Ahora requiere autenticacion |

---

### 5. Reduccion de Tiempo de Expiracion de Token

| Configuracion | Antes | Ahora | Recomendacion |
|---------------|-------|-------|---------------|
| Token expiration | 180 min | **30 min** (configurable) | 15-30 min para produccion |

**Configuracion en `.env`**:
```bash
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

### 6. Suite de Tests de Seguridad

**Directorio creado**: `tests/`

**Archivo creado**: `tests/__init__.py`

```python
"""
Test suite for Mancaperros FastAPI application.
- Authentication endpoints (login, JWT token validation)
- User management (registration, user retrieval)
- Security (protected endpoints, authorization)
- Configuration (settings validation)
"""
```

**Comandos de ejecucion**:
```bash
pytest                           # Todos los tests
pytest tests/test_auth.py        # Tests de autenticacion
pytest -v                        # Salida verbose
pytest --cov=.                   # Con reporte de cobertura
```

---

## 🔑 Credenciales que DEBEN Rotarse INMEDIATAMENTE

> ⚠️ **ACCION REQUERIDA**: Las siguientes credenciales fueron expuestas en el codigo fuente y DEBEN ser rotadas antes del proximo deployment.

### 1. SECRET_KEY para JWT

```bash
# Generar nueva clave (ejecutar en terminal):
openssl rand -hex 32

# O con Python:
python -c "import secrets; print(secrets.token_hex(32))"
```

**Donde actualizar**: Variable de entorno `SECRET_KEY` en Railway/Azure

---

### 2. Contrasena de Base de Datos

**Pasos para rotar en Railway**:
1. Ir a Railway Dashboard > Tu proyecto > Variables
2. Localizar `DB_PASSWORD` o la variable correspondiente
3. Generar nueva contrasena segura (minimo 16 caracteres, alfanumericos + especiales)
4. Actualizar en Railway
5. Actualizar en el archivo `.env` local (desarrollo)

---

### 3. Credenciales de Usuario de Prueba

El archivo `crud.py` contiene un usuario de prueba hardcodeado:

```python
fake_users_db = {
    "johndoe": {
        "user_name": "johndoe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
    },
}
```

**Accion**: Si este usuario existe en produccion, cambiar su contrasena inmediatamente.

---

## 📋 Checklist de Deployment Seguro

### Pre-Deployment

- [ ] **SECRET_KEY rotada** - Nueva clave de 64 caracteres hex generada
- [ ] **DB_PASSWORD rotada** - Nueva contrasena de base de datos configurada
- [ ] **Variables de entorno configuradas** - Todas las variables en `.env.example` tienen valores en produccion
- [ ] **DEBUG=false** - Modo debug desactivado
- [ ] **ENVIRONMENT=production** - Entorno correcto configurado
- [ ] **USE_SQLITE=false** - Base de datos de produccion activa
- [ ] **CORS_ORIGINS restringidos** - Solo dominios confiables

### Verificacion de Configuracion

```bash
# Verificar que no hay secretos en el codigo
git log --oneline --all -- "*.py" | head -20
grep -r "SECRET_KEY\s*=" --include="*.py" .
grep -r "password" --include="*.py" .
```

### Post-Deployment

- [ ] **Endpoint /test/ responde** - Verificar que la aplicacion arranca
- [ ] **Login funciona** - Verificar autenticacion con credenciales validas
- [ ] **Endpoints protegidos rechazan sin token** - Verificar 401 Unauthorized
- [ ] **Logs sin errores criticos** - Revisar logs de Railway/Azure
- [ ] **Tests pasan** - `pytest` sin errores

### Monitoreo Continuo

- [ ] Alertas configuradas para errores 5xx
- [ ] Alertas configuradas para intentos de login fallidos excesivos
- [ ] Revision periodica de dependencias con vulnerabilidades

---

## 📚 Referencias

### OWASP Top 10 (2021)
- [A01:2021 - Broken Access Control](https://owasp.org/Top10/A01_2021-Broken_Access_Control/)
- [A02:2021 - Cryptographic Failures](https://owasp.org/Top10/A02_2021-Cryptographic_Failures/)
- [A06:2021 - Vulnerable and Outdated Components](https://owasp.org/Top10/A06_2021-Vulnerable_and_Outdated_Components/)
- [A07:2021 - Identification and Authentication Failures](https://owasp.org/Top10/A07_2021-Identification_and_Authentication_Failures/)

### CVE Details
- [CVE-2025-54121 - Starlette DoS](https://nvd.nist.gov/vuln/detail/CVE-2025-54121)
- [CVE-2024-33663 - python-jose JWT Signature Bypass](https://nvd.nist.gov/vuln/detail/CVE-2024-33663)
- [CVE-2024-33664 - python-jose Information Disclosure](https://nvd.nist.gov/vuln/detail/CVE-2024-33664)

### Mejores Practicas
- [12 Factor App - Config](https://12factor.net/config)
- [FastAPI Security Best Practices](https://fastapi.tiangolo.com/tutorial/security/)
- [Pydantic Settings Documentation](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)

---

## 📞 Contacto para Reportar Vulnerabilidades

Si descubres una vulnerabilidad de seguridad en esta aplicacion:

1. **NO** la reportes publicamente en issues de GitHub
2. Envia un email a: `security@[tu-dominio].com`
3. Incluye:
   - Descripcion detallada de la vulnerabilidad
   - Pasos para reproducirla
   - Impacto potencial
   - Sugerencia de correccion (si la tienes)

**Tiempo de respuesta esperado**: 48 horas habiles

---

*Documento generado el 2026-01-08 | Version 1.0*
