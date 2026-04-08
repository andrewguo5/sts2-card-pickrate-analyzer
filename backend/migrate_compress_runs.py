#!/usr/bin/env python3
"""
Migration script to compress existing run data.

This script:
1. Connects to the database
2. Fetches all runs
3. Converts raw_data from JSONB to compressed LargeBinary
4. Updates each run with compressed data

Run this AFTER changing the model but BEFORE deploying new code.
"""
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from compression import compress_run_data, is_compressed
from config import settings
import json


def migrate_runs():
    """Migrate all existing runs to use compression."""

    # Connect to database
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        print("=" * 70)
        print("RUN DATA COMPRESSION MIGRATION")
        print("=" * 70)
        print(f"Database: {settings.database_url.split('@')[-1]}")
        print()

        # First, alter the column type
        print("[1/4] Altering table schema...")
        print("  Changing raw_data from JSONB to bytea...")

        # Check if column is already bytea
        result = db.execute(text("""
            SELECT data_type
            FROM information_schema.columns
            WHERE table_name = 'runs' AND column_name = 'raw_data'
        """)).fetchone()

        current_type = result[0] if result else None
        print(f"  Current type: {current_type}")

        if current_type == 'jsonb':
            print("  Converting JSONB column to bytea...")
            # We can't directly ALTER COLUMN from jsonb to bytea, so we need to:
            # 1. Add new column
            # 2. Migrate data
            # 3. Drop old column
            # 4. Rename new column

            db.execute(text("ALTER TABLE runs ADD COLUMN IF NOT EXISTS raw_data_new bytea"))
            db.commit()
            print("  ✓ Added temporary column")
        elif current_type == 'bytea':
            print("  ✓ Column already bytea, skipping schema change")
        else:
            print(f"  ✗ Unexpected column type: {current_type}")
            return

        # Get all runs
        print("\n[2/4] Fetching runs...")
        if current_type == 'jsonb':
            result = db.execute(text("SELECT id, raw_data FROM runs"))
        else:
            result = db.execute(text("SELECT id, raw_data_new as raw_data FROM runs WHERE raw_data_new IS NOT NULL"))

        runs = result.fetchall()
        print(f"  Found {len(runs)} runs")

        if not runs:
            # Check if data is already in new column
            result = db.execute(text("SELECT id FROM runs WHERE raw_data_new IS NOT NULL LIMIT 1"))
            if result.fetchone():
                print("  ✓ Data already migrated to new column")
                runs = db.execute(text("SELECT id, raw_data_new as raw_data FROM runs")).fetchall()
            else:
                print("  No runs to migrate")
                return

        # Compress and update each run
        print("\n[3/4] Compressing and updating runs...")
        total_original = 0
        total_compressed = 0
        migrated = 0
        already_compressed = 0
        errors = 0

        for i, (run_id, raw_data) in enumerate(runs, 1):
            try:
                # Check if already compressed
                if isinstance(raw_data, bytes):
                    if is_compressed(raw_data):
                        already_compressed += 1
                        if i % 10 == 0:
                            print(f"  [{i}/{len(runs)}] Run {run_id}: already compressed, skipping")
                        continue
                    # It's bytes but not compressed - try to decompress as JSON string
                    try:
                        run_data = json.loads(raw_data.decode('utf-8'))
                    except:
                        print(f"  [{i}/{len(runs)}] ✗ Run {run_id}: corrupted data")
                        errors += 1
                        continue
                else:
                    # It's JSONB dict
                    run_data = raw_data

                # Compress the data
                compressed = compress_run_data(run_data)

                original_size = len(json.dumps(run_data).encode('utf-8'))
                compressed_size = len(compressed)

                total_original += original_size
                total_compressed += compressed_size

                # Update the run
                if current_type == 'jsonb':
                    db.execute(
                        text("UPDATE runs SET raw_data_new = :compressed WHERE id = :id"),
                        {"compressed": compressed, "id": run_id}
                    )
                else:
                    db.execute(
                        text("UPDATE runs SET raw_data = :compressed WHERE id = :id"),
                        {"compressed": compressed, "id": run_id}
                    )

                migrated += 1

                if i % 10 == 0 or i == len(runs):
                    ratio = (1 - compressed_size / original_size) * 100
                    print(f"  [{i}/{len(runs)}] Run {run_id}: {original_size} → {compressed_size} bytes ({ratio:.1f}% reduction)")

            except Exception as e:
                print(f"  [{i}/{len(runs)}] ✗ Run {run_id}: {e}")
                errors += 1

        db.commit()

        # Finalize schema change
        if current_type == 'jsonb' and migrated > 0:
            print("\n[4/4] Finalizing schema change...")
            print("  Dropping old column...")
            db.execute(text("ALTER TABLE runs DROP COLUMN raw_data"))
            print("  Renaming new column...")
            db.execute(text("ALTER TABLE runs RENAME COLUMN raw_data_new TO raw_data"))
            db.commit()
            print("  ✓ Schema migration complete")
        else:
            print("\n[4/4] Schema already finalized")

        # Print summary
        print("\n" + "=" * 70)
        print("MIGRATION COMPLETE")
        print("=" * 70)
        print(f"Total runs:           {len(runs)}")
        print(f"Migrated:             {migrated}")
        print(f"Already compressed:   {already_compressed}")
        print(f"Errors:               {errors}")

        if migrated > 0:
            avg_reduction = (1 - total_compressed / total_original) * 100
            print(f"\nOriginal size:        {total_original:,} bytes ({total_original/1024/1024:.2f} MB)")
            print(f"Compressed size:      {total_compressed:,} bytes ({total_compressed/1024/1024:.2f} MB)")
            print(f"Savings:              {total_original - total_compressed:,} bytes ({(total_original - total_compressed)/1024/1024:.2f} MB)")
            print(f"Average reduction:    {avg_reduction:.1f}%")
        print("=" * 70)

    except Exception as e:
        print(f"\n✗ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    print("\n⚠️  WARNING: This will modify the database schema and all run data!")
    print("Make sure you have a backup before proceeding.\n")

    response = input("Type 'MIGRATE' to continue: ").strip()
    if response != "MIGRATE":
        print("Migration cancelled")
        sys.exit(0)

    migrate_runs()
