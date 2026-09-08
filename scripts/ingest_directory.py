import sys
from pathlib import Path

# Add root directory to sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from backend.app.database.session import SessionLocal, init_db
from backend.app.services.ingestion_service import IngestionService
from backend.app.database.repositories.source_repo import SourceRepository
from backend.app.core.config import settings


def ingest_corpus():
    init_db()
    db = SessionLocal()
    source_repo = SourceRepository(db)
    ingestion_service = IngestionService(db)

    # Map folders/files to sources & categories
    raw_dir = settings.DATA_DIR / "raw"
    if not raw_dir.exists():
        print("No raw directory found.")
        return

    # Look up source IDs
    who_source = source_repo.get_source_by_name("World Health Organization")
    cdc_source = source_repo.get_source_by_name("Centers for Disease Control and Prevention (CDC)")
    medline_source = source_repo.get_source_by_name("MedlinePlus (National Library of Medicine / NIH)")
    icmr_source = source_repo.get_source_by_name("Indian Council of Medical Research (ICMR)")

    # Category map
    cat_hypertension = source_repo.get_category_by_slug("chronic_condition_education")
    cat_nutrition = source_repo.get_category_by_slug("nutrition")
    cat_concepts = source_repo.get_category_by_slug("common_health_concepts")
    cat_vaccine = source_repo.get_category_by_slug("vaccination")
    cat_mental = source_repo.get_category_by_slug("mental_health_education")
    cat_maternal = source_repo.get_category_by_slug("maternal_and_child_health")
    cat_infection = source_repo.get_category_by_slug("infectious_disease_education")

    files_to_ingest = [
        # WHO
        (raw_dir / "who" / "who_hypertension_factsheet.md", who_source.id if who_source else None, cat_hypertension.id if cat_hypertension else 1),
        (raw_dir / "who" / "who_healthy_diet_factsheet.md", who_source.id if who_source else None, cat_nutrition.id if cat_nutrition else 1),
        (raw_dir / "who" / "who_diabetes_factsheet.md", who_source.id if who_source else None, cat_hypertension.id if cat_hypertension else 1),
        # MedlinePlus
        (raw_dir / "nih_medlineplus" / "medlineplus_dehydration.md", medline_source.id if medline_source else None, cat_concepts.id if cat_concepts else 1),
        (raw_dir / "nih_medlineplus" / "medlineplus_anxiety.md", medline_source.id if medline_source else None, cat_mental.id if cat_mental else 1),
        (raw_dir / "nih_medlineplus" / "medlineplus_fever.md", medline_source.id if medline_source else None, cat_infection.id if cat_infection else 1),
        # CDC
        (raw_dir / "cdc" / "cdc_vaccine_basics.md", cdc_source.id if cdc_source else None, cat_vaccine.id if cat_vaccine else 1),
        # ICMR
        (raw_dir / "icmr" / "icmr_maternal_child_nutrition.md", icmr_source.id if icmr_source else None, cat_maternal.id if cat_maternal else 1),
    ]

    for file_path, source_id, category_id in files_to_ingest:
        if file_path.exists() and source_id:
            try:
                doc = ingestion_service.ingest_file(
                    file_path=file_path,
                    source_id=source_id,
                    category_id=category_id
                )
                print(f"Successfully ingested: {doc.title} ({len(doc.chunks)} chunks)")
            except Exception as e:
                print(f"Error ingesting {file_path.name}: {e}")

    db.close()
    print("Corpus ingestion complete.")


if __name__ == "__main__":
    ingest_corpus()
