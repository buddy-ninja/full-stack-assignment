-- Starter schema. Users, pets and collar activity are provided.
-- Chat turns, reviews and audit entries are yours to design: add them in
-- your own migrations (see README).

CREATE TABLE users (
    id           TEXT PRIMARY KEY,
    email        TEXT NOT NULL UNIQUE,
    display_name TEXT NOT NULL,
    role         TEXT NOT NULL CHECK (role IN ('owner', 'vet', 'admin')),
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE pets (
    id         TEXT PRIMARY KEY,
    owner_id   TEXT NOT NULL REFERENCES users (id),
    name       TEXT NOT NULL,
    species    TEXT NOT NULL CHECK (species IN ('dog', 'cat')),
    breed      TEXT,
    sex        TEXT CHECK (sex IN ('male', 'female')),
    neutered   BOOLEAN,
    birth_date DATE,
    weight_kg  NUMERIC(5, 2),
    notes      TEXT
);

CREATE INDEX pets_owner_id_idx ON pets (owner_id);

-- Daily posture minutes from the collar, as produced by the behaviour service.
-- Minutes not covered by the four postures are time the collar was off or charging.
CREATE TABLE activity_daily (
    pet_id       TEXT NOT NULL REFERENCES pets (id),
    day          DATE NOT NULL,
    lying_min    INTEGER NOT NULL CHECK (lying_min >= 0),
    sitting_min  INTEGER NOT NULL CHECK (sitting_min >= 0),
    standing_min INTEGER NOT NULL CHECK (standing_min >= 0),
    walking_min  INTEGER NOT NULL CHECK (walking_min >= 0),
    PRIMARY KEY (pet_id, day),
    CHECK (lying_min + sitting_min + standing_min + walking_min <= 1440)
);
