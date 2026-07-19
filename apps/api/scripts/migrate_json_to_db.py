import argparse
import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.db import SessionLocal, init_db
from app.services.migration_service import JsonMigrationService


def main() -> None:
    parser = argparse.ArgumentParser(description="Migrate GrowthOS JSON data into the database.")
    parser.add_argument("--workspace-id", required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    init_db()
    with SessionLocal() as db:
        result = JsonMigrationService(db, args.workspace_id).migrate(dry_run=args.dry_run)
        print(json.dumps(result.__dict__, indent=2))


if __name__ == "__main__":
    main()
