-- pgvector schema init for DHIS2 AI Analyst metadata index.
-- Runs automatically on first Postgres container startup.

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS metadata_index (
    uid TEXT PRIMARY KEY,
    object_type TEXT NOT NULL,
    name TEXT NOT NULL,
    short_name TEXT,
    description TEXT,
    dataset_names TEXT,
    embedding vector(1536),
    raw_metadata JSONB,
    last_synced_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS metadata_index_embedding_idx
ON metadata_index USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

CREATE INDEX IF NOT EXISTS metadata_index_name_idx
ON metadata_index USING gin (to_tsvector('english', name || ' ' || COALESCE(short_name, '') || ' ' || COALESCE(description, '')));
