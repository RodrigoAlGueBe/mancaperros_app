# MED-08: Consolidación User/Global - RESUMEN EJECUTIVO

**Fecha:** 2026-01-16
**Estado:** RECOMENDACIÓN: POSPONER
**Urgencia:** BAJA
**Riesgo:** ALTO

---

## 1. EL PROBLEMA EN 30 SEGUNDOS

Tu proyecto tiene 3 pares de modelos con 90-95% código duplicado:

```
Exercise_plan          ↔ Exercise_plan_global
Rutine                 ↔ Rutine_global
Exercise               ↔ Exercise_global
```

Estos modelos viven en tablas separadas pero hacen esencialmente lo MISMO.

**Pregunta:** ¿Consolidarlos?

---

## 2. DIFERENCIAS CLAVE

### Exercise_plan vs Exercise_plan_global

| Campo | Personal | Global | Diferencia |
|-------|----------|--------|-----------|
| `user_owner_id` | nullable=True | - | "Usuario propietario" |
| `user_creator_id` | - | nullable=False | "Usuario creador" |
| **Semántica** | Asignado a usuario | Plantilla reutilizable | CRÍTICA |

### Rutine vs Rutine_global

| Aspecto | Personal | Global |
|--------|----------|--------|
| Estructura | 100% idéntica | 100% idéntica |
| FK destino | exercise_plans | exercise_plans_global |
| Difference | SOLO la tabla destino diferente | |

### Exercise vs Exercise_global

| Aspecto | Personal | Global |
|--------|----------|--------|
| Estructura | 95% idéntica | 95% idéntica |
| FK destino | rutines | rutines_global |
| Nullable | Mixto | Todas NOT NULL |

---

## 3. IMPACTO DE CONSOLIDAR

### Cambios Requeridos

| Componente | Archivos | Complejidad | Duración |
|-----------|----------|-----------|----------|
| Models | 6 | ALTA | 4-6h |
| Repositorios | 6 | ALTA | 6-8h |
| Schemas | 14 clases | MEDIA | 3-4h |
| Endpoints | 2 | MEDIA | 2-3h |
| Tests | 4 | ALTA | 6-8h |
| Migraciones BD | 1 | CRÍTICA | 3-5h |
| **TOTAL** | **26+ archivos** | **CRÍTICA** | **30-40 horas** |

### Archivos Críticos Afectados

```
infrastructure/database/models/
├── exercise_plan.py              (85 líneas)
├── exercise_plan_global.py       (90 líneas)
├── routine.py                    (94 líneas)
├── routine_global.py             (109 líneas)
├── exercise.py                   (56 líneas)
└── exercise_global.py            (79 líneas)

infrastructure/database/repositories/
├── exercise_plan_repository.py   (351 líneas - contiene create_from_global())
├── exercise_plan_global_repository.py (317 líneas)
├── routine_repository.py
├── routine_global_repository.py
├── exercise_repository.py
└── exercise_global_repository.py

app/api/v1/endpoints/
├── exercises.py     (30+ líneas con Exercise_plan_global)
└── routines.py      (20+ líneas con Rutine_global)

schemas.py          (14 clases relacionadas)
tests/              (4+ archivos de tests)
alembic/            (migraciones)
```

---

## 4. RIESGOS CRÍTICOS

### Riesgo 1: Pérdida de Semántica (CRÍTICO)
```
Hoy: Claro qué es "personal" vs "global"
Consolidado: Mezcla conceptos diferentes en una tabla
```
**Solución:** Usar discriminador booleano (is_global), pero reduce claridad.

### Riesgo 2: Ruptura de Relaciones (CRÍTICO)
```
Exercise.rutine_id → ForeignKey("rutines.rutine_id")
Exercise_global.rutine_id → ForeignKey("rutines_global.rutine_id")

Si consolidas a UNA tabla, ¿qué FK usas?
```
Necesitas polimorfismo SQLAlchemy (complejo).

### Riesgo 3: Migración Destructiva (CRÍTICO)
```
- Renumerar IDs en tablas puede quebrar referencias
- ¿Qué pasa con datos históricos?
- ¿Backup y rollback planificado?
```

### Riesgo 4: Lógica de Negocio (CRÍTICO)
```python
# Hoy - claro
personal = Exercise_plan.query.filter(user_id=123)
global = Exercise_plan_global.query.filter(user_creator_id=456)

# Consolidado - UNION requerida, queries más complejas
all_plans = Exercise_plan.query.filter(
    or_(user_id=123, created_by=456)
)
```

### Riesgo 5: Performance (MODERADO)
- Tablas más grandes (~6x si 1/3 global, 2/3 personal)
- Índices existentes pueden no ser óptimos
- Scans de tabla completa más costosos

---

## 5. MATRIZ DE DECISIÓN

```
                     Urgencia: 2/10 (BAJA)
                    Complejidad: 8/10 (ALTA)
                      Riesgo: 8/10 (ALTO)
                   Beneficio: 5/10 (MODERADO)

Recomendación = POSPONER
```

---

## 6. ALTERNATIVAS (SIN CONSOLIDACIÓN)

### Opción A: Mixins (Compartir código sin consolidar BD)
```python
class ExercisePlanMixin:
    """Campos compartidos"""
    exercise_plan_name = Column(String)
    exercise_plan_type = Column(String)

class Exercise_plan(Base, ExercisePlanMixin):
    __tablename__ = "exercise_plans"

class Exercise_plan_global(Base, ExercisePlanMixin):
    __tablename__ = "exercise_plans_global"
```

**Ventajas:** Reutilización, cero riesgo
**Desventajas:** Todavía hay duplicación (aceptable)

### Opción B: Vistas SQL
Crear VISTAs que unifiquen datos sin cambiar BD:
```sql
CREATE VIEW v_exercise_plans AS
SELECT ... FROM exercise_plans
UNION ALL
SELECT ... FROM exercise_plans_global;
```

**Ventajas:** Cero cambios en BD, queries unificadas
**Desventajas:** Vistas no updatable

---

## 7. RECOMENDACIÓN FINAL

### DECISIÓN: **POSPONER CONSOLIDACIÓN**

**Por qué:**

✗ **Complejidad desproporcionada** (30-40 horas para 5-10% beneficio)
✗ **Riesgos críticos** sin mitigación lista
✗ **Timing malo** (Semana 5 enfocada en DevOps/CI-CD)
✗ **Infraestructura falta** (versioning, feature flags)
✗ **Preguntas pendientes** (¿en producción? ¿datos históricos?)

**Cuándo reconsidera:** Semana 6-7 (si:)
- PM aprueba como prioritario
- Hay tiempo asignado (40 horas)
- Datos de producción analizados
- API versioning implementado

---

## 8. ACCIONES INMEDIATAS

- [ ] Documentar esta decisión en REFACTORING_PROGRESS.md
- [ ] Preguntar a PM: ¿Es consolidación prioritaria?
- [ ] Evaluar si Mixins son suficientes para reducir duplicación
- [ ] Archivar MED-08 como "DEFERRED_WEEK_6-7"

---

## 9. CONCLUSIÓN

**MED-08 es un problema válido (90-95% duplicación), pero:**

**CONSOLIDA SI:**
- Urgencia de negocio (ahora no hay)
- Tiempo asignado (30-40 horas)
- Infraestructura lista (versioning, rollback)
- Análisis de BD completado

**POSPÓN HASTA TENER TODO ESTO.**

**Código actual está limpio y documentado. No urgente arreglarlo.**

---

*Database Architect - 2026-01-16*
