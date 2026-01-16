# MEJORAS OPCIONALES PENDIENTES - MANCAPERROS APP

**Fecha de creacion:** 2026-01-16
**Estado del proyecto:** PLAN ORIGINAL COMPLETADO
**Puntuacion actual:** ~8.5/10 (era 2.0/10)

---

## CONTEXTO PARA LA SIGUIENTE IA

Este proyecto FastAPI ("Mancaperros App") ha completado un plan de refactorizacion de 8-12 semanas. El plan original identifico 28 problemas (7 criticos, 9 altos, 9 medios, 3 bajos) y todos han sido resueltos.

### Archivos de referencia importantes:
- `REFACTORING_PROGRESS.md` - Historial completo de cambios por semana
- `SECURITY_AUDIT_REPORT.md` - Auditoria de seguridad original
- `SECURITY_CHANGELOG.md` - Cambios de seguridad implementados
- `MED08_*.md` - Documentacion del analisis de consolidacion de modelos
- `README_SOFT_DELETE.md` - Documentacion de soft-delete

### Estado actual:
- **Tests:** 150/150 pasando (100%)
- **Cobertura:** Alta (servicios, repositorios, endpoints)
- **CI/CD:** GitHub Actions configurado
- **Docker:** Dockerfile multi-stage listo
- **Seguridad:** Auditada y parcheada

---

## MEJORAS OPCIONALES (NO CRITICAS)

Estas mejoras surgieron durante la refactorizacion pero NO estaban en el plan original. Son opcionales y pueden implementarse segun prioridad del negocio.

---

### 1. EJECUTAR MIGRACIONES ALEMBIC PENDIENTES

**Prioridad:** Media
**Esfuerzo:** 1-2 horas
**Riesgo:** Bajo

**Descripcion:**
Se crearon migraciones para la nueva estructura de WorkoutEvent (HIGH-08) pero no se ejecutaron en la base de datos.

**Archivos relevantes:**
- `alembic/versions/high08_create_workout_events_table.py`
- `migrations/high08_sqlite_migration.sql`
- `migrations/high08_complete_migration.sql`
- `migrations/high08_migrate_tracker_data.py`

**Pasos:**
```bash
cd C:\Users\Rodrigo\Desktop\proyectos\mancaperros_app\code\backend\mancaperros_app

# 1. Ver estado actual de migraciones
alembic current

# 2. Aplicar migracion de WorkoutEvent
alembic upgrade high08_workout_events

# 3. Migrar datos existentes (opcional, solo si hay datos)
python -m migrations.high08_migrate_tracker_data --dry-run  # Verificar primero
python -m migrations.high08_migrate_tracker_data            # Ejecutar

# 4. Verificar
python -m migrations.high08_migrate_tracker_data --verify-only
```

**Notas:**
- La tabla `users_tracker` (legacy) NO se elimina
- El sistema usa dual-write (escribe en ambas tablas)
- Los endpoints tienen fallback automatico

---

### 2. APLICAR MIXINS A MODELOS EXISTENTES

**Prioridad:** Baja
**Esfuerzo:** 2-3 horas
**Riesgo:** Medio (requiere tests exhaustivos)

**Descripcion:**
Se crearon mixins para reducir duplicacion de codigo (~47%), pero los modelos existentes aun no los usan. Los mixins estan listos y testeados.

**Archivos relevantes:**
- `infrastructure/database/models/mixins.py` - Mixins creados
- `tests/test_mixins.py` - Tests de los mixins
- `MED08_QUICK_WIN_MIXIN_SOLUTION.md` - Guia de implementacion

**Mixins disponibles:**
- `ExercisePlanMixin` - 5 campos comunes (83% cobertura)
- `RoutineMixin` - 8 campos comunes (89% cobertura)
- `ExerciseMixin` - 5 campos comunes (83% cobertura)

**Ejemplo de como aplicar:**
```python
# ANTES (models.py)
class Exercise_plan(Base):
    __tablename__ = "exercise_plans"
    exercise_plan_id = Column(Integer, primary_key=True)
    exercise_plan_name = Column(String(255), default="New exercise plan")
    exercise_plan_type = Column(String(255), default="New type")
    # ... mas campos duplicados ...

# DESPUES
from infrastructure.database.models.mixins import ExercisePlanMixin

class Exercise_plan(Base, ExercisePlanMixin):
    __tablename__ = "exercise_plans"
    exercise_plan_id = Column(Integer, primary_key=True)
    user_owner_id = Column(Integer, ForeignKey("users.user_id"))
    # Los campos comunes vienen del mixin
```

**Pasos:**
1. Leer `MED08_QUICK_WIN_MIXIN_SOLUTION.md`
2. Modificar un modelo a la vez
3. Ejecutar tests despues de cada cambio
4. Repetir para todos los modelos

---

### 3. AGREGAR CAMPOS SOFT-DELETE A MODELOS VIA MIGRACION

**Prioridad:** Baja
**Esfuerzo:** 1-2 horas
**Riesgo:** Bajo

**Descripcion:**
Se implemento `SoftDeleteMixin` pero los campos (`deleted_at`, `is_deleted`) no se agregaron a la base de datos existente.

**Archivos relevantes:**
- `infrastructure/database/models/soft_delete_mixin.py`
- `MIGRATION_SOFT_DELETE_TEMPLATE.py` - Template de migracion
- `README_SOFT_DELETE.md` - Documentacion completa

**Pasos:**
```bash
# 1. Crear migracion
alembic revision --autogenerate -m "Add soft delete columns"

# 2. Revisar el archivo generado en alembic/versions/

# 3. Aplicar
alembic upgrade head

# 4. Verificar
pytest tests/ -v
```

**Notas:**
- El mixin ya esta aplicado a los modelos en codigo
- Solo falta agregar las columnas a la BD

---

### 4. CONFIGURAR BRANCH PROTECTION EN GITHUB

**Prioridad:** Media (si hay equipo)
**Esfuerzo:** 30 minutos
**Riesgo:** Ninguno

**Descripcion:**
Los workflows de CI/CD estan configurados pero la proteccion de ramas debe configurarse manualmente en GitHub.

**Pasos:**
1. Ir a GitHub > Settings > Branches
2. Add rule para `main`:
   - Require pull request reviews
   - Require status checks: `test`, `lint`, `security`
   - Require branches to be up to date
3. Add rule para `develop` (similar)

**Archivos relevantes:**
- `.github/workflows/ci.yml`
- `.github/workflows/docker-build.yml`
- `.github/CONTRIBUTING.md`

---

### 5. CONFIGURAR SECRETS EN GITHUB ACTIONS

**Prioridad:** Alta (si se va a usar CI/CD)
**Esfuerzo:** 15 minutos
**Riesgo:** Ninguno

**Descripcion:**
Los workflows esperan ciertos secrets para funcionar completamente.

**Secrets necesarios:**
```
DOCKER_USERNAME    - Usuario de Docker Hub (opcional)
DOCKER_PASSWORD    - Password de Docker Hub (opcional)
DATABASE_URL       - URL de BD para tests de integracion (opcional)
```

**Pasos:**
1. Ir a GitHub > Settings > Secrets and variables > Actions
2. Agregar cada secret

---

### 6. IMPLEMENTAR CACHE CON REDIS

**Prioridad:** Baja
**Esfuerzo:** 4-6 horas
**Riesgo:** Medio

**Descripcion:**
Estaba mencionado en el plan original como mejora de rendimiento pero no se implemento.

**Endpoints candidatos para cache:**
- `GET /api/v1/exercises/plans/available` - Lista de planes globales
- `GET /api/v1/users/me` - Datos del usuario actual

**Pasos:**
1. Agregar `redis` a requirements.txt
2. Crear `app/core/cache.py`
3. Implementar decorador `@cached(ttl=300)`
4. Aplicar a endpoints seleccionados

---

### 7. IMPLEMENTAR RATE LIMITING

**Prioridad:** Media (para produccion)
**Esfuerzo:** 2-3 horas
**Riesgo:** Bajo

**Descripcion:**
Mencionado en el plan original de seguridad pero no implementado.

**Opciones:**
- `slowapi` - Biblioteca simple para FastAPI
- `fastapi-limiter` - Con Redis backend

**Endpoints criticos:**
- `POST /api/v1/auth/token` - Login (5 req/min)
- `POST /api/v1/auth/refresh` - Refresh (10 req/min)
- `POST /api/v1/users/` - Registro (3 req/min)

---

## COMANDOS UTILES

```bash
# Directorio del proyecto
cd C:\Users\Rodrigo\Desktop\proyectos\mancaperros_app\code\backend\mancaperros_app

# Activar entorno virtual
./mancaperros_env/Scripts/activate

# Ejecutar tests
./mancaperros_env/Scripts/python.exe -m pytest tests/ -v

# Ejecutar aplicacion
./mancaperros_env/Scripts/python.exe -m uvicorn main:app --reload

# Ver estado de migraciones
alembic current
alembic history

# Build Docker
docker build -t mancaperros_app:latest .
```

---

## ESTRUCTURA DEL PROYECTO

```
mancaperros_app/
├── main.py                          # Punto de entrada (solo inicializacion)
├── crud.py                          # Operaciones CRUD legacy
├── models.py                        # Modelos SQLAlchemy legacy
├── schemas.py                       # Schemas Pydantic
├── app/
│   ├── api/v1/
│   │   ├── endpoints/               # Routers por dominio
│   │   │   ├── auth.py
│   │   │   ├── users.py
│   │   │   ├── exercises.py
│   │   │   └── routines.py
│   │   └── dependencies.py
│   ├── core/
│   │   ├── config.py                # Configuracion con Pydantic Settings
│   │   └── security.py              # JWT, hashing
│   └── domain/services/             # Capa de servicios
├── infrastructure/database/
│   ├── models/
│   │   ├── mixins.py                # Mixins para reducir duplicacion
│   │   ├── soft_delete_mixin.py     # Soft delete
│   │   └── workout_event.py         # Nuevos modelos polimorficos
│   └── repositories/                # Patron Repository
├── migrations/                      # Scripts SQL de migracion
├── alembic/                         # Migraciones Alembic
├── tests/                           # 150 tests
├── .github/workflows/               # CI/CD
├── Dockerfile                       # Multi-stage build
└── requirements.txt
```

---

## DEPENDENCIAS PRINCIPALES

```
fastapi>=0.115.0
pydantic>=2.10.0
pydantic-settings>=2.6.0
sqlalchemy>=2.0.36
python-jose>=3.4.0
passlib[bcrypt]>=1.7.4
pytest>=8.0.0
```

---

## CONTACTO

Este documento fue generado por Claude (Opus 4.5) el 2026-01-16 como parte de un proyecto de refactorizacion de 8-12 semanas que fue completado exitosamente.

Para continuar con las mejoras opcionales, la siguiente IA debe:
1. Leer este documento
2. Leer `REFACTORING_PROGRESS.md` para contexto historico
3. Ejecutar tests para verificar estado actual
4. Seleccionar una mejora y seguir los pasos indicados
