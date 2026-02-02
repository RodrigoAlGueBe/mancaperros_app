# MED-08: Análisis de Consolidación User/Global - Modelo Paralelismo

**Fecha:** 2026-01-16
**Estado:** REPORTE ANALÍTICO (Sin cambios)
**Problema:** 90-95% de duplicidad entre pares de modelos

---

## 1. ANÁLISIS DETALLADO DE DIFERENCIAS

### 1.1 EXERCISE_PLAN vs EXERCISE_PLAN_GLOBAL

#### Campos Comunes (95% similitud):
```python
# IGUALES - Misma estructura, tipo y comportamiento
exercise_plan_id        → Column(Integer, primary_key=True, index=True)
exercise_plan_name      → Column(String(255), index=True, default="New exercise plan")
exercise_plan_type      → Column(String(255), index=True, default="New exercise plan type")
creation_date          → Column(Date, index=True, default=date(1970, 1, 1))
difficult_level        → Column(String(255), index=True, default="New exercise plan difficult level")
routine_group_order    → Column(JSON, nullable=False, default=ROUTINE_GROUP_ORDER_DEFAULT)
```

#### Diferencias Clave (5%):

| Aspecto | Exercise_plan | Exercise_plan_global | Impacto |
|---------|---------------|----------------------|---------|
| **FK Usuario** | `user_owner_id` (nullable=True) | `user_creator_id` (nullable=False) | CRÍTICO: Semántica diferente |
| **Nullable** | Multiple campos con nullable=True | Todos nullable=False | MODERADO: Restricción de datos |
| **Tabla** | "exercise_plans" | "exercise_plans_global" | BAJO: Solo nombre |
| **Relación Rutines** | "Rutine" (back_populates) | "Rutine_global" (back_populates) | CRÍTICO: Referencias cruzadas |
| **Relación User** | "exercise_plan" (back_populates) | "exercise_plan_global" (back_populates) | BAJO: Solo nombre |

---

### 1.2 RUTINE vs RUTINE_GLOBAL

#### Campos Comunes (100% similitud):
```python
# IDÉNTICOS - Misma estructura, tipos y defaults
rutine_id              → Column(Integer, primary_key=True, index=True)
rutine_name            → Column(String(255), index=True, default="New rutine name")
rutine_type            → Column(String(255), index=True, default="New rutine type")
rutine_group           → Column(String(255), index=True, default="New rutine group")
rutine_category        → Column(String(255), index=True, default="New rutine category")
exercise_plan_id       → Column(Integer, ForeignKey(...)) [diferentes tablas destino]
rounds                 → Column(Integer, index=True, default=0)
rst_btw_exercises      → Column(String(255), index=True, default="0")
rst_btw_rounds         → Column(String(255), index=True, default="0")
difficult_level        → Column(String(255), index=True, default="New rutine difficult level")
```

#### Diferencias Clave:

| Aspecto | Rutine | Rutine_global | Impacto |
|---------|--------|---------------|---------|
| **FK destino** | "exercise_plans.exercise_plan_id" | "exercise_plans_global.exercise_plan_id" | CRÍTICO: Tabla destino diferente |
| **Nullable** | Sin validación (default nullable) | Todos nullable=False | BAJO: Restricción menor |
| **Tabla** | "rutines" | "rutines_global" | BAJO: Solo nombre |
| **Relación Exercise** | "Exercise" model | "Exercise_global" model | CRÍTICO: Referencias cruzadas |

**HALLAZGO CRUCIAL:** Rutine y Rutine_global son 100% idénticos en estructura de datos. Las ÚNICAS diferencias son las relaciones a otros modelos.

---

### 1.3 EXERCISE vs EXERCISE_GLOBAL

#### Campos Comunes (95% similitud):
```python
# IDÉNTICOS
exercise_id     → Column(Integer, primary_key=True, index=True)
exercise_name   → Column(String(255), index=True, default="New exercise name")
rep             → Column(String(255), index=True, default="empty")
exercise_type   → Column(String(255), index=True, default="New exercise type")
exercise_group  → Column(String(255), index=True, default="New exercise group")
rutine_id       → Column(Integer, ForeignKey(...)) [diferentes tablas]
image           → Column(String(255), index=True, default="empty")
```

#### Diferencias Clave:

| Aspecto | Exercise | Exercise_global | Impacto |
|---------|----------|-----------------|---------|
| **Nullable** | Sin validación | Todos nullable=False | BAJO: Restricción |
| **Tabla** | "exercises" | "exercises_global" | BAJO: Solo nombre |
| **FK destino** | "rutines.rutine_id" | "rutines_global.rutine_id" | CRÍTICO: Tabla destino |

---

## 2. IMPACTO DE CONSOLIDACIÓN

### 2.1 Tablas Afectadas
```
ACTUALMENTE (Separadas):
├── exercise_plans (usuario personal)
├── exercise_plans_global (plantilla global)
├── rutines (usuario personal)
├── rutines_global (plantilla global)
├── exercises (usuario personal)
└── exercises_global (plantilla global)

CONSOLIDADO (Propuesto):
├── exercise_plans (usuario personal + global combinado)
├── rutines (usuario personal + global combinado)
└── exercises (usuario personal + global combinado)
```

### 2.2 Estrategia de Consolidación

**Opción A: POLIMORFISMO CON TIPO DISCRIMINADOR** (Recomendado)

```python
# Nuevo campo en cada tabla
class Exercise_plan(Base):
    __tablename__ = "exercise_plans"

    exercise_plan_id = Column(Integer, primary_key=True)
    exercise_plan_name = Column(String(255))
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=True)  # NULL = global
    exercise_plan_type = Column(String(255))
    creation_date = Column(Date)
    difficult_level = Column(String(255))
    routine_group_order = Column(JSON)
    is_global = Column(Boolean, default=False, index=True)  # Discriminador
    created_by_user_id = Column(Integer, ForeignKey("users.user_id"))  # Siempre requerido
```

**Ventaja:** Simples queries, UNION innecesario
**Desventaja:** Semantica mezclada en una tabla

---

**Opción B: TABLA UNIFICADA CON POLIMORFISMO SQLALCHEMY**

```python
class Exercise_plan(Base):
    __tablename__ = "exercise_plans"

    exercise_plan_id = Column(Integer, primary_key=True)
    type = Column(String(50), index=True)  # "personal" o "global"
    __mapper_args__ = {
        "polymorphic_on": type,
        "polymorphic_identity": "personal"
    }
    # ... campos comunes

class Exercise_plan_global(Exercise_plan):
    __mapper_args__ = {"polymorphic_identity": "global"}
```

**Ventaja:** Herencia ORM clara, queries tipadas
**Desventaja:** Complejidad SQLAlchemy, cambios significativos en lógica

---

**Opción C: VISTA SQL UNIFICADA** (Menos invasivo)

Mantener tablas separadas pero crear VISTAs SQL que unifiquen datos:
```sql
CREATE VIEW v_exercise_plans AS
SELECT
    ep.exercise_plan_id,
    ep.exercise_plan_name,
    ep.user_owner_id as user_id,
    ep.created_by as created_by_user_id,
    'personal' as type,
    FROM exercise_plans ep
UNION ALL
SELECT
    epg.exercise_plan_id,
    epg.exercise_plan_name,
    NULL as user_id,
    epg.user_creator_id as created_by_user_id,
    'global' as type
FROM exercise_plans_global epg;
```

**Ventaja:** Cero cambios en BD existente, queries unificadas desde ORM
**Desventaja:** Vistas no updatable, complejidad de mapeo

---

### 2.3 Código Afectado

**CRÍTICO (Cambios requeridos):**

1. **Models** (6 archivos):
   - `exercise_plan.py`
   - `exercise_plan_global.py`
   - `routine.py`
   - `routine_global.py`
   - `exercise.py`
   - `exercise_global.py`

2. **Repositorios** (6 archivos):
   - `exercise_plan_repository.py`
   - `exercise_plan_global_repository.py`
   - `routine_repository.py`
   - `routine_global_repository.py`
   - `exercise_repository.py`
   - `exercise_global_repository.py`

3. **Servicios** (al menos 2 archivos):
   - `exercise_plan_service.py`
   - `routine_service.py`

4. **Schemas** (14 clases en `schemas.py`):
   - Exercise_Base, Exercise_Create, Exercise
   - Rutine_Base, Rutine_Create, Rutine
   - Exercise_plan_Base, Exercise_plan_Create, Exercise_plan
   - Exercise_plan_global_Base, Exercise_plan_global_Create, Exercise_plan_global
   - Rutine_global_Base, Rutine_global_Create, Rutine_global
   - Exercise_global_Base, Exercise_global_Create, Exercise_global

5. **Endpoints** (2 archivos):
   - `app/api/v1/endpoints/exercises.py` (usa Exercise_plan_global)
   - `app/api/v1/endpoints/routines.py` (usa Rutine_global)

6. **CRUD deprecado** (`crud.py`):
   - 8+ funciones que crean/consultan modelos global

7. **Tests** (4 archivos):
   - `test_exercise_plans.py`
   - `test_routines.py`
   - `test_models.py`
   - `tests/test_crud.py`

8. **Migraciones** (1+ archivos):
   - Nueva migración para consolidar tablas
   - Migración reversa para rollback

---

## 3. RIESGOS DE CONSOLIDACIÓN

### 3.1 Riesgos CRÍTICOS

#### Riesgo 1: Pérdida de Semántica de Negocio
**Severidad:** CRÍTICA
**Descripción:** Los modelos tienen significado diferente:
- `Exercise_plan` = Asignado a usuario (personal)
- `Exercise_plan_global` = Plantilla reutilizable (global)

Consolidar pierde esta distinción clara.

**Mitigación:**
- Usar discriminador explícito (`is_global` boolean)
- Tests que validen la semántica

---

#### Riesgo 2: Ruptura de Relaciones Polimórficas
**Severidad:** CRÍTICA
**Descripción:** Actualmente:
```python
# Exercise tiene FK EXPLÍCITO a Rutine
class Exercise(Base):
    rutine_id = ForeignKey("rutines.rutine_id")

# Exercise_global tiene FK EXPLÍCITO a Rutine_global
class Exercise_global(Base):
    rutine_id = ForeignKey("rutines_global.rutine_id")
```

Si consolidas a una sola tabla `exercises`, NO PUEDES tener dos FKs diferentes.

**Solución:**
```python
class Exercise(Base):
    rutine_id = Column(Integer, ForeignKey("rutines.rutine_id"))
    # Relación polimórfica via discriminador
```

---

#### Riesgo 3: Migración de Datos Destructiva
**Severidad:** CRÍTICA
**Descripción:**
- Renumerar IDs puede quebrar referencias existentes
- 6 tablas con datos históricos (si existen)
- Eliminar tablas globales puede perder datos no copiados

**Mitigación:**
- Backup completo pre-consolidación
- Verificación 1-a-1 de integridad post-migración

---

#### Riesgo 4: Impacto en Lógica de Negocio
**Severidad:** CRÍTICA
**Descripción:**
- `Exercise_plan_repository.create_from_global()` copia datos de global a personal
- Con consolidación, sería copiar dentro de la MISMA tabla (cuidado con IDs)
- Queries que filtran por tabla harían UNION (performance degradada)

**Ejemplo problemático:**
```python
# Hoy
personal_plans = db.query(Exercise_plan).filter(Exercise_plan.user_owner_id == user_id)
global_plans = db.query(Exercise_plan_global).filter(Exercise_plan_global.user_creator_id == user_id)

# Consolidado (UNION required)
all_plans = db.query(Exercise_plan).filter(
    or_(
        Exercise_plan.user_owner_id == user_id,
        Exercise_plan.created_by_user_id == user_id
    )
)
```

---

### 3.2 Riesgos MODERADOS

#### Riesgo 5: Performance - Tablas Más Grandes
**Severidad:** MODERADO
**Descripción:**
- Tablas consolidadas serían más grandes (~6x si 1/3 global, 2/3 personal)
- Índices existentes pueden no ser óptimos para queries mixtas
- Scaneos de tabla completa más costosos

**Mitigación:**
- Índices compuestos en (user_id, is_global)
- Particionamiento si escala crece

---

#### Riesgo 6: API Breaking Change
**Severidad:** MODERADO
**Descripción:**
Clientes de la API esperan endpoints separados:
- `POST /exercise_plans` (personal)
- `POST /exercise_plans_global` (global)

Consolidar internamente requiere actualizar contracto API.

---

#### Riesgo 7: Test Coverage
**Severidad:** MODERADO
**Descripción:**
- 133 tests actuales (100% pasando)
- Consolidación requiere nuevos tests para polimorfismo
- Riesgo de regressiones sutiles en lógica de copia de datos

---

### 3.3 Riesgos BAJOS

- **Documentación desactualizada** (BAJO): README.md, docstrings mencionan estructuras
- **Backward compatibility** (BAJO): Re-exports en `models.py` pueden mantener interfaz
- **Cache invalidation** (BAJO): Si hay cache, patrones de invalidación necesitan ajuste

---

## 4. ANÁLISIS DE FACTIBILIDAD

### 4.1 ¿Es Factible la Consolidación?

**RESPUESTA:** Sí, es **TÉCNICAMENTE FACTIBLE** pero **NO RECOMENDADO AHORA**

#### Factibilidad por Componente:

| Componente | Factibilidad | Complejidad | Riesgo | Duración Est. |
|-----------|----------|-----------|--------|-----------------|
| Models | 100% | ALTA | ALTO | 4-6 horas |
| Repositorios | 100% | ALTA | MODERADO | 6-8 horas |
| Servicios | 100% | MEDIA | MODERADO | 2-3 horas |
| Schemas | 100% | MEDIA | BAJO | 3-4 horas |
| Endpoints | 100% | MEDIA | MODERADO | 2-3 horas |
| Tests | 95% | ALTA | ALTO | 6-8 horas |
| Migraciones | 80% | CRÍTICA | CRÍTICO | 3-5 horas |
| **TOTAL** | **~95%** | **CRÍTICA** | **ALTO** | **30-40 horas** |

---

### 4.2 Prerrequisitos No Presentes

Para consolidar sin ruptura:

1. **MISSING:** Control de versiones de API (v1, v2)
   - Sin versioning, cambios en endpoints rompen clientes existentes

2. **MISSING:** Feature flags / gradual rollout
   - No hay forma de activar/desactivar consolidación por usuario

3. **MISSING:** Replicación de datos en vivo
   - No hay mecanismo para copiar datos de tablas globales a personales antes de consolidar

4. **MISSING:** Datos históricos documentados
   - ¿Cuántos records en cada tabla global? ¿Críticos?

5. **MISSING:** Análisis de impacto en producción
   - ¿Sistema está en producción con datos reales?
   - ¿Hay usuarios dependiendo de estructura actual?

---

## 5. RECOMENDACIÓN FINAL

### 5.1 RECOMENDACIÓN: POSPONER CONSOLIDACIÓN

**Justificación:**

1. **Riesgo vs Beneficio desfavorable**
   - Beneficio: ~5-10% de reducción en mantenimiento, claridad de código
   - Riesgo: Ruptura de semántica, impacto en 8+ archivos, potencial data loss

2. **Demasiadas incógnitas en producción**
   - ¿Sistema está en producción?
   - ¿Hay usuarios con planes globales/personales?
   - ¿Datos históricos importantes?

3. **Timing inapropiado**
   - Semana 5 focus: DevOps/CI-CD (Dockerfile ya completado)
   - Consolidación requiere **30-40 horas** concentradas
   - Mejor hacerlo como task aislada en Semana 6-7

4. **Existen alternativas menos riesgosas**
   - Mantener código como está (ya está limpio/documentado)
   - Usar herencia SQLAlchemy sin consolidar tablas (si ORM es futura meta)
   - Crear VISTAS para consolidación lógica sin cambiar BD

---

### 5.2 ALTERNATIVA RECOMENDADA: Abstracción sin Consolidación

**SI NECESITAS unificar lógica, hacer:**

```python
# Crear mixin para código compartido
class ExercisePlanMixin:
    """Campos y métodos comunes"""
    exercise_plan_name = Column(String(255))
    exercise_plan_type = Column(String(255))
    # ...métodos compartidos

class Exercise_plan(Base, ExercisePlanMixin):
    __tablename__ = "exercise_plans"
    user_owner_id = Column(Integer, ForeignKey("users.user_id"), nullable=True)

class Exercise_plan_global(Base, ExercisePlanMixin):
    __tablename__ = "exercise_plans_global"
    user_creator_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)

# Crear factory para abstracción
class ExercisePlanFactory:
    @staticmethod
    def get_plan(plan_id: int, is_global: bool = False, db: Session = None):
        if is_global:
            return db.query(Exercise_plan_global).filter(...).first()
        return db.query(Exercise_plan).filter(...).first()
```

**Ventajas:**
- Código compartido sin consolidación
- Cero riesgo de data loss
- Mantiene semántica clara
- Fácil revertir

**Desventajas:**
- Todavía hay duplicación (aceptable en este caso)

---

### 5.3 TIMELINE ALTERNATIVA

#### Semana 5 (Actual) - MANTENER PLAN ACTUAL:
- DevOps/CI-CD improvements
- Redis caching (si tiempo permite)
- Rate limiting

#### Semana 6-7 (FUTURA): Evaluación de Consolidación
- Feature flag infrastructure
- API versioning (v1/v2)
- **ENTONCES**: Considerar consolidación con seguridad

#### Semana 8+: Consolidación (si aprobada)
- Implementación
- Testing exhaustivo
- Gradual rollout

---

## 6. MATRIZ DE DECISIÓN

```
CONSOLIDAR AHORA?

┌─────────────────────────┬───────┬──────────────────────┐
│ Criterio                │ Score │ Recomendación        │
├─────────────────────────┼───────┼──────────────────────┤
│ Urgencia de negocio     │ 2/10  │ NO es prioritario    │
│ Complejidad técnica     │ 8/10  │ MUY complejo         │
│ Riesgo de ruptura       │ 8/10  │ MUY riesgoso         │
│ Beneficio esperado      │ 5/10  │ Moderado             │
│ Madurez del código      │ 7/10  │ Bueno pero preparado │
│ Tiempo disponible       │ 3/10  │ NO hay tiempo        │
├─────────────────────────┼───────┼──────────────────────┤
│ SCORE FINAL             │ 5.5/10│ POSPONER             │
└─────────────────────────┴───────┴──────────────────────┘
```

---

## 7. PRÓXIMOS PASOS RECOMENDADOS

### Inmediato (Semana 5):
- [ ] Documentar esta decisión en REFACTORING_PROGRESS.md
- [ ] Agregar notas al código: "MED-08: Consolidation deferred to Week 6-7"
- [ ] Evaluar urgencia de consolidación (preguntar PM/stakeholders)

### Mediano plazo (Semana 6):
- [ ] Implementar API versioning (si no existe)
- [ ] Crear feature flag infrastructure
- [ ] Re-evaluar consolidación con datos de producción

### Largo plazo (Semana 8+):
- [ ] SI se decide consolidar: Planning detallado
- [ ] Crear migration strategy exhaustiva
- [ ] Implementar con rollback plan claro

---

## 8. ARCHIVOS ANALIZADOS

```
Modelos (6):
├── infrastructure/database/models/exercise_plan.py (85 líneas)
├── infrastructure/database/models/exercise_plan_global.py (90 líneas)
├── infrastructure/database/models/routine.py (94 líneas)
├── infrastructure/database/models/routine_global.py (109 líneas)
├── infrastructure/database/models/exercise.py (56 líneas)
└── infrastructure/database/models/exercise_global.py (79 líneas)

Repositorios (6):
├── infrastructure/database/repositories/exercise_plan_repository.py (351 líneas)
├── infrastructure/database/repositories/exercise_plan_global_repository.py (317 líneas)
├── infrastructure/database/repositories/routine_repository.py
├── infrastructure/database/repositories/routine_global_repository.py
├── infrastructure/database/repositories/exercise_repository.py
└── infrastructure/database/repositories/exercise_global_repository.py

Otros:
├── schemas.py (14 clases relacionadas)
├── app/api/v1/endpoints/exercises.py
├── app/api/v1/endpoints/routines.py
├── crud.py (8+ funciones)
├── tests/ (4+ archivos)
└── alembic/versions/bcc1303c427a_create_global_tables.py

TOTAL: 26 archivos afectados
```

---

## 9. CONCLUSIÓN

**El MED-08 identifica un problema real: 90-95% de duplicidad en 3 pares de modelos.**

**Sin embargo, consolidar ahora es PREMATURO porque:**

1. ✗ Complejidad desproporcionada vs beneficio
2. ✗ Riesgos críticos sin mitigación lista
3. ✗ 30-40 horas de esfuerzo NO presupuestadas
4. ✗ Falta infraestructura (versioning, feature flags)
5. ✗ Timing malo en cronograma de refactoring

**RECOMENDACIÓN FINAL: POSPONER a Semana 6-7 con re-evaluación de negocio.**

*Firmado por Database Architect - 2026-01-16*

---
