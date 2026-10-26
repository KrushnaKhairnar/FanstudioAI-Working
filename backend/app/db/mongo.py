"""
FanStudioAI - MongoDB Database Manager & Persistent Storage Engine.
Unified database layer providing live PyMongo support with seamless
persistent file-backed JSON store fallback at data/mongodb/.
"""
import os
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from pymongo import MongoClient, ASCENDING, DESCENDING
    from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
    PYMONGO_AVAILABLE = True
except ImportError:
    PYMONGO_AVAILABLE = False
    MongoClient = None
    ASCENDING = 1
    DESCENDING = -1

from app.core.config import settings

logger = logging.getLogger("fanstudioai.mongo")

# Project directories
DATA_DIR = Path(settings.DATA_DIR)
CATALOG_PATH = DATA_DIR / "catalog.json"
PRODUCT_SAMPLE_PATH = DATA_DIR / "seed" / "products_sample.json"
DATA_MONGODB_DIR = DATA_DIR / "mongodb"

# Default Finishes
DEFAULT_FINISHES = [
    {"finish_id": "mf-matt-grey", "name": "Matt Grey", "type": "motor", "color_code": "#808080", "sort_order": 1, "is_active": True},
    {"finish_id": "mf-matt-black", "name": "Matt Black", "type": "motor", "color_code": "#1A1A1A", "sort_order": 2, "is_active": True},
    {"finish_id": "mf-matt-white", "name": "Matt White", "type": "motor", "color_code": "#F3F4F6", "sort_order": 3, "is_active": True},
    {"finish_id": "mf-antique-bronze", "name": "Antique Bronze", "type": "motor", "color_code": "#8B7355", "sort_order": 4, "is_active": True},
    {"finish_id": "mf-champagne-gold", "name": "Champagne Gold", "type": "motor", "color_code": "#D4AF37", "sort_order": 5, "is_active": True},
    {"finish_id": "mf-walnut", "name": "Walnut", "type": "motor", "color_code": "#5C4033", "sort_order": 6, "is_active": True},
    {"finish_id": "mf-teak", "name": "Teak", "type": "motor", "color_code": "#B3672B", "sort_order": 7, "is_active": True},
    {"finish_id": "bf-teak", "name": "Teak Wooden", "type": "blade", "color_code": "#C27E38", "sort_order": 1, "is_active": True},
    {"finish_id": "bf-rosewood", "name": "Rosewood Wooden", "type": "blade", "color_code": "#5F311C", "sort_order": 2, "is_active": True},
    {"finish_id": "bf-walnut", "name": "Walnut Wooden", "type": "blade", "color_code": "#996933", "sort_order": 3, "is_active": True},
    {"finish_id": "bf-natural-wood", "name": "Natural Wood", "type": "blade", "color_code": "#BA9962", "sort_order": 4, "is_active": True},
    {"finish_id": "bf-cane", "name": "Cane Weave", "type": "blade", "color_code": "#D2A66C", "sort_order": 5, "is_active": True},
    {"finish_id": "bf-matt-black", "name": "Matt Black", "type": "blade", "color_code": "#1A1A1A", "sort_order": 6, "is_active": True},
    {"finish_id": "bf-matt-white", "name": "Matt White", "type": "blade", "color_code": "#F3F4F6", "sort_order": 7, "is_active": True},
    {"finish_id": "bf-oriental-ash", "name": "Oriental Ash", "type": "blade", "color_code": "#D7B88C", "sort_order": 8, "is_active": True},
]

DEFAULT_MOTOR_COLORS = [
    "Matt Grey", "Metallic Grey", "Matt Black", "Matt White",
    "Antique Bronze", "Champagne Gold", "Walnut", "Teak"
]

DEFAULT_BLADE_COLORS = [
    "Teak Wooden", "Rosewood Wooden", "Walnut Wooden",
    "Natural Wood", "Cane Weave", "Matt Black", "Matt White"
]


class MockCursor:
    def __init__(self, data: List[Dict[str, Any]]):
        self._data = list(data)
        self._skip = 0
        self._limit = None
        self._sort_key = None
        self._sort_dir = 1

    def sort(self, key_or_list: Any, direction: int = 1):
        if isinstance(key_or_list, list) and key_or_list:
            self._sort_key = key_or_list[0][0]
            self._sort_dir = key_or_list[0][1]
        elif isinstance(key_or_list, str):
            self._sort_key = key_or_list
            self._sort_dir = direction
        return self

    def skip(self, n: int):
        self._skip = max(0, n)
        return self

    def limit(self, n: int):
        self._limit = n
        return self

    def _apply(self) -> List[Dict[str, Any]]:
        res = list(self._data)
        if self._sort_key:
            res.sort(
                key=lambda x: str(x.get(self._sort_key, "")),
                reverse=(self._sort_dir == -1 or self._sort_dir == DESCENDING)
            )
        if self._skip:
            res = res[self._skip:]
        if self._limit is not None and self._limit > 0:
            res = res[:self._limit]
        return res

    def __iter__(self):
        return iter(self._apply())

    def __len__(self):
        return len(self._apply())

    def __getitem__(self, idx):
        return self._apply()[idx]


class FileBackedCollection:
    """
    Persistent document collection mimicking PyMongo Collection interface.
    Stores documents as JSON in data/mongodb/<name>.json.
    Ensures seamless operation when live MongoDB daemon is not running.
    """
    def __init__(self, name: str, base_dir: Path):
        self.name = name
        self.file_path = base_dir / f"{name}.json"
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self._cache: Optional[List[Dict[str, Any]]] = None

    def _load(self) -> List[Dict[str, Any]]:
        if self._cache is not None:
            return self._cache
        if self.file_path.exists():
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._cache = data if isinstance(data, list) else []
                    return self._cache
            except Exception as e:
                logger.error(f"Error loading {self.file_path}: {e}")
                self._cache = []
                return self._cache
        self._cache = []
        return self._cache

    def _save(self) -> None:
        if self._cache is None:
            return
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self._cache, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving {self.file_path}: {e}")

    def count_documents(self, filter: Optional[Dict[str, Any]] = None) -> int:
        docs = self._load()
        if not filter:
            return len(docs)
        return len(list(self.find(filter)))

    def find(self, filter: Optional[Dict[str, Any]] = None):
        docs = self._load()
        if not filter:
            return MockCursor(docs)
        result = []
        for doc in docs:
            match = True
            for k, v in filter.items():
                if isinstance(v, dict) and "$in" in v:
                    if doc.get(k) not in v["$in"]:
                        match = False
                        break
                elif doc.get(k) != v:
                    match = False
                    break
            if match:
                result.append(doc)
        return MockCursor(result)

    def find_one(self, filter: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        cursor = self.find(filter)
        matches = list(cursor)
        return matches[0] if matches else None

    def insert_one(self, document: Dict[str, Any]) -> Dict[str, Any]:
        docs = self._load()
        docs.append(document)
        self._save()
        return {"inserted_id": document.get("_id", document.get("product_id"))}

    def insert_many(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        docs = self._load()
        docs.extend(documents)
        self._save()
        return {"inserted_ids": len(documents)}

    def update_one(self, filter: Dict[str, Any], update: Dict[str, Any], upsert: bool = False) -> Dict[str, Any]:
        docs = self._load()
        set_vals = update.get("$set", update)
        for i, doc in enumerate(docs):
            match = all(doc.get(k) == v for k, v in filter.items())
            if match:
                docs[i].update(set_vals)
                self._save()
                return {"matched_count": 1, "modified_count": 1}
        if upsert:
            new_doc = {**filter, **set_vals}
            docs.append(new_doc)
            self._save()
            return {"matched_count": 0, "modified_count": 0, "upserted_id": new_doc.get("product_id")}
        return {"matched_count": 0, "modified_count": 0}

    def delete_one(self, filter: Dict[str, Any]) -> Dict[str, Any]:
        docs = self._load()
        for i, doc in enumerate(docs):
            if all(doc.get(k) == v for k, v in filter.items()):
                docs.pop(i)
                self._save()
                return {"deleted_count": 1}
        return {"deleted_count": 0}

    def delete_many(self, filter: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not filter:
            count = len(self._load())
            self._cache = []
            self._save()
            return {"deleted_count": count}
        docs = self._load()
        retained = [d for d in docs if not all(d.get(k) == v for k, v in filter.items())]
        deleted = len(docs) - len(retained)
        self._cache = retained
        self._save()
        return {"deleted_count": deleted}

    def create_index(self, keys: Any, **kwargs) -> str:
        return "index_ok"


class FileBackedDatabase:
    """Mock Database wrapper mapping collection properties to FileBackedCollection."""
    def __init__(self, name: str, base_dir: Path):
        self.name = name
        self.base_dir = base_dir
        self._collections: Dict[str, FileBackedCollection] = {}

    def __getitem__(self, name: str) -> FileBackedCollection:
        if name not in self._collections:
            self._collections[name] = FileBackedCollection(name, self.base_dir)
        return self._collections[name]

    def __getattr__(self, name: str) -> FileBackedCollection:
        return self[name]

    def list_collection_names(self) -> List[str]:
        return [
            "products", "finishes", "combinations", "visualizations",
            "audit_logs", "ai_jobs", "ai_configurations", "rooms", "visualization_results"
        ]


class MongoDBManager:
    """Unified MongoDB manager for Python handling live server or file-backed storage."""
    def __init__(self):
        self.uri = settings.MONGODB_URI or "mongodb://127.0.0.1:27017"
        self.db_name = settings.DB_NAME or "fanstudio"
        self.is_live = False
        self.client = None
        self.db = None
        self._connect()

    def _connect(self) -> None:
        if PYMONGO_AVAILABLE and self.uri:
            try:
                logger.info(f"Connecting to MongoDB at {self.uri}...")
                self.client = MongoClient(self.uri, serverSelectionTimeoutMS=2000)
                self.client.admin.command("ping")
                self.db = self.client[self.db_name]
                self.is_live = True
                logger.info(f"Successfully connected to MongoDB server! Database: {self.db_name}")
                return
            except (ConnectionFailure, ServerSelectionTimeoutError, Exception) as e:
                logger.warning(f"Could not connect to live MongoDB daemon ({e}). Using file-backed storage at {DATA_MONGODB_DIR}.")

        # Fallback to persistent file-backed collections
        self.is_live = False
        self.client = None
        self.db = FileBackedDatabase(self.db_name, DATA_MONGODB_DIR)
        logger.info(f"Initialized persistent file-backed MongoDB database '{self.db_name}' at {DATA_MONGODB_DIR}")

    def connect(self) -> None:
        """Connect database and initialize indexes."""
        self._connect()
        self.create_indexes()
        for f in DEFAULT_FINISHES:
            if not self.db.finishes.find_one({"finish_id": f["finish_id"]}):
                self.db.finishes.insert_one(dict(f))

    def disconnect(self) -> None:
        """Close database connection if open."""
        if self.client and hasattr(self.client, "close"):
            try:
                self.client.close()
                logger.info("Database connection closed.")
            except Exception:
                pass

    @property
    def engine_type(self) -> str:
        return "mongodb" if self.is_live else "mongita_persistent"

    # Collection property shortcuts
    @property
    def products(self):
        return self.db["products"]

    @property
    def finishes(self):
        return self.db["finishes"]

    @property
    def product_variants(self):
        return self.db["product_variants"]

    @property
    def product_media(self):
        return self.db["product_media"]

    @property
    def combinations(self):
        return self.db["combinations"]

    @property
    def visualizations(self):
        return self.db["visualizations"]

    @property
    def audit_logs(self):
        return self.db["audit_logs"]

    @property
    def ai_jobs(self):
        return self.db["ai_jobs"]

    @property
    def ai_configurations(self):
        return self.db["ai_configurations"]

    @property
    def rooms(self):
        return self.db["rooms"]

    @property
    def visualization_results(self):
        return self.db["visualization_results"]

    def __getitem__(self, name: str):
        return self.db[name]

    def create_indexes(self) -> None:
        """Create required indexes for fast querying and uniqueness."""
        try:
            logger.info("Configuring MongoDB indexes...")
            if self.is_live and self.db is not None:
                self.db.products.create_index([("product_id", ASCENDING)], unique=True)
                self.db.products.create_index([("product_code", ASCENDING)], unique=True)
                self.db.products.create_index([("category", ASCENDING)])
                self.db.products.create_index([("status", ASCENDING)])

                self.db.finishes.create_index([("finish_id", ASCENDING)], unique=True)
                self.db.finishes.create_index([("type", ASCENDING), ("is_active", ASCENDING)])

                self.db.combinations.create_index([
                    ("fan_code", ASCENDING),
                    ("motor_color", ASCENDING),
                    ("blade_color", ASCENDING)
                ], unique=True)
            logger.info("MongoDB indexes verified successfully.")
        except Exception as e:
            logger.warning(f"Index creation note: {e}")

    def seed_database(self, force: bool = False) -> Dict[str, Any]:
        """
        Seeds catalog products and finishes into MongoDB.
        Ensures motor_colors, blade_colors, and combinations are set for all fans.
        """
        # Ensure baseline default finishes are present
        for f in DEFAULT_FINISHES:
            if not self.db.finishes.find_one({"finish_id": f["finish_id"]}):
                self.db.finishes.insert_one(dict(f))

        existing_products_count = self.db.products.count_documents({})
        if existing_products_count > 0 and not force:
            logger.info(f"Database already contains {existing_products_count} products. Skipping re-seed.")
            return self.get_status()

        logger.info("Seeding MongoDB catalog with fan models and finishes...")

        source_products = []
        if CATALOG_PATH.exists():
            try:
                with open(CATALOG_PATH, "r", encoding="utf-8") as f:
                    cat_data = json.load(f)
                    if isinstance(cat_data, dict) and "products" in cat_data:
                        source_products = cat_data["products"]
                    elif isinstance(cat_data, list):
                        source_products = cat_data
            except Exception as e:
                logger.error(f"Error reading {CATALOG_PATH}: {e}")

        if not source_products and PRODUCT_SAMPLE_PATH.exists():
            try:
                with open(PRODUCT_SAMPLE_PATH, "r", encoding="utf-8") as f:
                    sample_data = json.load(f)
                    source_products = sample_data if isinstance(sample_data, list) else sample_data.get("products", [])
            except Exception as e:
                logger.error(f"Error reading {PRODUCT_SAMPLE_PATH}: {e}")

        formatted_products = []
        for p in source_products:
            prod_id = p.get("product_id") or p.get("productId") or f"prod-{len(formatted_products)+1}"
            fan_code = p.get("fanCode") or p.get("product_code") or prod_id
            name = p.get("name") or p.get("fanName") or "Ceiling Fan"
            category = p.get("category") or "Ceiling"

            motor_colors = p.get("motor_colors") or DEFAULT_MOTOR_COLORS
            blade_colors = p.get("blade_colors") or DEFAULT_BLADE_COLORS
            default_motor = p.get("default_motor_color") or motor_colors[0]
            default_blade = p.get("default_blade_color") or blade_colors[0]

            combinations = []
            for mc in motor_colors:
                m_slug = mc.lower().replace(" ", "-")
                for bc in blade_colors:
                    b_slug = bc.lower().replace(" ", "-")
                    combinations.append({
                        "combination_id": f"{fan_code}_{m_slug}_{b_slug}",
                        "motor_color": mc,
                        "blade_color": bc,
                        "image_url": f"/api/users/combination-image?fan_code={fan_code}&motor_color={mc}&blade_color={bc}",
                        "transparent_image_url": f"/api/users/combination-image?fan_code={fan_code}&motor_color={mc}&blade_color={bc}&transparent=true"
                    })

            doc = {
                **p,
                "product_id": prod_id,
                "product_code": fan_code,
                "fanCode": fan_code,
                "name": name,
                "fanName": name,
                "category": category,
                "motor_colors": motor_colors,
                "blade_colors": blade_colors,
                "default_motor_color": default_motor,
                "default_blade_color": default_blade,
                "color_combinations": combinations,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            formatted_products.append(doc)

        if force:
            self.db.products.delete_many({})
            self.db.finishes.delete_many({})

        for fp in formatted_products:
            self.db.products.update_one({"product_id": fp["product_id"]}, {"$set": fp}, upsert=True)

        for f in DEFAULT_FINISHES:
            self.db.finishes.update_one({"finish_id": f["finish_id"]}, {"$set": f}, upsert=True)

        logger.info(f"Database seeded successfully with {len(formatted_products)} products and {len(DEFAULT_FINISHES)} finishes.")
        return self.get_status()

    def get_status(self) -> Dict[str, Any]:
        """Returns connection state and counts across collections."""
        prod_count = self.db.products.count_documents({})
        finish_count = self.db.finishes.count_documents({})
        vis_count = self.db.visualizations.count_documents({}) if hasattr(self.db, "visualizations") else 0
        comb_count = self.db.combinations.count_documents({}) if hasattr(self.db, "combinations") else 0

        return {
            "is_live": self.is_live,
            "engine": "live_mongodb" if self.is_live else "file_backed_mongodb",
            "database": self.db_name,
            "uri": self.uri if self.is_live else "Local File-backed MongoDB Store",
            "collections": {
                "products": prod_count,
                "finishes": finish_count,
                "visualizations": vis_count,
                "combinations": comb_count
            }
        }


# Global database manager singleton
db_manager = MongoDBManager()


def get_db() -> MongoDBManager:
    """Retrieve active database manager."""
    return db_manager


def get_status() -> Dict[str, Any]:
    """Retrieve active database status."""
    return db_manager.get_status()


def init_db(force: bool = False) -> Dict[str, Any]:
    """Initialize database, create indexes and seed data."""
    db_manager.create_indexes()
    return db_manager.seed_database(force=force)


__all__ = [
    "MongoDBManager",
    "FileBackedCollection",
    "FileBackedDatabase",
    "MockCursor",
    "db_manager",
    "get_db",
    "get_status",
    "init_db",
    "DEFAULT_FINISHES",
    "DEFAULT_MOTOR_COLORS",
    "DEFAULT_BLADE_COLORS",
]
