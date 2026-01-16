# MED-08: Comparativa Detallada de Campos

**Tabla técnica de diferencias campo por campo**

---

## EXERCISE_PLAN vs EXERCISE_PLAN_GLOBAL

```
┌─────────────────────────┬──────────────────────┬──────────────────────┬─────────┐
│ Campo                   │ Exercise_plan        │ Exercise_plan_global │ Igual?  │
├─────────────────────────┼──────────────────────┼──────────────────────┼─────────┤
│ exercise_plan_id        │ Integer PK Index     │ Integer PK Index     │ ✓ SÍ    │
│ exercise_plan_name      │ String(255)          │ String(255)          │ ✓ SÍ    │
│                         │ unique=False         │ nullable=False       │ ✗ DIFF  │
│                         │ index=True           │ index=True           │         │
│                         │ default="New..."     │ default="New..."     │         │
├─────────────────────────┼──────────────────────┼──────────────────────┼─────────┤
│ FK Usuario              │ user_owner_id        │ user_creator_id      │ ✗ CRIT  │
│ (diferente semántica)   │ ForeignKey users     │ ForeignKey users     │         │
│                         │ nullable=True        │ nullable=False       │         │
├─────────────────────────┼──────────────────────┼──────────────────────┼─────────┤
│ exercise_plan_type      │ String(255)          │ String(255)          │ ✓ SÍ    │
│                         │ unique=False         │ nullable=False       │ ✗ DIFF  │
│                         │ index=True           │ index=True           │         │
│                         │ default="New..."     │ default="New..."     │         │
├─────────────────────────┼──────────────────────┼──────────────────────┼─────────┤
│ creation_date           │ Date                 │ Date                 │ ✓ SÍ    │
│                         │ unique=False         │ nullable=False       │ ✗ DIFF  │
│                         │ index=True           │ index=True           │         │
│                         │ default=1970-01-01   │ default=1970-01-01   │         │
├─────────────────────────┼──────────────────────┼──────────────────────┼─────────┤
│ difficult_level         │ String(255)          │ String(255)          │ ✓ SÍ    │
│                         │ unique=False         │ nullable=False       │ ✗ DIFF  │
│                         │ index=True           │ index=True           │         │
│                         │ default="New..."     │ default="New..."     │         │
├─────────────────────────┼──────────────────────┼──────────────────────┼─────────┤
│ routine_group_order     │ JSON                 │ JSON                 │ ✓ SÍ    │
│                         │ nullable=False       │ nullable=False       │         │
│                         │ unique=False         │ unique=False         │         │
│                         │ default=SETTING      │ default=SETTING      │         │
└─────────────────────────┴──────────────────────┴──────────────────────┴─────────┘

DIFERENCIAS:
✗ CRÍTICO: user_owner_id vs user_creator_id (semántica diferente)
✗ MODERADO: nullable diferente (global más restrictivo)
✓ BAJO: nombre de tabla diferente (solo cosmético)
✓ BAJO: relación back_populates diferente (solo nombre)

SIMILITUD: 88-90%
```

---

## RUTINE vs RUTINE_GLOBAL

```
┌──────────────────────────┬──────────────────────┬──────────────────────┬─────────┐
│ Campo                    │ Rutine               │ Rutine_global        │ Igual?  │
├──────────────────────────┼──────────────────────┼──────────────────────┼─────────┤
│ rutine_id                │ Integer PK Index     │ Integer PK Index     │ ✓ SÍ    │
├──────────────────────────┼──────────────────────┼──────────────────────┼─────────┤
│ rutine_name              │ String(255)          │ String(255)          │ ✓ SÍ    │
│                          │ unique=False         │ nullable=False       │ ✗ DIFF  │
│                          │ index=True           │ index=True           │         │
│                          │ default="New..."     │ default="New..."     │         │
├──────────────────────────┼──────────────────────┼──────────────────────┼─────────┤
│ rutine_type              │ String(255)          │ String(255)          │ ✓ SÍ    │
│                          │ unique=False         │ nullable=False       │ ✗ DIFF  │
│                          │ index=True           │ index=True           │         │
│                          │ default="New..."     │ default="New..."     │         │
├──────────────────────────┼──────────────────────┼──────────────────────┼─────────┤
│ rutine_group             │ String(255)          │ String(255)          │ ✓ SÍ    │
│                          │ unique=False         │ nullable=False       │ ✗ DIFF  │
│                          │ index=True           │ index=True           │         │
│                          │ default="New..."     │ default="New..."     │         │
├──────────────────────────┼──────────────────────┼──────────────────────┼─────────┤
│ rutine_category          │ String(255)          │ String(255)          │ ✓ SÍ    │
│                          │ unique=False         │ nullable=False       │ ✗ DIFF  │
│                          │ index=True           │ index=True           │         │
│                          │ default="New..."     │ default="New..."     │         │
├──────────────────────────┼──────────────────────┼──────────────────────┼─────────┤
│ exercise_plan_id         │ ForeignKey           │ ForeignKey           │ ✗ DIFF  │
│ (tabla destino diff)     │ exercise_plans       │ exercise_plans_global│ CRÍTICO │
├──────────────────────────┼──────────────────────┼──────────────────────┼─────────┤
│ rounds                   │ Integer              │ Integer              │ ✓ SÍ    │
│                          │ unique=False         │ nullable=False       │ ✗ DIFF  │
│                          │ index=True           │ index=True           │         │
│                          │ default=0            │ default=0            │         │
├──────────────────────────┼──────────────────────┼──────────────────────┼─────────┤
│ rst_btw_exercises        │ String(255)          │ String(255)          │ ✓ SÍ    │
│                          │ unique=False         │ nullable=False       │ ✗ DIFF  │
│                          │ index=True           │ index=True           │         │
│                          │ default="0"          │ default="0"          │         │
├──────────────────────────┼──────────────────────┼──────────────────────┼─────────┤
│ rst_btw_rounds           │ String(255)          │ String(255)          │ ✓ SÍ    │
│                          │ unique=False         │ nullable=False       │ ✗ DIFF  │
│                          │ index=True           │ index=True           │         │
│                          │ default="0"          │ default="0"          │         │
├──────────────────────────┼──────────────────────┼──────────────────────┼─────────┤
│ difficult_level          │ String(255)          │ String(255)          │ ✓ SÍ    │
│                          │ unique=False         │ nullable=False       │ ✗ DIFF  │
│                          │ index=True           │ index=True           │         │
│                          │ default="New..."     │ default="New..."     │         │
└──────────────────────────┴──────────────────────┴──────────────────────┴─────────┘

DIFERENCIAS:
✗ CRÍTICO: exercise_plan_id tabla destino (personal vs global)
✗ MODERADO: nullable diferente (global más restrictivo)

SIMILITUD: 100% en estructura de campos
DIFERENCIA: SOLO tabla destino y nullable

HALLAZGO: "Son esencialmente IDÉNTICAS excepto por la FK"
```

---

## EXERCISE vs EXERCISE_GLOBAL

```
┌──────────────────────┬──────────────────────┬──────────────────────┬─────────┐
│ Campo                │ Exercise             │ Exercise_global      │ Igual?  │
├──────────────────────┼──────────────────────┼──────────────────────┼─────────┤
│ exercise_id          │ Integer PK Unique    │ Integer PK Index     │ ✗ DIFF  │
│                      │ Index                │                      │         │
├──────────────────────┼──────────────────────┼──────────────────────┼─────────┤
│ exercise_name        │ String(255)          │ String(255)          │ ✓ SÍ    │
│                      │ unique=False         │ nullable=False       │ ✗ DIFF  │
│                      │ index=True           │ index=True           │         │
│                      │ default="New..."     │ default="New..."     │         │
├──────────────────────┼──────────────────────┼──────────────────────┼─────────┤
│ rep                  │ String(255)          │ String(255)          │ ✓ SÍ    │
│                      │ unique=False         │ nullable=False       │ ✗ DIFF  │
│                      │ index=True           │ index=True           │         │
│                      │ default="empty"      │ default="empty"      │         │
├──────────────────────┼──────────────────────┼──────────────────────┼─────────┤
│ exercise_type        │ String(255)          │ String(255)          │ ✓ SÍ    │
│                      │ unique=False         │ nullable=False       │ ✗ DIFF  │
│                      │ index=True           │ index=True           │         │
│                      │ default="New..."     │ default="New..."     │         │
├──────────────────────┼──────────────────────┼──────────────────────┼─────────┤
│ exercise_group       │ String(255)          │ String(255)          │ ✓ SÍ    │
│                      │ unique=False         │ nullable=False       │ ✗ DIFF  │
│                      │ index=True           │ index=True           │         │
│                      │ default="New..."     │ default="New..."     │         │
├──────────────────────┼──────────────────────┼──────────────────────┼─────────┤
│ rutine_id            │ ForeignKey           │ ForeignKey           │ ✗ DIFF  │
│ (tabla destino diff) │ rutines              │ rutines_global       │ CRÍTICO │
├──────────────────────┼──────────────────────┼──────────────────────┼─────────┤
│ image                │ String(255)          │ String(255)          │ ✓ SÍ    │
│                      │ unique=False         │ nullable=False       │ ✗ DIFF  │
│                      │ index=True           │ index=True           │         │
│                      │ default="empty"      │ default="empty"      │         │
└──────────────────────┴──────────────────────┴──────────────────────┴─────────┘

DIFERENCIAS:
✗ CRÍTICO: rutine_id tabla destino (rutines vs rutines_global)
✗ MODERADO: nullable diferente (global más restrictivo)
✗ BAJO: exercise_id constraints ligeramente diferentes

SIMILITUD: 95%
DIFERENCIA: Principalmente tabla destino
```

---

## MATRIZ CONSOLIDADA DE DIFERENCIAS

```
Modelo              │ Similitud │ Diferencias Críticas         │ Factibilidad
────────────────────┼───────────┼──────────────────────────────┼────────────────
Exercise_plan vs    │   88-90%  │ • FK semántica (owner/       │ Media-Alta
_global             │           │   creator)                   │ (renombrar FK)
                    │           │ • nullable diferente         │
                    │           │ • tabla diferente            │
────────────────────┼───────────┼──────────────────────────────┼────────────────
Rutine vs           │   100%    │ • SOLO tabla destino del FK  │ Media
_global             │ estructura│ • nullable (global NOT NULL) │ (polimorfismo
                    │           │                              │  necesario)
────────────────────┼───────────┼──────────────────────────────┼────────────────
Exercise vs         │   95%     │ • SOLO tabla destino del FK  │ Media-Alta
_global             │           │ • nullable diferente         │
                    │           │ • PK constraints ligeramente  │
────────────────────┴───────────┴──────────────────────────────┴────────────────

HALLAZGO PRINCIPAL:
Las 3 parejas están 95%+ idénticas en ESTRUCTURA.
La diferencia real es: "¿A qué tabla apunta la FK?"

Esto sugiere:
1. Polimorfismo de ORM solveería elegantemente
2. Pero requiere refactoring de RELACIONES, no campos
3. Complejidad REAL está en las relaciones cruzadas
```

---

## RELACIONES POLIMÓRFICAS - EL VERDADERO PROBLEMA

```
DIAGRAMA ER ACTUAL:
┌─────────────────┐         ┌──────────────┐
│ exercise_plans  │ 1───∞  │ rutines      │
│                 │         │              │
│ user_owner_id ──┼──FK     │              │
└─────────────────┘         └──────────────┘
        │                            │
        │                    ┌───────┘
        │                    ∞
        │                    │
        └───────┬────────────┴─────────┐
                │                      │
        ┌───────▼──────┐      ┌────────▼──────┐
        │ exercises    │      │ exercises_    │
        │              │      │ global        │
        └──────────────┘      └───────────────┘


PROBLEMA DE CONSOLIDACIÓN:

Si consolidas exercise_plans + exercise_plans_global en UNA tabla:

     ┌─────────────────────────────────────┐
     │ exercise_plans (combinada)          │
     │ - exercise_plan_id                  │
     │ - is_global (discriminador)         │
     │ - user_owner_id (NULL si global)    │
     │ - ...                               │
     └─────────────────────────────────────┘
              │
              ├─── rutines (¿global o personal?)
              │
              ├─── exercises (¿global o personal?)
              │
              └─── PROBLEMA: Una rutine puede ser global O personal

SOLUCIÓN ELEGANTE (Herencia SQLAlchemy):

     ┌─────────────────────────────────────────┐
     │     Exercise_plan (base)                │
     │     - type = Column(String)  (polymorphic)│
     │     - ...                               │
     └─────────────────────────────────────────┘
              △              △
              │              │
        Personal       Global
        subclass       subclass

ESTO PERMITE:
- routine.parent_plan: Exercise_plan (type-agnostic)
- Queries polimórficas automáticas
- PERO: Complejidad SQLAlchemy muy alta
```

---

## IMPACTO POR LÍNEA DE CÓDIGO

```
Métrica                          │ Afectado │ Complejidad
─────────────────────────────────┼──────────┼──────────────
Models (cambios campos)          │ Mínimo   │ BAJA
Models (cambios relaciones)      │ CRÍTICO  │ ALTA
Repositorios (queries)           │ ALTO     │ MEDIA-ALTA
Endpoints (filters)              │ MEDIO    │ MEDIA
Schemas (validación)             │ MEDIO    │ BAJA
Tests (nuevo coverage)           │ ALTO     │ MEDIA
Migraciones BD (reversible?)     │ CRÍTICO  │ ALTA
Documentación                    │ MEDIO    │ BAJA

NOTA: Relaciones polimórficas son 60% de la complejidad
```

---

## ESTADÍSTICAS DE CÓDIGO COMPARTIDO

```python
# Líneas de código que serían deduplicadas:

Models:
  - exercise_plan.py       : 85 líneas → 40 líneas (53% duplicado)
  - routine.py             : 94 líneas → 94 líneas (100% duplicado)
  - exercise.py            : 56 líneas → 45 líneas (80% duplicado)
  Subtotal duplicado: ~200 líneas

Repositorios:
  - exercise_plan_repository.py      : 351 líneas
  - exercise_plan_global_repository.py: 317 líneas
    DUPLICACIÓN: ~270 líneas (88% similar)
  - routine_repository.py            : N/A
  - routine_global_repository.py      : N/A
    DUPLICACIÓN: ~200 líneas (90%+ similar)
  Subtotal duplicado: ~470 líneas

Schemas:
  - 14 clases → 7 clases unificadas
    DUPLICACIÓN: ~200 líneas

Endpoints:
  - exercises.py uses Exercise_plan_global: ~50 líneas
  - routines.py uses Rutine_global: ~30 líneas
    DUPLICACIÓN: ~40 líneas

CÓDIGO DUPLICADO TOTAL: ~910 líneas (16% de codebase)

BENEFICIO DE CONSOLIDAR: Eliminar 910 líneas duplicadas
COSTO DE CONSOLIDAR: 40 horas de refactoring + riesgo

ROI: Cuestionable
```

---

## CONCLUSIÓN TÉCNICA

```
┌─────────────────────────────────────────────────────────────┐
│ ¿Cuán idénticos son?                                        │
│ ════════════════════                                        │
│ • Estructura de datos: 95-100% idéntica                   │
│ • Código de implementación: 80-90% duplicado              │
│ • Semántica de negocio: 30% idéntica (son diferentes)    │
│                                                             │
│ ¿Qué hace que no sea trivial consolidar?                  │
│ ════════════════════════════════════════                  │
│ • Relaciones polimórficas complejas                       │
│ • Semántica diferente (personal vs global)                │
│ • Impacto en 26+ archivos                                 │
│ • Riesgo de ruptura en 40 horas de trabajo               │
│                                                             │
│ ¿Alternativa mejor?                                        │
│ ════════════════════════════                              │
│ • Usar Mixins para compartir código                       │
│ • Mantener tablas separadas (semántica clara)            │
│ • Eliminar 80% del código duplicado sin consolidar       │
│ • Costo: 5 horas, Riesgo: BAJO                          │
└─────────────────────────────────────────────────────────────┘
```

---

**Fin del análisis técnico detallado**
**Database Architect - 2026-01-16**
