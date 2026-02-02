# MED-08: Guía de Implementación (SI se aprueba consolidación)

**Nota:** Este documento es SOLO SI se decide consolidar en futuro.
**Estado:** PREPARACIÓN / NO ACTIVO

---

## 1. ESTRATEGIA RECOMENDADA: Polimorfismo con Discriminador

### 1.1 Enfoque Técnico

```python
# Nueva estructura consolidada

class Exercise_plan(Base):
    """Unificada: personal + global"""
    __tablename__ = "exercise_plans"

    exercise_plan_id = Column(Integer, primary_key=True, index=True)
    exercise_plan_name = Column(String(255), nullable=False, index=True)
    exercise_plan_type = Column(String(255), nullable=False, index=True)
    creation_date = Column(Date, nullable=False, index=True)
    difficult_level = Column(String(255), nullable=False, index=True)
    routine_group_order = Column(JSON, nullable=False)

    # DISCRIMINADOR
    is_global = Column(Boolean, default=False, nullable=False, index=True)

    # ForeignKeys
    user_owner_id = Column(Integer, ForeignKey("users.user_id"), nullable=True)  # NULL si is_global=True
    created_by_user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)  # Siempre presente

    # Relationships
    routines = relationship("Rutine", back_populates="exercise_plan", cascade="all, delete-orphan")
    owner = relationship("User", foreign_keys=[user_owner_id], back_populates="exercise_plans_personal")
    creator = relationship("User", foreign_keys=[created_by_user_id], back_populates="exercise_plans_created")

class Rutine(Base):
    """Unificada: personal + global"""
    __tablename__ = "rutines"

    rutine_id = Column(Integer, primary_key=True, index=True)
    rutine_name = Column(String(255), nullable=False, index=True)
    rutine_type = Column(String(255), nullable=False, index=True)
    rutine_group = Column(String(255), nullable=False, index=True)
    rutine_category = Column(String(255), nullable=False, index=True)
    exercise_plan_id = Column(Integer, ForeignKey("exercise_plans.exercise_plan_id"), nullable=False)
    rounds = Column(Integer, nullable=False, index=True, default=0)
    rst_btw_exercises = Column(String(255), nullable=False, index=True, default="0")
    rst_btw_rounds = Column(String(255), nullable=False, index=True, default="0")
    difficult_level = Column(String(255), nullable=False, index=True)

    # Relationships
    exercise_plan = relationship("Exercise_plan", back_populates="routines")
    exercises = relationship("Exercise", back_populates="routine", cascade="all, delete-orphan")

class Exercise(Base):
    """Unificada: personal + global"""
    __tablename__ = "exercises"

    exercise_id = Column(Integer, primary_key=True, index=True)
    exercise_name = Column(String(255), nullable=False, index=True)
    rep = Column(String(255), nullable=False, index=True, default="empty")
    exercise_type = Column(String(255), nullable=False, index=True)
    exercise_group = Column(String(255), nullable=False, index=True)
    rutine_id = Column(Integer, ForeignKey("rutines.rutine_id"), nullable=False)
    image = Column(String(255), nullable=False, index=True, default="empty")

    # Relationships
    routine = relationship("Rutine", back_populates="exercises")
```

### 1.2 Cambios en User Model

```python
class User(Base):
    """Actualizado para nuevas relaciones"""
    __tablename__ = "users"

    # ... campos existentes ...

    # Nuevas relaciones
    exercise_plans_personal = relationship(
        "Exercise_plan",
        foreign_keys=[Exercise_plan.user_owner_id],
        back_populates="owner",
        cascade="all, delete-orphan"
    )
    exercise_plans_created = relationship(
        "Exercise_plan",
        foreign_keys=[Exercise_plan.created_by_user_id],
        back_populates="creator"
    )
```

---

## 2. MIGRACIÓN DE DATOS

### 2.1 Script de Migración Alembic (Pseudocódigo)

```python
# alembic/versions/XXXXX_consolidate_exercise_tables.py

def upgrade() -> None:
    # PASO 1: Crear tabla nueva unificada
    op.create_table(
        'exercise_plans_new',
        sa.Column('exercise_plan_id', sa.Integer, primary_key=True),
        sa.Column('exercise_plan_name', sa.String(255), nullable=False),
        sa.Column('exercise_plan_type', sa.String(255), nullable=False),
        sa.Column('creation_date', sa.Date, nullable=False),
        sa.Column('difficult_level', sa.String(255), nullable=False),
        sa.Column('routine_group_order', sa.JSON, nullable=False),
        sa.Column('is_global', sa.Boolean, nullable=False, default=False),
        sa.Column('user_owner_id', sa.Integer, sa.ForeignKey('users.user_id'), nullable=True),
        sa.Column('created_by_user_id', sa.Integer, sa.ForeignKey('users.user_id'), nullable=False),
    )

    # PASO 2: Copiar datos personales
    op.execute("""
        INSERT INTO exercise_plans_new
        (exercise_plan_id, exercise_plan_name, exercise_plan_type, creation_date,
         difficult_level, routine_group_order, is_global, user_owner_id, created_by_user_id)
        SELECT exercise_plan_id, exercise_plan_name, exercise_plan_type, creation_date,
               difficult_level, routine_group_order, 0, user_owner_id, user_owner_id
        FROM exercise_plans
    """)

    # PASO 3: Copiar datos globales (renumerar IDs para evitar conflictos)
    op.execute("""
        INSERT INTO exercise_plans_new
        (exercise_plan_id, exercise_plan_name, exercise_plan_type, creation_date,
         difficult_level, routine_group_order, is_global, user_owner_id, created_by_user_id)
        SELECT exercise_plan_id + 1000000, exercise_plan_name, exercise_plan_type, creation_date,
               difficult_level, routine_group_order, 1, NULL, user_creator_id
        FROM exercise_plans_global
    """)

    # PASO 4: Crear tabla rutines_new con referencias actualizadas
    # ... similar ...

    # PASO 5: Crear tabla exercises_new con referencias actualizadas
    # ... similar ...

    # PASO 6: Eliminar tablas viejas
    op.drop_table('exercise_plans_global')
    op.drop_table('exercise_plans')
    op.drop_table('rutines_global')
    op.drop_table('rutines')
    op.drop_table('exercises_global')
    op.drop_table('exercises')

    # PASO 7: Renombrar nuevas tablas
    op.rename_table('exercise_plans_new', 'exercise_plans')
    op.rename_table('rutines_new', 'rutines')
    op.rename_table('exercises_new', 'exercises')

    # PASO 8: Crear índices
    op.create_index('idx_exercise_plans_user_owner', 'exercise_plans', ['user_owner_id'])
    op.create_index('idx_exercise_plans_created_by', 'exercise_plans', ['created_by_user_id'])
    op.create_index('idx_exercise_plans_is_global', 'exercise_plans', ['is_global'])
    op.create_index('idx_exercise_plans_compound', 'exercise_plans', ['is_global', 'user_owner_id'])

def downgrade() -> None:
    # Recrear tablas viejas
    # Copiar datos con conversión reversa
    # Eliminar nuevas tablas
```

### 2.2 Validación Post-Migración

```python
# Script de validación
def validate_migration(db_path):
    """Verificar integridad post-consolidación"""

    # Check 1: Contar registros
    personal_count = db.query(Exercise_plan).filter(Exercise_plan.is_global == False).count()
    global_count = db.query(Exercise_plan).filter(Exercise_plan.is_global == True).count()

    print(f"Personal: {personal_count}, Global: {global_count}")

    # Check 2: Verificar FKs válidas
    orphaned = db.query(Exercise_plan).filter(
        and_(
            Exercise_plan.is_global == True,
            Exercise_plan.user_owner_id != None
        )
    ).all()

    if orphaned:
        print(f"ERROR: {len(orphaned)} registros globales con user_owner_id")

    # Check 3: Verificar cascadas
    for plan in db.query(Exercise_plan).all():
        routine_count = db.query(Rutine).filter(
            Rutine.exercise_plan_id == plan.exercise_plan_id
        ).count()
        print(f"Plan {plan.exercise_plan_id}: {routine_count} rutinas")

    # Check 4: Verificar todos los campos críticos
    assert db.query(Exercise_plan).filter(Exercise_plan.created_by_user_id == None).count() == 0
    print("✓ Validación completada")
```

---

## 3. CAMBIOS EN REPOSITORIOS

### 3.1 ExercisePlanRepository Unificado

```python
class ExercisePlanRepository(BaseRepository[Exercise_plan, ...]):
    """Repositorio unificado para personal y global"""

    def get_personal_by_user(self, user_id: int) -> Exercise_plan | None:
        """Obtener plan personal de usuario"""
        return self.db.query(Exercise_plan).filter(
            Exercise_plan.user_owner_id == user_id,
            Exercise_plan.is_global == False
        ).first()

    def get_all_global(self) -> Sequence[Exercise_plan]:
        """Obtener todos los planes globales"""
        return self.db.query(Exercise_plan).filter(
            Exercise_plan.is_global == True
        ).all()

    def create_from_global(self, global_plan_id: int, user_id: int) -> Exercise_plan:
        """Crear plan personal copiando desde global"""

        # Obtener plan global
        global_plan = self.db.query(Exercise_plan).filter(
            Exercise_plan.exercise_plan_id == global_plan_id,
            Exercise_plan.is_global == True
        ).first()

        if not global_plan:
            raise ValueError("Global plan not found")

        # Crear nuevo plan personal (copia dentro MISMA tabla)
        personal_plan = Exercise_plan(
            exercise_plan_name=global_plan.exercise_plan_name,
            exercise_plan_type=global_plan.exercise_plan_type,
            creation_date=datetime.now().date(),
            difficult_level=global_plan.difficult_level,
            routine_group_order=global_plan.routine_group_order,
            is_global=False,  # Marcado como personal
            user_owner_id=user_id,  # Asignado a usuario
            created_by_user_id=user_id  # Copiado por usuario
        )

        self.db.add(personal_plan)
        self.db.flush()

        # Copiar rutinas y ejercicios
        for routine_global in global_plan.routines:
            routine_personal = Rutine(
                rutine_name=routine_global.rutine_name,
                # ... copiar otros campos ...
                exercise_plan_id=personal_plan.exercise_plan_id
            )
            self.db.add(routine_personal)
            self.db.flush()

            # Copiar ejercicios
            for exercise_global in routine_global.exercises:
                exercise_personal = Exercise(
                    # ... copiar campos ...
                    rutine_id=routine_personal.rutine_id
                )
                self.db.add(exercise_personal)

        self.db.commit()
        return personal_plan

    def search_by_type(self, plan_type: str, is_global: bool = False) -> Sequence[Exercise_plan]:
        """Buscar planes por tipo, especificando si personal o global"""
        return self.db.query(Exercise_plan).filter(
            Exercise_plan.exercise_plan_type == plan_type,
            Exercise_plan.is_global == is_global
        ).all()
```

### 3.2 Eliminar repositorios dualizados

```
ELIMINAR:
├── exercise_plan_global_repository.py
├── routine_global_repository.py
└── exercise_global_repository.py

MANTENER:
├── exercise_plan_repository.py (ahora unificado)
├── routine_repository.py (ahora unificado)
└── exercise_repository.py (ahora unificado)
```

---

## 4. CAMBIOS EN ENDPOINTS

### 4.1 Unificar endpoints

**ANTES:**
```
POST /exercise_plans              → Crear plan personal
GET /exercise_plans              → Listar planes personales
POST /exercise_plans_global      → Crear plan global
GET /exercise_plans_global       → Listar planes globales
POST /exercise_plans/copy/{id}   → Copiar global a personal
```

**DESPUÉS:**
```
POST /exercise_plans             → Crear plan (tipo query param)
GET /exercise_plans              → Listar planes (tipo query param)
GET /exercise_plans/global       → Listar globales (filtro booleano)
POST /exercise_plans/{id}/copy   → Copiar global a personal

Ejemplos:
GET /exercise_plans?is_global=false     → Planes personales
GET /exercise_plans?is_global=true      → Planes globales
GET /exercise_plans?type=full_body      → Todos tipo full_body
GET /exercise_plans?type=full_body&is_global=true → Solo globales full_body
```

### 4.2 Ejemplo de endpoint unificado

```python
@router.get("/exercise_plans", response_model=List[ExercisePlanResponse])
async def list_exercise_plans(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    is_global: bool = Query(False),
    plan_type: str = Query(None),
    skip: int = Query(0),
    limit: int = Query(100),
):
    """
    Listar planes de ejercicio.

    Query params:
    - is_global: True para globales, False para personales (default)
    - plan_type: Filtrar por tipo (opcional)
    """

    repository = ExercisePlanRepository(db)

    # Construir query base según tipo
    query = db.query(Exercise_plan)

    if is_global:
        # Planes globales - acceso público
        query = query.filter(Exercise_plan.is_global == True)
    else:
        # Planes personales - solo usuario actual
        query = query.filter(
            Exercise_plan.is_global == False,
            Exercise_plan.user_owner_id == current_user.user_id
        )

    # Filtro opcional por tipo
    if plan_type:
        query = query.filter(Exercise_plan.exercise_plan_type == plan_type)

    # Paginación
    plans = query.offset(skip).limit(limit).all()
    return plans
```

---

## 5. CAMBIOS EN SCHEMAS

### 5.1 Schemas unificados

```python
# ANTES: 6 schemas diferentes
class Exercise_plan_Base(BaseModel):
    exercise_plan_name: str
    exercise_plan_type: str
    difficult_level: str

class Exercise_plan_global_Base(BaseModel):
    exercise_plan_name: str
    exercise_plan_type: str
    difficult_level: str

# DESPUÉS: 1 schema con discriminador
class Exercise_planBase(BaseModel):
    exercise_plan_name: str
    exercise_plan_type: str
    difficult_level: str
    is_global: bool = False
    routine_group_order: dict = Field(default=settings.ROUTINE_GROUP_ORDER_DEFAULT)

class ExercisePlanCreate(ExercisePlanBase):
    """Para crear planes (personal o global según is_global)"""
    pass

class ExercisePlanResponse(ExercisePlanBase):
    exercise_plan_id: int
    creation_date: date
    user_owner_id: int | None
    created_by_user_id: int

    model_config = ConfigDict(from_attributes=True)
```

### 5.2 Eliminar schemas duplicados

```
ELIMINAR DE schemas.py:
- Exercise_global_Base
- Exercise_global_Create
- Exercise_global
- Rutine_global_Base
- Rutine_global_Create
- Rutine_global
- Exercise_plan_global_Base
- Exercise_plan_global_Create
- Exercise_plan_global
- Exercise_plan_global_Response
- Exercise_plan_global_info
```

---

## 6. PLAN DE IMPLEMENTACIÓN DETALLADO

### Fase 1: Preparación (2-3 horas)
- [ ] Crear rama `feature/med-08-consolidation`
- [ ] Backup completo de BD
- [ ] Documentar queries existentes que serán afectadas
- [ ] Crear suite de tests pre-consolidación (validar datos)

### Fase 2: Modelos (4-6 horas)
- [ ] Actualizar Exercise_plan model
- [ ] Actualizar Rutine model
- [ ] Actualizar Exercise model
- [ ] Actualizar User model (relaciones)
- [ ] Crear migrations de Alembic
- [ ] Tests unitarios de modelos

### Fase 3: Repositorios (6-8 horas)
- [ ] Consolidar ExercisePlanRepository
- [ ] Consolidar RoutineRepository
- [ ] Consolidar ExerciseRepository
- [ ] Eliminar *_global_repository.py
- [ ] Tests de repositorios

### Fase 4: Schemas (3-4 horas)
- [ ] Crear schemas unificados
- [ ] Remover schemas *_global
- [ ] Tests de validación de schemas

### Fase 5: Endpoints (2-3 horas)
- [ ] Actualizar endpoints en exercises.py
- [ ] Actualizar endpoints en routines.py
- [ ] Integración con repositorios unificados

### Fase 6: Tests (6-8 horas)
- [ ] Tests unitarios de modelos
- [ ] Tests de repositorios
- [ ] Tests de endpoints (integración)
- [ ] Verificar 133/133 tests todavía pasan
- [ ] Tests de migración de datos

### Fase 7: Validación (3-5 horas)
- [ ] Ejecutar script de validación post-migración
- [ ] Verificar integridad referencial
- [ ] Performance testing (tablas consolidadas)
- [ ] Verificar cascadas de eliminación

### Fase 8: Documentación (1-2 horas)
- [ ] Actualizar README.md
- [ ] Actualizar REFACTORING_PROGRESS.md
- [ ] Documentar cambios en API
- [ ] Changelog

### Fase 9: Rollback (2-3 horas)
- [ ] Crear rama downgrade con script reverso
- [ ] Probar downgrade en BD de test

**TOTAL:** 30-42 horas

---

## 7. CRITERIOS DE ÉXITO

```
✓ Todos 133 tests pasan (100%)
✓ Integridad referencial validada (0 referencias rotas)
✓ Migración reversible (downgrade funciona)
✓ Rendimiento: queries no más lentas (benchmark)
✓ API backward compatible (versioning implementado)
✓ Documentación actualizada
✓ Cobertura de tests >= 95%
✓ Performance no degradada (índices optimizados)
```

---

## 8. ROLLBACK PLAN

Si algo sale mal:

```bash
# 1. Detener aplicación
systemctl stop mancaperros_app

# 2. Backup de BD corrupta
cp mancaperros_app.db mancaperros_app.db.corrupted

# 3. Restaurar desde backup pre-consolidación
cp backups/mancaperros_app.db.2026-01-20.backup mancaperros_app.db

# 4. Ejecutar downgrade
alembic downgrade -1

# 5. Reiniciar
systemctl start mancaperros_app

# 6. Verificar
curl http://localhost:8000/health
```

---

## 9. CONSIDERACIONES DE SEGURIDAD

### 9.1 Cambios en Access Control

```python
# ANTES: Claro quién accede qué
def get_global_plans():
    return Exercise_plan_global.query.all()  # Públicos

def get_personal_plans(user_id):
    return Exercise_plan.query.filter(user_owner_id=user_id)  # Solo usuario

# DESPUÉS: Necesita ser más cuidadoso
def get_plans(is_global, user_id=None):
    query = Exercise_plan.query.filter(is_global=is_global)
    if not is_global:
        query = query.filter(user_owner_id=user_id)  # ← CRÍTICO no olvidar
    return query.all()
```

### 9.2 Tests de Seguridad

```python
def test_user_cannot_access_other_users_plans():
    """Usuario 1 no puede ver planes personales de Usuario 2"""
    user1_plans = ExercisePlanRepository(db).get_personal_by_user(user_id=1)
    user2_plans = ExercisePlanRepository(db).get_personal_by_user(user_id=2)

    # Verificar que son diferentes
    assert user1_plans.exercise_plan_id != user2_plans.exercise_plan_id

def test_anyone_can_access_global_plans():
    """Cualquier usuario puede acceder planes globales"""
    plans = ExercisePlanRepository(db).get_all_global()
    assert len(plans) > 0
```

---

## 10. ÍNDICES RECOMENDADOS POST-CONSOLIDACIÓN

```sql
-- Muy críticos
CREATE INDEX idx_exercise_plans_user_owner_id ON exercise_plans(user_owner_id);
CREATE INDEX idx_exercise_plans_is_global ON exercise_plans(is_global);
CREATE INDEX idx_exercise_plans_compound ON exercise_plans(is_global, user_owner_id);
CREATE INDEX idx_exercise_plans_created_by ON exercise_plans(created_by_user_id);

-- Soporte a queries comunes
CREATE INDEX idx_exercise_plans_type_global ON exercise_plans(exercise_plan_type, is_global);
CREATE INDEX idx_exercise_plans_difficulty_global ON exercise_plans(difficult_level, is_global);

-- Para rutines y exercises
CREATE INDEX idx_rutines_exercise_plan_id ON rutines(exercise_plan_id);
CREATE INDEX idx_exercises_rutine_id ON exercises(rutine_id);
```

---

**Documento preparado por: Database Architect - 2026-01-16**
**Activar cuando se apruebe consolidación**
