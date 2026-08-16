-- Scanline database schema (Postgres + pgvector extension)
CREATE EXTENSION IF NOT EXISTS vector;
 
CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           TEXT UNIQUE NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
 
-- One row per profile snapshot so we keep history, not just current state.
CREATE TABLE profiles (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    northstar       TEXT NOT NULL,
    final_idea      TEXT,
    timeframe       TEXT,
    stage           TEXT,
    priorities      TEXT[],
    skills          TEXT,
    dealbreakers    TEXT,
    location_pref   TEXT,
    target_types    TEXT[],           -- 'job','internship','college'
    is_current      BOOLEAN NOT NULL DEFAULT true,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_profiles_user_current ON profiles(user_id) WHERE is_current;
 
CREATE TABLE listings (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source          TEXT NOT NULL,     -- 'adzuna','usajobs','greenhouse', etc.
    external_id     TEXT NOT NULL,     -- id from the source, for dedupe
    title           TEXT NOT NULL,
    org             TEXT NOT NULL,
    type            TEXT NOT NULL,     -- 'job','internship','college'
    location         TEXT,
    description     TEXT,
    tags            TEXT[],
    deadline        DATE,
    apply_url       TEXT NOT NULL,
    fetched_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(source, external_id)
);
CREATE INDEX idx_listings_type ON listings(type);
CREATE INDEX idx_listings_tags ON listings USING GIN(tags);
 
CREATE TABLE match_scores (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    listing_id      UUID NOT NULL REFERENCES listings(id) ON DELETE CASCADE,
    profile_id      UUID NOT NULL REFERENCES profiles(id),
    score_pct       NUMERIC(5,2) NOT NULL,
    goal_match_tags TEXT[],
    skill_match_tags TEXT[],
    rationale       TEXT,
    scan_cycle      INTEGER NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(user_id, listing_id, scan_cycle)
);
 
CREATE TABLE outcomes (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    listing_id      UUID NOT NULL REFERENCES listings(id) ON DELETE CASCADE,
    status          TEXT NOT NULL,     -- 'applied','interview','rejected','ghosted','offer'
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
 
CREATE TABLE roadmap_milestones (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title           TEXT NOT NULL,
    description     TEXT,
    target_stage    INTEGER NOT NULL,   -- ordering within roadmap
    status          TEXT NOT NULL DEFAULT 'planned', -- planned/in_progress/done
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
 
-- Summarized chat memory chunks, embedded for retrieval (RAG-style).
CREATE TABLE chat_memory (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    summary         TEXT NOT NULL,
    embedding       vector(1536),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
 
CREATE TABLE applications (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    listing_id      UUID NOT NULL REFERENCES listings(id) ON DELETE CASCADE,
    draft_content   TEXT,
    confidence_pct  NUMERIC(5,2),
    status          TEXT NOT NULL DEFAULT 'pending_review', -- pending_review/approved/sent/undone
    sendable_at     TIMESTAMPTZ,        -- undo window expiry
    sent_at         TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
 
