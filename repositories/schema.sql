-- Database schema for artwork backend
-- Compatible with SQLite, PostgreSQL, and other SQL databases
-- 
-- PostgreSQL-specific optimizations:
-- - Uses UUID type for UUID fields (PostgreSQL native UUID support)
-- - Uses VARCHAR for string fields (more efficient than TEXT for short strings)
-- - Uses TIMESTAMP for datetime fields (PostgreSQL handles timezone-aware timestamps)
-- - Foreign key constraints ensure referential integrity
-- - Indexes optimize common query patterns
--
-- Note: For SQLite compatibility, UUID fields are stored as TEXT/VARCHAR(36)
-- The application code generates UUIDs as strings using str(uuid.uuid4())

CREATE TABLE IF NOT EXISTS user_profiles (
    user_id UUID PRIMARY KEY references auth.users(id) on delete cascade
);

-- Table for storing artwork explanations
CREATE TABLE IF NOT EXISTS artwork_explanations (
    artwork_id UUID PRIMARY KEY,
    explanation_xml TEXT NOT NULL,
    image_path VARCHAR(500),  -- Path to image in Supabase Storage
    creator_user_id UUID references user_profiles(user_id) on delete set null,  -- User who created/uploaded the artwork (nullable for anonymous)
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Table for storing subject expansions
CREATE TABLE IF NOT EXISTS subject_expansions (
    expansion_id UUID PRIMARY KEY,
    artwork_id UUID NOT NULL,
    subject VARCHAR(500) NOT NULL,
    subject_hash VARCHAR(64) NOT NULL,  -- PostgreSQL-generated hash of subject for efficient caching
    expansion_xml TEXT NOT NULL,
    parent_expansion_id UUID,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (artwork_id) REFERENCES artwork_explanations(artwork_id) on delete cascade,
    FOREIGN KEY (parent_expansion_id) REFERENCES subject_expansions(expansion_id) on delete cascade
);

-- Index for faster lookups on artwork_id in subject_expansions
CREATE INDEX IF NOT EXISTS idx_subject_expansions_artwork_id ON subject_expansions(artwork_id);

-- Index for faster lookups on parent_expansion_id in subject_expansions
CREATE INDEX IF NOT EXISTS idx_subject_expansions_parent_expansion_id ON subject_expansions(parent_expansion_id);

-- Index for efficient caching lookups by artwork_id, subject_hash, and parent_expansion_id
CREATE INDEX IF NOT EXISTS idx_subject_expansions_artwork_subject_hash_parent ON subject_expansions(artwork_id, subject_hash, parent_expansion_id);

-- Table for tracking which users have saved which artworks
CREATE TABLE IF NOT EXISTS user_saved_artworks (
    user_id UUID NOT NULL references user_profiles(user_id) on delete cascade,
    artwork_id UUID NOT NULL,
    saved_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, artwork_id),
    FOREIGN KEY (artwork_id) REFERENCES artwork_explanations(artwork_id) on delete cascade
);

-- Index for faster lookups on creator_user_id in artwork_explanations
CREATE INDEX IF NOT EXISTS idx_artwork_explanations_creator_user_id ON artwork_explanations(creator_user_id);

-- Indexes for efficient queries on user_saved_artworks
CREATE INDEX IF NOT EXISTS idx_user_saved_artworks_user_id ON user_saved_artworks(user_id);
CREATE INDEX IF NOT EXISTS idx_user_saved_artworks_artwork_id ON user_saved_artworks(artwork_id);
CREATE INDEX IF NOT EXISTS idx_user_saved_artworks_saved_at ON user_saved_artworks(saved_at);

-- Index for faster lookups on created_at in both tables
CREATE INDEX IF NOT EXISTS idx_artwork_explanations_created_at ON artwork_explanations(created_at);
CREATE INDEX IF NOT EXISTS idx_subject_expansions_created_at ON subject_expansions(created_at);
