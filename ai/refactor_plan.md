FASE 1: Seguridad (Crítico)

- Crear authService.js con persistencia de token en localStorage
- Crear instancia axios con interceptor para 401 y auto-adjuntar token
- Reemplazar contentEditable por inputs controlados en Routine.jsx

FASE 2: Estado Global

- Crear AuthContext con user, token, login, logout
- Implementar ProtectedRoute para rutas autenticadas
- Migrar 7 componentes de props drilling a useAuth()

FASE 3: Servicios API

- Crear userService.js, routineService.js, exercisePlanService.js
- Centralizar manejo de errores en handleApiError.js
- Reemplazar 10 llamadas axios directas por servicios

FASE 4: Componentes

- Unificar 2 Modal.jsx en BaseModal + variantes específicas
- Cambiar key={index} por IDs únicos (Modal.jsx:177)
- Extraer botones duplicados a ActionButton.jsx

FASE 5: Estilos

- Crear theme.js con tokens de color y spacing
- Definir breakpoints: 480px, 768px, 1024px
- Migrar 4 archivos CSS a styled-components

Tests: Cada fase incluye tests unitarios/snapshot sugeridos.