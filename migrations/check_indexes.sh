#!/bin/bash
# Quick index verification script for SQLite
# Usage: bash migrations/check_indexes.sh

DB_PATH="mancaperros_app.db"

echo "=========================================="
echo "Database Index Verification"
echo "=========================================="
echo "Database: $DB_PATH"
echo ""

if [ ! -f "$DB_PATH" ]; then
    echo "Error: Database file not found: $DB_PATH"
    exit 1
fi

echo "All Custom Indexes:"
echo "----------------------------------------"
sqlite3 "$DB_PATH" <<EOF
SELECT
    printf('%-35s | %-20s', name, tbl_name) as "Index Name | Table"
FROM sqlite_master
WHERE type='index' AND name LIKE 'idx_%'
ORDER BY tbl_name, name;
EOF

echo ""
echo "=========================================="
echo "Indexes by Table:"
echo "=========================================="

for table in users exercise_plans rutines exercises user_tracker; do
    echo ""
    echo "Table: $table"
    echo "----------------------------------------"
    sqlite3 "$DB_PATH" <<EOF
SELECT '  - ' || name
FROM sqlite_master
WHERE type='index' AND tbl_name='$table' AND name LIKE 'idx_%'
ORDER BY name;
EOF
done

echo ""
echo "=========================================="
echo "Recommended Index Check:"
echo "=========================================="

# Check each recommended index
check_index() {
    local idx_name=$1
    local result=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM sqlite_master WHERE type='index' AND name='$idx_name';")
    if [ "$result" -eq 1 ]; then
        echo "  ✓ $idx_name"
    else
        echo "  ✗ $idx_name (MISSING)"
    fi
}

echo ""
echo "Users table:"
check_index "idx_users_email"
check_index "idx_users_user_name"

echo ""
echo "Exercise Plans table:"
check_index "idx_exercise_plans_user_owner_id"
check_index "idx_exercise_plans_type"

echo ""
echo "Rutines table:"
check_index "idx_rutines_exercise_plan_id"
check_index "idx_rutines_plan_group"

echo ""
echo "Exercises table:"
check_index "idx_exercises_rutine_id"

echo ""
echo "User Tracker table:"
check_index "idx_user_tracker_user_id"
check_index "idx_user_tracker_user_type"

echo ""
echo "=========================================="
echo "Database Statistics:"
echo "=========================================="
sqlite3 "$DB_PATH" <<EOF
SELECT
    'Total Indexes: ' || COUNT(*) as stat
FROM sqlite_master
WHERE type='index' AND name LIKE 'idx_%'
UNION ALL
SELECT
    'Database Size: ' || CAST((page_count * page_size / 1024.0 / 1024.0) AS TEXT) || ' MB'
FROM pragma_page_count(), pragma_page_size();
EOF

echo ""
echo "=========================================="
echo "Done!"
echo "=========================================="
