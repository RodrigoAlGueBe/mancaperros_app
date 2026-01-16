# Guía de Migración - Índices de Base de Datos

## Resumen

Se han creado migraciones para agregar índices de rendimiento a la base de datos de mancaperros_app.

### Estado Actual

1. **Migración Existente** (`f1a2b3c4d5e6_add_database_indexes.py`):
   - Ya aplicada
   - Contiene índices básicos en users, exercise_plans, rutines, exercises, user_tracker

2. **Nueva Migración** (`a2b3c4d5e6f7_add_additional_database_indexes.py`):
   - Pendiente de aplicar
   - Agrega índices compuestos adicionales
   - Optimiza consultas complejas con múltiples filtros

## Archivos Creados

```
migrations/
├── README.md                          # Documentación completa
├── MIGRATION_GUIDE.md                 # Esta guía
├── apply_migrations.py                # Script Python para aplicar migraciones SQL
├── 000_all_indexes_complete.sql      # Referencia completa de todos los índices
└── 001_add_additional_indexes.sql    # Migración incremental (solo índices faltantes)

alembic/versions/
├── f1a2b3c4d5e6_add_database_indexes.py           # Migración existente
└── a2b3c4d5e6f7_add_additional_database_indexes.py # Nueva migración
```

## Índices que se Agregarán

La nueva migración agrega 3 índices adicionales:

1. **idx_exercise_plans_type**
   - Tabla: `exercise_plans`
   - Columna: `exercise_plan_type`
   - Propósito: Filtrar planes por tipo (fuerza, cardio, etc.)

2. **idx_rutines_plan_group** (índice compuesto)
   - Tabla: `rutines`
   - Columnas: `exercise_plan_id`, `rutine_group`
   - Propósito: Consultas que filtran por plan Y grupo simultáneamente

3. **idx_user_tracker_user_type** (índice compuesto)
   - Tabla: `user_tracker`
   - Columnas: `user_id`, `info_type`
   - Propósito: Consultas que buscan métricas específicas de un usuario

## Métodos de Aplicación

### Método 1: Usar Alembic (Recomendado)

```bash
# Navegar al directorio del proyecto
cd C:\Users\Rodrigo\Desktop\proyectos\mancaperros_app\code\backend\mancaperros_app

# Ver migraciones pendientes
alembic current
alembic history

# Aplicar la nueva migración
alembic upgrade head

# O aplicar solo esta migración específica
alembic upgrade a2b3c4d5e6f7
```

**Ventajas:**
- Control de versiones automático
- Fácil rollback si hay problemas
- Historial de migraciones rastreado
- Ideal para desarrollo y producción

### Método 2: Script Python

```bash
# Ver qué SQL se ejecutará (dry run)
python migrations/apply_migrations.py --file 001_add_additional_indexes.sql --dry-run

# Aplicar migración
python migrations/apply_migrations.py --file 001_add_additional_indexes.sql

# Aplicar y verificar
python migrations/apply_migrations.py --file 001_add_additional_indexes.sql --verify

# Solo verificar índices existentes
python migrations/apply_migrations.py --verify-only
```

**Ventajas:**
- No requiere Alembic instalado
- Útil para troubleshooting
- Verificación integrada de índices

### Método 3: SQL Directo

```bash
# Conectar a la base de datos SQLite
sqlite3 mancaperros_app.db

# Ejecutar el script SQL
.read migrations/001_add_additional_indexes.sql

# Verificar índices creados
SELECT name, tbl_name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%';

# Salir
.quit
```

**Ventajas:**
- Control total sobre la ejecución
- Útil para debugging
- No requiere dependencias Python

## Verificación Post-Migración

### Opción 1: Verificar con Script Python

```bash
python migrations/apply_migrations.py --verify-only
```

Esto mostrará:
- Todos los índices existentes organizados por tabla
- Estado de los índices recomendados (OK/MISSING)
- Lista de índices faltantes si los hay

### Opción 2: Verificar con SQLite

```sql
-- Ver todos los índices personalizados
SELECT
    name as index_name,
    tbl_name as table_name,
    sql as definition
FROM sqlite_master
WHERE type='index' AND name LIKE 'idx_%'
ORDER BY tbl_name, name;
```

### Opción 3: Verificar con Alembic

```bash
# Ver versión actual
alembic current

# Debería mostrar:
# a2b3c4d5e6f7 (head)
```

## Análisis de Rendimiento

Después de aplicar los índices, puedes analizar su impacto:

```sql
-- Ver plan de ejecución ANTES de crear índices
EXPLAIN QUERY PLAN
SELECT * FROM rutines
WHERE exercise_plan_id = 1 AND rutine_group = 'A';

-- Crear índices (aplicar migración)

-- Ver plan de ejecución DESPUÉS de crear índices
EXPLAIN QUERY PLAN
SELECT * FROM rutines
WHERE exercise_plan_id = 1 AND rutine_group = 'A';

-- Debería mostrar: "SEARCH TABLE rutines USING INDEX idx_rutines_plan_group"
```

## Rollback (Revertir)

### Con Alembic

```bash
# Revertir a la migración anterior
alembic downgrade -1

# O revertir a versión específica
alembic downgrade f1a2b3c4d5e6
```

### Con SQL

```sql
-- Eliminar los índices manualmente
DROP INDEX IF EXISTS idx_exercise_plans_type;
DROP INDEX IF EXISTS idx_rutines_plan_group;
DROP INDEX IF EXISTS idx_user_tracker_user_type;
```

## Impacto Esperado

### Mejoras de Rendimiento

1. **Consultas por tipo de plan** (~50-70% más rápido)
   ```python
   # Consulta beneficiada:
   plans = db.query(ExercisePlan).filter(
       ExercisePlan.exercise_plan_type == "strength"
   ).all()
   ```

2. **Consultas de rutinas con filtro compuesto** (~60-80% más rápido)
   ```python
   # Consulta beneficiada:
   rutines = db.query(Rutine).filter(
       Rutine.exercise_plan_id == plan_id,
       Rutine.rutine_group == "A"
   ).all()
   ```

3. **Consultas de tracking específico** (~50-70% más rápido)
   ```python
   # Consulta beneficiada:
   tracker = db.query(UserTracker).filter(
       UserTracker.user_id == user_id,
       UserTracker.info_type == "weight"
   ).all()
   ```

### Overhead de Escritura

- **Impacto en INSERT**: +2-5% tiempo de ejecución
- **Impacto en UPDATE**: +3-7% tiempo de ejecución (solo si se actualizan columnas indexadas)
- **Impacto en DELETE**: +2-5% tiempo de ejecución
- **Espacio en disco**: ~5-15% adicional

**Conclusión:** El trade-off es favorable para aplicaciones con más lecturas que escrituras (típico en aplicaciones web).

## Troubleshooting

### Error: "table already has an index named idx_xxx"

**Solución:** El índice ya existe. Verifica con:
```bash
python migrations/apply_migrations.py --verify-only
```

### Error: "no such table: xxx"

**Solución:** Asegúrate de que las tablas existan. Aplica primero las migraciones de creación de tablas:
```bash
alembic upgrade head
```

### Error: "database is locked"

**Solución:** Cierra todas las conexiones a la base de datos:
- Detén el servidor de desarrollo
- Cierra clientes SQLite abiertos
- Intenta nuevamente

### Los índices no mejoran el rendimiento

**Causas posibles:**
1. Base de datos muy pequeña (índices solo ayudan con datos suficientes)
2. Necesitas ejecutar `ANALYZE` para actualizar estadísticas
3. La consulta no usa las columnas indexadas en el WHERE

**Solución:**
```sql
-- Actualizar estadísticas del optimizador
ANALYZE;

-- Verificar que la consulta use el índice
EXPLAIN QUERY PLAN SELECT ...;
```

## Siguiente Paso

**Recomendación:** Usa Alembic para aplicar la migración

```bash
cd C:\Users\Rodrigo\Desktop\proyectos\mancaperros_app\code\backend\mancaperros_app
alembic upgrade head
```

Esto aplicará automáticamente la nueva migración `a2b3c4d5e6f7_add_additional_database_indexes.py` con los índices adicionales.

## Referencias

- Migración Alembic: `alembic/versions/a2b3c4d5e6f7_add_additional_database_indexes.py`
- Migración SQL: `migrations/001_add_additional_indexes.sql`
- Documentación completa: `migrations/README.md`
- Script de aplicación: `migrations/apply_migrations.py`
