-- SQL queries for artwork repository operations
-- Compatible with PostgreSQL

-- name: ensure_user_profile
-- Ensure a user profile exists in the database
INSERT INTO user_profiles (user_id) VALUES (:user_id::uuid)
ON CONFLICT (user_id) DO NOTHING;

-- name: save_artwork_explanation
-- Save an artwork explanation to the database
INSERT INTO artwork_explanations (artwork_id, explanation_xml, image_path, creator_user_id, created_at)
VALUES (:artwork_id::uuid, :explanation_xml, :image_path, :creator_user_id::uuid, :created_at);

-- name: get_artwork_explanation
-- Retrieve an artwork explanation by artwork_id
SELECT artwork_id, explanation_xml, image_path, creator_user_id, created_at
FROM artwork_explanations
WHERE artwork_id = :artwork_id::uuid;

-- name: save_subject_expansion
-- Save a subject expansion to the database
INSERT INTO subject_expansions (expansion_id, artwork_id, subject, subject_hash, expansion_xml, parent_expansion_id, created_at)
VALUES (:expansion_id::uuid, :artwork_id::uuid, :subject::text, md5(:subject::text), :expansion_xml, :parent_expansion_id::uuid, :created_at);

-- name: get_subject_expansion
-- Retrieve a subject expansion by expansion_id
SELECT expansion_id, artwork_id, subject, subject_hash, expansion_xml, parent_expansion_id, created_at
FROM subject_expansions
WHERE expansion_id = :expansion_id::uuid;

-- name: get_subject_expansions
-- Retrieve all subject expansions for a given artwork
SELECT expansion_id, artwork_id, subject, subject_hash, expansion_xml, parent_expansion_id, created_at
FROM subject_expansions
WHERE artwork_id = :artwork_id::uuid
ORDER BY created_at;

-- name: get_cached_subject_expansion
-- Retrieve a subject expansion by artwork_id, subject, and parent_expansion_id for caching (PostgreSQL generates hash)
SELECT expansion_id, artwork_id, subject, subject_hash, expansion_xml, parent_expansion_id, created_at
FROM subject_expansions
WHERE artwork_id = :artwork_id::uuid 
  AND subject_hash = md5(:subject::text)
  AND (parent_expansion_id = :parent_expansion_id::uuid OR (parent_expansion_id IS NULL AND :parent_expansion_id IS NULL));

-- name: save_user_artwork
-- Save an artwork to a user's collection
INSERT INTO user_saved_artworks (user_id, artwork_id, saved_at)
VALUES (:user_id::uuid, :artwork_id::uuid, :saved_at);

-- name: get_user_saved_artworks
-- Retrieve all artworks saved by a user (metadata only, no XML)
select artwork_id, image_path, created_at, creator_user_id, created_at as saved_at
from artwork_explanations
-- SELECT ae.artwork_id, ae.image_path, ae.created_at, ae.creator_user_id, usa.saved_at
-- FROM user_saved_artworks usa
-- JOIN artwork_explanations ae ON usa.artwork_id = ae.artwork_id
-- WHERE usa.user_id = :user_id::uuid
-- ORDER BY usa.saved_at DESC;
