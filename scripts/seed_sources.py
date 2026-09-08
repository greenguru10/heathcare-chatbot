import sys
from pathlib import Path
import yaml

# Add root directory to sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from backend.app.database.session import SessionLocal, init_db
from backend.app.models.source import SourceRegistry
from backend.app.models.category import Category
from backend.app.core.config import settings


def seed_sources_and_categories():
    init_db()
    db = SessionLocal()
    
    yaml_path = settings.CONFIGS_DIR / "source_registry.yaml"
    if not yaml_path.exists():
        print(f"Error: {yaml_path} not found.")
        return

    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    # Seed Categories
    categories = data.get("categories", [])
    for cat in categories:
        existing = db.get(Category, cat["id"])
        if not existing:
            new_cat = Category(
                id=cat["id"],
                slug=cat["slug"],
                display_name=cat["display_name"],
                description=cat.get("description"),
                active=cat.get("active", True)
            )
            db.add(new_cat)
            print(f"Added category: {cat['display_name']}")
    db.commit()

    # Seed Sources
    sources = data.get("sources", [])
    for src in sources:
        existing = db.get(SourceRegistry, src["id"])
        if not existing:
            new_src = SourceRegistry(
                id=src["id"],
                name=src["name"],
                base_url=src["base_url"],
                authority_tier=src["authority_tier"],
                authority_score=src.get("authority_score", 1.0),
                source_type=src["source_type"],
                license_notes=src.get("license_notes"),
                active=src.get("active", True)
            )
            db.add(new_src)
            print(f"Added source: {src['name']}")
    db.commit()
    db.close()
    print("Database seeding completed successfully.")


if __name__ == "__main__":
    seed_sources_and_categories()
