"""
MongoDB Schema definitions, index strategy, and collection validation constraints.
Adheres strictly to FanStudioAI Master Development Plan Section 5, 6, and 7.
"""
from typing import Dict, Any, List

COLLECTION_NAMES = [
    "admins",
    "products",
    "finishes",
    "product_variants",
    "product_media",
    "ai_configurations",
    "ai_jobs",
    "room_analyses",
    "generated_results",
    "audit_logs",
    "visitor_sessions",
    "usage_events",
    "system_settings",
]

INDEX_DEFINITIONS: Dict[str, List[Dict[str, Any]]] = {
    "admins": [
        {"fields": [("admin_id", 1)], "unique": True},
        {"fields": [("email", 1)], "unique": True},
        {"fields": [("role", 1)]},
    ],
    "products": [
        {"fields": [("product_id", 1)], "unique": True},
        {"fields": [("product_code", 1)], "unique": True},
        {"fields": [("status", 1)]},
        {"fields": [("created_at", -1)]},
    ],
    "finishes": [
        {"fields": [("finish_id", 1)], "unique": True},
        {"fields": [("type", 1), ("is_active", 1)]},
        {"fields": [("sort_order", 1)]},
    ],
    "product_variants": [
        {"fields": [("variant_id", 1)], "unique": True},
        {"fields": [("product_id", 1), ("motor_finish_id", 1), ("blade_finish_id", 1)], "unique": True},
        {"fields": [("product_id", 1), ("is_active", 1)]},
        {"fields": [("sku", 1)]},
    ],
    "product_media": [
        {"fields": [("media_id", 1)], "unique": True},
        {"fields": [("product_id", 1), ("sort_order", 1)]},
        {"fields": [("variant_id", 1)]},
    ],
    "ai_configurations": [
        {"fields": [("product_id", 1)], "unique": True},
    ],
    "ai_jobs": [
        {"fields": [("job_id", 1)], "unique": True},
        {"fields": [("status", 1)]},
        {"fields": [("product_id", 1)]},
        {"fields": [("created_at", -1)]},
    ],
    "room_analyses": [
        {"fields": [("analysis_id", 1)], "unique": True},
        {"fields": [("job_id", 1)], "unique": True},
    ],
    "generated_results": [
        {"fields": [("result_id", 1)], "unique": True},
        {"fields": [("job_id", 1)], "unique": True},
        {"fields": [("created_at", -1)]},
    ],
    "audit_logs": [
        {"fields": [("log_id", 1)], "unique": True},
        {"fields": [("admin_id", 1)]},
        {"fields": [("created_at", -1)]},
    ],
    "system_settings": [
        {"fields": [("key", 1)], "unique": True},
    ],
}
