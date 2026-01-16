# Quick index verification script for SQLite (PowerShell)
# Usage: powershell -ExecutionPolicy Bypass -File migrations\check_indexes.ps1

$DB_PATH = "mancaperros_app.db"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Database Index Verification" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Database: $DB_PATH"
Write-Host ""

if (-not (Test-Path $DB_PATH)) {
    Write-Host "Error: Database file not found: $DB_PATH" -ForegroundColor Red
    exit 1
}

# Function to execute SQLite query
function Invoke-SQLite {
    param (
        [string]$Query
    )
    $result = sqlite3 $DB_PATH $Query 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Warning: SQLite command failed. Make sure sqlite3 is in your PATH." -ForegroundColor Yellow
        Write-Host "You can download it from: https://www.sqlite.org/download.html" -ForegroundColor Yellow
        return $null
    }
    return $result
}

# Check if sqlite3 is available
$sqlite3Available = Get-Command sqlite3 -ErrorAction SilentlyContinue
if (-not $sqlite3Available) {
    Write-Host "Error: sqlite3 command not found in PATH" -ForegroundColor Red
    Write-Host "Please install SQLite from: https://www.sqlite.org/download.html" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Alternative: Use Python script instead:" -ForegroundColor Yellow
    Write-Host "  python migrations\apply_migrations.py --verify-only" -ForegroundColor Green
    exit 1
}

Write-Host "All Custom Indexes:" -ForegroundColor Yellow
Write-Host "----------------------------------------"
$indexes = Invoke-SQLite "SELECT name || ' | ' || tbl_name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%' ORDER BY tbl_name, name;"
if ($indexes) {
    $indexes | ForEach-Object { Write-Host $_ }
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Indexes by Table:" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

$tables = @("users", "exercise_plans", "rutines", "exercises", "user_tracker")
foreach ($table in $tables) {
    Write-Host ""
    Write-Host "Table: $table" -ForegroundColor Yellow
    Write-Host "----------------------------------------"
    $tableIndexes = Invoke-SQLite "SELECT '  - ' || name FROM sqlite_master WHERE type='index' AND tbl_name='$table' AND name LIKE 'idx_%' ORDER BY name;"
    if ($tableIndexes) {
        $tableIndexes | ForEach-Object { Write-Host $_ }
    } else {
        Write-Host "  (no indexes)" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Recommended Index Check:" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Function to check if index exists
function Test-Index {
    param (
        [string]$IndexName
    )
    $result = Invoke-SQLite "SELECT COUNT(*) FROM sqlite_master WHERE type='index' AND name='$IndexName';"
    if ($result -eq "1") {
        Write-Host "  ✓ $IndexName" -ForegroundColor Green
        return $true
    } else {
        Write-Host "  ✗ $IndexName (MISSING)" -ForegroundColor Red
        return $false
    }
}

$missingCount = 0

Write-Host ""
Write-Host "Users table:" -ForegroundColor Yellow
if (-not (Test-Index "idx_users_email")) { $missingCount++ }
if (-not (Test-Index "idx_users_user_name")) { $missingCount++ }

Write-Host ""
Write-Host "Exercise Plans table:" -ForegroundColor Yellow
if (-not (Test-Index "idx_exercise_plans_user_owner_id")) { $missingCount++ }
if (-not (Test-Index "idx_exercise_plans_type")) { $missingCount++ }

Write-Host ""
Write-Host "Rutines table:" -ForegroundColor Yellow
if (-not (Test-Index "idx_rutines_exercise_plan_id")) { $missingCount++ }
if (-not (Test-Index "idx_rutines_plan_group")) { $missingCount++ }

Write-Host ""
Write-Host "Exercises table:" -ForegroundColor Yellow
if (-not (Test-Index "idx_exercises_rutine_id")) { $missingCount++ }

Write-Host ""
Write-Host "User Tracker table:" -ForegroundColor Yellow
if (-not (Test-Index "idx_user_tracker_user_id")) { $missingCount++ }
if (-not (Test-Index "idx_user_tracker_user_type")) { $missingCount++ }

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Database Statistics:" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

$indexCount = Invoke-SQLite "SELECT COUNT(*) FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%';"
Write-Host "Total Custom Indexes: $indexCount"

$dbSize = (Get-Item $DB_PATH).Length / 1MB
Write-Host ("Database Size: {0:N2} MB" -f $dbSize)

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan

if ($missingCount -eq 0) {
    Write-Host "✓ All recommended indexes are present!" -ForegroundColor Green
} else {
    Write-Host "⚠ $missingCount recommended index(es) missing!" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To apply missing indexes, run:" -ForegroundColor Yellow
    Write-Host "  alembic upgrade head" -ForegroundColor Green
    Write-Host "Or:" -ForegroundColor Yellow
    Write-Host "  python migrations\apply_migrations.py --file 001_add_additional_indexes.sql" -ForegroundColor Green
}

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Done!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
