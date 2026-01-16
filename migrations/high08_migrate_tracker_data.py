"""
HIGH-08: Data migration script for User_Tracker to WorkoutEvent.

This script migrates existing data from the legacy users_tracker table
to the new workout_events table with proper polymorphic event types.

Usage:
    python -m migrations.high08_migrate_tracker_data [--dry-run] [--batch-size=1000]

Options:
    --dry-run       Print migration plan without executing
    --batch-size    Number of records to process per batch (default: 1000)
    --verify-only   Only run verification queries, no migration

Prerequisites:
    1. The workout_events table must exist (run Alembic migration first)
    2. The database connection must be configured
"""

import argparse
import sys
from datetime import datetime, timezone
from typing import Generator

from sqlalchemy.orm import Session
from sqlalchemy import text

# Add parent directory to path for imports
sys.path.insert(0, '.')

from infrastructure.database.session import SessionLocal
from infrastructure.database.models import (
    User_Tracker,
    WorkoutEvent,
    RoutineCompletedEvent,
    ExercisePlanStartedEvent,
    ExercisePlanCompletedEvent,
)


def get_legacy_records_batch(
    db: Session,
    info_type: str,
    offset: int = 0,
    limit: int = 1000
) -> list[User_Tracker]:
    """Fetch a batch of legacy tracker records."""
    return db.query(User_Tracker).filter(
        User_Tracker.info_type == info_type
    ).offset(offset).limit(limit).all()


def count_legacy_records(db: Session, info_type: str) -> int:
    """Count total legacy records of a specific type."""
    return db.query(User_Tracker).filter(
        User_Tracker.info_type == info_type
    ).count()


def count_new_records(db: Session, event_type: str) -> int:
    """Count total new records of a specific event type."""
    return db.query(WorkoutEvent).filter(
        WorkoutEvent.event_type == event_type
    ).count()


def migrate_routine_completions(
    db: Session,
    batch_size: int = 1000,
    dry_run: bool = False
) -> int:
    """Migrate rutine_end records to RoutineCompletedEvent."""
    total_migrated = 0
    offset = 0

    while True:
        records = get_legacy_records_batch(db, "rutine_end", offset, batch_size)
        if not records:
            break

        if dry_run:
            print(f"  [DRY RUN] Would migrate {len(records)} routine completions")
            total_migrated += len(records)
            offset += batch_size
            continue

        for record in records:
            event = RoutineCompletedEvent(
                user_id=record.user_id,
                timestamp=record.record_datetime,
                routine_group=record.info_description,
                exercise_increments=record.exercise_increments,
                push_increment=record.push_increment or 0,
                pull_increment=record.pull_increment or 0,
                isometric_increment=record.isometric_increment or 0,
                push_time_increment=record.push_time_increment or 0,
                pull_time_increment=record.pull_time_increment or 0,
                isometric_time_increment=record.isometric_time_increment or 0,
            )
            db.add(event)

        db.commit()
        total_migrated += len(records)
        print(f"  Migrated batch: {len(records)} records (total: {total_migrated})")
        offset += batch_size

    return total_migrated


def migrate_exercise_plan_starts(
    db: Session,
    batch_size: int = 1000,
    dry_run: bool = False
) -> int:
    """Migrate exercise_plan_start records to ExercisePlanStartedEvent."""
    total_migrated = 0
    offset = 0

    while True:
        records = get_legacy_records_batch(db, "exercise_plan_start", offset, batch_size)
        if not records:
            break

        if dry_run:
            print(f"  [DRY RUN] Would migrate {len(records)} exercise plan starts")
            total_migrated += len(records)
            offset += batch_size
            continue

        for record in records:
            # Parse exercise_plan_id from info_description
            exercise_plan_id = None
            if record.info_description and record.info_description != "Non_specifed":
                try:
                    exercise_plan_id = int(record.info_description)
                except ValueError:
                    print(f"  Warning: Could not parse exercise_plan_id from '{record.info_description}'")
                    continue

            event = ExercisePlanStartedEvent(
                user_id=record.user_id,
                timestamp=record.record_datetime,
                exercise_plan_id=exercise_plan_id,
            )
            db.add(event)

        db.commit()
        total_migrated += len(records)
        print(f"  Migrated batch: {len(records)} records (total: {total_migrated})")
        offset += batch_size

    return total_migrated


def migrate_exercise_plan_ends(
    db: Session,
    batch_size: int = 1000,
    dry_run: bool = False
) -> int:
    """Migrate exercise_plan_end records to ExercisePlanCompletedEvent."""
    total_migrated = 0
    offset = 0

    while True:
        records = get_legacy_records_batch(db, "exercise_plan_end", offset, batch_size)
        if not records:
            break

        if dry_run:
            print(f"  [DRY RUN] Would migrate {len(records)} exercise plan completions")
            total_migrated += len(records)
            offset += batch_size
            continue

        for record in records:
            # Parse exercise_plan_id from info_description
            exercise_plan_id = None
            if record.info_description and record.info_description != "Non_specifed":
                try:
                    exercise_plan_id = int(record.info_description)
                except ValueError:
                    print(f"  Warning: Could not parse exercise_plan_id from '{record.info_description}'")
                    continue

            event = ExercisePlanCompletedEvent(
                user_id=record.user_id,
                timestamp=record.record_datetime,
                exercise_plan_id=exercise_plan_id,
            )
            db.add(event)

        db.commit()
        total_migrated += len(records)
        print(f"  Migrated batch: {len(records)} records (total: {total_migrated})")
        offset += batch_size

    return total_migrated


def verify_migration(db: Session) -> dict:
    """Verify migration by comparing record counts."""
    results = {
        "routine_completions": {
            "legacy": count_legacy_records(db, "rutine_end"),
            "new": count_new_records(db, "routine_completed"),
        },
        "exercise_plan_starts": {
            "legacy": count_legacy_records(db, "exercise_plan_start"),
            "new": count_new_records(db, "exercise_plan_started"),
        },
        "exercise_plan_ends": {
            "legacy": count_legacy_records(db, "exercise_plan_end"),
            "new": count_new_records(db, "exercise_plan_completed"),
        },
    }
    return results


def print_verification(results: dict) -> None:
    """Print verification results in a formatted table."""
    print("\n" + "=" * 60)
    print("Migration Verification Results")
    print("=" * 60)
    print(f"{'Event Type':<30} {'Legacy':<10} {'New':<10} {'Match'}")
    print("-" * 60)

    all_match = True
    for event_type, counts in results.items():
        match = counts["legacy"] == counts["new"]
        match_str = "OK" if match else "MISMATCH"
        if not match:
            all_match = False
        print(f"{event_type:<30} {counts['legacy']:<10} {counts['new']:<10} {match_str}")

    print("-" * 60)
    if all_match:
        print("All record counts match - migration successful!")
    else:
        print("WARNING: Some record counts do not match!")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Migrate User_Tracker data to WorkoutEvent"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print migration plan without executing"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=1000,
        help="Number of records to process per batch"
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Only run verification queries"
    )
    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("HIGH-08: User_Tracker to WorkoutEvent Migration")
    print(f"Started at: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 60)

    if args.dry_run:
        print("\n*** DRY RUN MODE - No changes will be made ***\n")

    db = SessionLocal()
    try:
        if args.verify_only:
            print("\nRunning verification only...")
            results = verify_migration(db)
            print_verification(results)
            return

        # Pre-migration verification
        print("\nPre-migration record counts:")
        results = verify_migration(db)
        print_verification(results)

        # Check if already migrated
        total_new = sum(r["new"] for r in results.values())
        if total_new > 0 and not args.dry_run:
            print("\nWARNING: workout_events table already contains data!")
            response = input("Continue anyway? (y/N): ")
            if response.lower() != 'y':
                print("Migration cancelled.")
                return

        # Run migrations
        print("\n" + "-" * 60)
        print("Migrating routine completions (rutine_end -> routine_completed)...")
        routine_count = migrate_routine_completions(db, args.batch_size, args.dry_run)
        print(f"Completed: {routine_count} records")

        print("\n" + "-" * 60)
        print("Migrating exercise plan starts...")
        start_count = migrate_exercise_plan_starts(db, args.batch_size, args.dry_run)
        print(f"Completed: {start_count} records")

        print("\n" + "-" * 60)
        print("Migrating exercise plan completions...")
        end_count = migrate_exercise_plan_ends(db, args.batch_size, args.dry_run)
        print(f"Completed: {end_count} records")

        # Post-migration verification
        if not args.dry_run:
            print("\nPost-migration verification:")
            results = verify_migration(db)
            print_verification(results)

        # Summary
        print("\n" + "=" * 60)
        print("Migration Summary")
        print("=" * 60)
        print(f"Routine completions migrated: {routine_count}")
        print(f"Exercise plan starts migrated: {start_count}")
        print(f"Exercise plan completions migrated: {end_count}")
        print(f"Total records migrated: {routine_count + start_count + end_count}")
        print("=" * 60)

    finally:
        db.close()


if __name__ == "__main__":
    main()
