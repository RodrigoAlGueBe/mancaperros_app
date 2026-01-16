# Database Migrations - SQL Scripts

Esta carpeta contiene scripts SQL para migraciones de base de datos que pueden ejecutarse manualmente como alternativa a Alembic.

## Archivos Disponibles

### 000_all_indexes_complete.sql
Script de referencia que contiene TODOS los índices recomendados para la base de datos. Incluye:
- Índices simples para búsquedas y joins
- Índices compuestos para consultas complejas
- Documentación del propósito de cada índice
- Comandos para verificar y eliminar índices

### 001_add_additional_indexes.sql
Migración incremental que agrega los índices adicionales que faltan:
- `idx_exercise_plans_type` - Filtra planes por tipo
- `idx_rutines_plan_group` - Índice compuesto para plan + grupo
- `idx_user_tracker_user_type` - Índice compuesto para usuario + tipo de info

## Cómo Usar

### Opción 1: Usar Alembic (Recomendado)

```bash
# Desde el directorio del proyecto backend
cd C:\Users\Rodrigo\Desktop\proyectos\mancaperros_app\code\backend\mancaperros_app

# Ver el estado actual de las migraciones
alembic current

# Ver el historial de migraciones
alembic history

# Aplicar todas las migraciones pendientes
alembic upgrade head

# Aplicar solo la migración de índices adicionales
alembic upgrade a2b3c4d5e6f7

# Revertir la última migración
alembic downgrade -1

# Revertir a una versión específica
alembic downgrade f1a2b3c4d5e6
```

### Opción 2: Ejecutar SQL Directamente

Para SQLite:
```bash
# Conectar a la base de datos
sqlite3 mancaperros_app.db

# Ejecutar el script SQL
.read migrations/001_add_additional_indexes.sql

# Verificar los índices creados
SELECT name, tbl_name, sql FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%' ORDER BY tbl_name;

# Salir
.quit
```

Para PostgreSQL:
```bash
psql -U usuario -d mancaperros_app -f migrations/001_add_additional_indexes.sql
```

Para MySQL:
```bash
mysql -u usuario -p mancaperros_app < migrations/001_add_additional_indexes.sql
```

## Índices Creados

### Tabla users
- `idx_users_email` - Búsqueda y autenticación por email
- `idx_users_user_name` - Búsqueda por nombre de usuario

### Tabla exercise_plans
- `idx_exercise_plans_user_owner_id` - Planes por usuario propietario
- `idx_exercise_plans_type` - Filtrado por tipo de plan

### Tabla rutines
- `idx_rutines_exercise_plan_id` - Rutinas por plan de ejercicio
- `idx_rutines_plan_group` - Búsqueda compuesta por plan + grupo

### Tabla exercises
- `idx_exercises_rutine_id` - Ejercicios por rutina

### Tabla user_tracker
- `idx_user_tracker_user_id` - Seguimiento por usuario
- `idx_user_tracker_user_type` - Búsqueda compuesta por usuario + tipo

## Verificación de Índices

### SQLite
```sql
-- Ver todos los índices
SELECT name, tbl_name, sql
FROM sqlite_master
WHERE type='index' AND name LIKE 'idx_%'
ORDER BY tbl_name, name;

-- Ver índices de una tabla específica
SELECT name, sql
FROM sqlite_master
WHERE type='index' AND tbl_name='users';
```

### PostgreSQL
```sql
-- Ver todos los índices
SELECT
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE indexname LIKE 'idx_%'
ORDER BY tablename, indexname;
```

### MySQL
```sql
-- Ver índices de una tabla
SHOW INDEX FROM users;

-- Ver todos los índices de la base de datos
SELECT
    TABLE_NAME,
    INDEX_NAME,
    COLUMN_NAME
FROM INFORMATION_SCHEMA.STATISTICS
WHERE TABLE_SCHEMA = 'mancaperros_app'
    AND INDEX_NAME LIKE 'idx_%'
ORDER BY TABLE_NAME, INDEX_NAME;
```

## Análisis de Rendimiento

Después de crear los índices, puedes analizar su impacto:

### SQLite
```sql
-- Habilitar análisis de consultas
EXPLAIN QUERY PLAN SELECT * FROM users WHERE email = 'test@example.com';

-- Analizar estadísticas
ANALYZE;
```

### PostgreSQL
```sql
-- Ver plan de ejecución
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'test@example.com';

-- Actualizar estadísticas
ANALYZE users;
```

### MySQL
```sql
-- Ver plan de ejecución
EXPLAIN SELECT * FROM users WHERE email = 'test@example.com';

-- Actualizar estadísticas
ANALYZE TABLE users;
```

## Rollback (Revertir Cambios)

Si necesitas eliminar los índices:

```sql
-- Eliminar índices adicionales
DROP INDEX IF EXISTS idx_exercise_plans_type;
DROP INDEX IF EXISTS idx_rutines_plan_group;
DROP INDEX IF EXISTS idx_user_tracker_user_type;
```

O usa Alembic:
```bash
alembic downgrade -1
```

## Notas Importantes

1. **Índices Existentes**: La migración `f1a2b3c4d5e6_add_database_indexes.py` ya creó los índices básicos. La nueva migración `a2b3c4d5e6f7_add_additional_database_indexes.py` agrega los índices compuestos adicionales.

2. **Índices Compuestos**: Los índices compuestos (multi-columna) son más eficientes para consultas que filtran por múltiples columnas en orden.

3. **Costo de Escritura**: Los índices mejoran las consultas SELECT pero añaden overhead en INSERT, UPDATE y DELETE. Esto es aceptable para aplicaciones con más lecturas que escrituras.

4. **Mantenimiento**: SQLite mantiene los índices automáticamente. Considera ejecutar `ANALYZE` periódicamente para actualizar las estadísticas del optimizador de consultas.

5. **Espacio en Disco**: Los índices ocupan espacio adicional en disco. Monitorea el tamaño de la base de datos después de crear índices.

## Recursos

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLite Index Documentation](https://www.sqlite.org/lang_createindex.html)
- [PostgreSQL Index Documentation](https://www.postgresql.org/docs/current/indexes.html)
- [MySQL Index Documentation](https://dev.mysql.com/doc/refman/8.0/en/optimization-indexes.html)
