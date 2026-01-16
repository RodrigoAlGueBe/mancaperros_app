# Resumen de Migración - Índices de Base de Datos

## Estado: APLICADO (2026-01-15)

Se ha creado una nueva migración de base de datos para agregar índices de rendimiento adicionales.

## Archivos Creados

### Migración Alembic (Recomendado)
- `alembic/versions/a2b3c4d5e6f7_add_additional_database_indexes.py`
  - Nueva migración con índices adicionales
  - Incluye upgrade() y downgrade()
  - Listo para aplicar con Alembic

### Migraciones SQL Alternativas
- `migrations/001_add_additional_indexes.sql` - Migración incremental (solo nuevos índices)
- `migrations/000_all_indexes_complete.sql` - Referencia completa de todos los índices
- `migrations/README.md` - Documentación detallada
- `migrations/MIGRATION_GUIDE.md` - Guía paso a paso

### Herramientas de Gestión
- `migrations/apply_migrations.py` - Script Python para aplicar SQL
- `migrations/check_indexes.sh` - Verificación rápida (Linux/Mac)
- `migrations/check_indexes.ps1` - Verificación rápida (Windows)

## Índices Agregados

### 1. idx_exercise_plans_type
- **Tabla:** exercise_plans
- **Columna:** exercise_plan_type
- **Propósito:** Filtrar planes de ejercicio por tipo
- **Consultas beneficiadas:**
  ```python
  plans = db.query(ExercisePlan).filter(
      ExercisePlan.exercise_plan_type == "strength"
  ).all()
  ```

### 2. idx_rutines_plan_group (Índice Compuesto)
- **Tabla:** rutines
- **Columnas:** exercise_plan_id, rutine_group
- **Propósito:** Consultas que filtran por plan Y grupo
- **Consultas beneficiadas:**
  ```python
  rutines = db.query(Rutine).filter(
      Rutine.exercise_plan_id == plan_id,
      Rutine.rutine_group == "A"
  ).all()
  ```

### 3. idx_user_tracker_user_type (Índice Compuesto)
- **Tabla:** user_tracker
- **Columnas:** user_id, info_type
- **Propósito:** Consultas de métricas específicas por usuario
- **Consultas beneficiadas:**
  ```python
  weight_data = db.query(UserTracker).filter(
      UserTracker.user_id == user_id,
      UserTracker.info_type == "weight"
  ).all()
  ```

## Cómo Aplicar (Opción Recomendada)

```bash
# 1. Navegar al directorio del proyecto
cd C:\Users\Rodrigo\Desktop\proyectos\mancaperros_app\code\backend\mancaperros_app

# 2. Ver el estado actual
alembic current

# 3. Aplicar la migración
alembic upgrade head

# 4. Verificar
alembic current
# Debería mostrar: a2b3c4d5e6f7 (head)
```

## Alternativas de Aplicación

### Opción 2: Script Python
```bash
python migrations/apply_migrations.py --file 001_add_additional_indexes.sql --verify
```

### Opción 3: SQL Directo
```bash
sqlite3 mancaperros_app.db < migrations/001_add_additional_indexes.sql
```

## Verificación

### PowerShell (Windows)
```powershell
powershell -ExecutionPolicy Bypass -File migrations\check_indexes.ps1
```

### Python
```bash
python migrations/apply_migrations.py --verify-only
```

### SQL
```bash
sqlite3 mancaperros_app.db "SELECT name, tbl_name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%' ORDER BY tbl_name;"
```

## Impacto Esperado

### Mejoras de Rendimiento
- Consultas por tipo de plan: 50-70% más rápido
- Consultas de rutinas con filtro compuesto: 60-80% más rápido
- Consultas de tracking específico: 50-70% más rápido

### Trade-offs
- INSERT: +2-5% tiempo
- UPDATE: +3-7% tiempo (solo columnas indexadas)
- DELETE: +2-5% tiempo
- Espacio en disco: +5-15%

**Conclusión:** Favorable para aplicaciones con más lecturas que escrituras (caso típico en apps web).

## Rollback

Si necesitas revertir la migración:

```bash
# Con Alembic
alembic downgrade -1

# Con SQL
sqlite3 mancaperros_app.db
DROP INDEX IF EXISTS idx_exercise_plans_type;
DROP INDEX IF EXISTS idx_rutines_plan_group;
DROP INDEX IF EXISTS idx_user_tracker_user_type;
```

## Índices Completos en la Base de Datos

Después de aplicar esta migración, tendrás los siguientes índices:

### Tabla users
- idx_users_email
- idx_users_user_name

### Tabla exercise_plans
- idx_exercise_plans_user_owner_id
- idx_exercise_plans_type ← **NUEVO**

### Tabla rutines
- idx_rutines_exercise_plan_id
- idx_rutines_plan_group ← **NUEVO** (compuesto)

### Tabla exercises
- idx_exercises_rutine_id

### Tabla user_tracker
- idx_user_tracker_user_id
- idx_user_tracker_user_type ← **NUEVO** (compuesto)

**Total:** 9 índices personalizados (3 nuevos)

## Próximos Pasos

1. **Revisar** la migración en `alembic/versions/a2b3c4d5e6f7_add_additional_database_indexes.py`
2. **Aplicar** con `alembic upgrade head`
3. **Verificar** con el script de verificación
4. **Monitorear** el rendimiento de las consultas después de aplicar

## Documentación Adicional

- Guía completa: `migrations/MIGRATION_GUIDE.md`
- Documentación de uso: `migrations/README.md`
- Referencia SQL: `migrations/000_all_indexes_complete.sql`

## Notas Importantes

1. La migración usa `CREATE INDEX IF NOT EXISTS` para evitar errores si los índices ya existen
2. Todos los índices tienen tanto upgrade() como downgrade() implementados
3. Los índices compuestos mejoran consultas con múltiples condiciones WHERE
4. No olvides ejecutar `ANALYZE;` después de crear índices para actualizar estadísticas

## Contacto y Soporte

Si encuentras problemas:
1. Revisa `migrations/MIGRATION_GUIDE.md` sección "Troubleshooting"
2. Verifica el estado con `python migrations/apply_migrations.py --verify-only`
3. Consulta los logs de Alembic si la migración falla

---

**Fecha de creación:** 2026-01-11
**Fecha de aplicación:** 2026-01-15
**Migración:** a2b3c4d5e6f7
**Depende de:** f1a2b3c4d5e6
**Estado:** APLICADO
