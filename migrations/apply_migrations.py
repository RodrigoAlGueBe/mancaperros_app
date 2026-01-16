#!/usr/bin/env python3
"""
Database Migration Script - Apply SQL Migrations

This script helps apply SQL migrations to the database when Alembic is not available
or when you prefer to use raw SQL.

Usage:
    python migrations/apply_migrations.py --file 001_add_additional_indexes.sql
    python migrations/apply_migrations.py --file 000_all_indexes_complete.sql --verify
    python migrations/apply_migrations.py --verify-only
"""

import argparse
import os
import sys
import sqlite3
from pathlib import Path
from typing import Optional


class MigrationManager:
    """Manages database migrations for SQLite"""

    def __init__(self, db_path: str = "mancaperros_app.db"):
        """
        Initialize migration manager

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.migrations_dir = Path(__file__).parent

    def connect(self) -> sqlite3.Connection:
        """Create database connection"""
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Database not found: {self.db_path}")

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def apply_migration(self, sql_file: str, dry_run: bool = False) -> bool:
        """
        Apply SQL migration from file

        Args:
            sql_file: Name of SQL file in migrations directory
            dry_run: If True, only print SQL without executing

        Returns:
            True if successful, False otherwise
        """
        migration_path = self.migrations_dir / sql_file

        if not migration_path.exists():
            print(f"Error: Migration file not found: {migration_path}")
            return False

        print(f"Reading migration: {sql_file}")

        with open(migration_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        # Split SQL into individual statements
        statements = [
            stmt.strip()
            for stmt in sql_content.split(';')
            if stmt.strip() and not stmt.strip().startswith('--')
        ]

        print(f"Found {len(statements)} SQL statements")

        if dry_run:
            print("\nDRY RUN - SQL to be executed:")
            print("=" * 80)
            for i, stmt in enumerate(statements, 1):
                print(f"\n-- Statement {i}:")
                print(stmt)
            print("=" * 80)
            return True

        # Execute migration
        try:
            conn = self.connect()
            cursor = conn.cursor()

            print(f"\nApplying migration to: {self.db_path}")

            for i, stmt in enumerate(statements, 1):
                # Skip comments and empty statements
                if stmt.startswith('--') or not stmt.strip():
                    continue

                print(f"  Executing statement {i}/{len(statements)}...")
                cursor.execute(stmt)

            conn.commit()
            print(f"\nMigration completed successfully!")
            print(f"Applied {len(statements)} statements")

            conn.close()
            return True

        except sqlite3.Error as e:
            print(f"\nError applying migration: {e}")
            if 'conn' in locals():
                conn.rollback()
                conn.close()
            return False

    def verify_indexes(self) -> None:
        """Verify all indexes exist in the database"""
        try:
            conn = self.connect()
            cursor = conn.cursor()

            print("\nVerifying database indexes:")
            print("=" * 80)

            # Query all custom indexes
            cursor.execute("""
                SELECT
                    name as index_name,
                    tbl_name as table_name,
                    sql as definition
                FROM sqlite_master
                WHERE type = 'index'
                  AND name LIKE 'idx_%'
                ORDER BY tbl_name, name
            """)

            indexes = cursor.fetchall()

            if not indexes:
                print("No custom indexes found in database!")
                conn.close()
                return

            print(f"Found {len(indexes)} custom indexes:\n")

            current_table = None
            for row in indexes:
                if current_table != row['table_name']:
                    current_table = row['table_name']
                    print(f"\nTable: {current_table}")
                    print("-" * 80)

                print(f"  - {row['index_name']}")

            print("\n" + "=" * 80)

            # Check for recommended indexes
            recommended_indexes = {
                'users': ['idx_users_email', 'idx_users_user_name'],
                'exercise_plans': ['idx_exercise_plans_user_owner_id', 'idx_exercise_plans_type'],
                'rutines': ['idx_rutines_exercise_plan_id', 'idx_rutines_plan_group'],
                'exercises': ['idx_exercises_rutine_id'],
                'user_tracker': ['idx_user_tracker_user_id', 'idx_user_tracker_user_type']
            }

            existing_indexes = {row['index_name'] for row in indexes}
            missing_indexes = []

            print("\nRecommended Index Status:")
            print("=" * 80)

            for table, indexes_list in recommended_indexes.items():
                print(f"\nTable: {table}")
                for idx in indexes_list:
                    status = "OK" if idx in existing_indexes else "MISSING"
                    symbol = "✓" if idx in existing_indexes else "✗"
                    print(f"  {symbol} {idx:45s} [{status}]")
                    if idx not in existing_indexes:
                        missing_indexes.append(idx)

            if missing_indexes:
                print("\n" + "=" * 80)
                print(f"WARNING: {len(missing_indexes)} recommended indexes are missing!")
                print("Missing indexes:")
                for idx in missing_indexes:
                    print(f"  - {idx}")
                print("\nRun the migration to create missing indexes:")
                print("  python migrations/apply_migrations.py --file 001_add_additional_indexes.sql")
            else:
                print("\n" + "=" * 80)
                print("All recommended indexes are present!")

            conn.close()

        except sqlite3.Error as e:
            print(f"Error verifying indexes: {e}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Apply SQL migrations to the database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Apply additional indexes migration
  python migrations/apply_migrations.py --file 001_add_additional_indexes.sql

  # Dry run to see what will be executed
  python migrations/apply_migrations.py --file 001_add_additional_indexes.sql --dry-run

  # Verify all indexes
  python migrations/apply_migrations.py --verify-only

  # Apply migration and verify
  python migrations/apply_migrations.py --file 001_add_additional_indexes.sql --verify
        """
    )

    parser.add_argument(
        '--file',
        help='SQL migration file to apply (relative to migrations directory)'
    )

    parser.add_argument(
        '--db',
        default='mancaperros_app.db',
        help='Path to SQLite database (default: mancaperros_app.db)'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show SQL without executing'
    )

    parser.add_argument(
        '--verify',
        action='store_true',
        help='Verify indexes after applying migration'
    )

    parser.add_argument(
        '--verify-only',
        action='store_true',
        help='Only verify indexes, do not apply migration'
    )

    args = parser.parse_args()

    # Validate arguments
    if not args.verify_only and not args.file:
        parser.error("Either --file or --verify-only must be specified")

    # Initialize migration manager
    manager = MigrationManager(db_path=args.db)

    # Verify only mode
    if args.verify_only:
        manager.verify_indexes()
        return 0

    # Apply migration
    success = manager.apply_migration(args.file, dry_run=args.dry_run)

    if not success:
        return 1

    # Verify if requested
    if args.verify and not args.dry_run:
        manager.verify_indexes()

    return 0


if __name__ == '__main__':
    sys.exit(main())
