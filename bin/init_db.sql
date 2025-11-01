DROP TABLE users CASCADE;
DROP TABLE posts;

-- CREATE TYPE userStatus AS ENUM (
--     'ACTIVE',
--     'DISABLED',
--     'DEACTIVATED'
-- );

-- CREATE TYPE postStatus AS ENUM (
--     'pending',
--     'sent',
--     'failed'
-- );

CREATE TABLE users (
    id BIGINT PRIMARY KEY,
    username VARCHAR(15) NOT NULL UNIQUE,
    display_name VARCHAR(50) NOT NULL,
    profile_img VARCHAR DEFAULT NULL,
    registered_at TIMESTAMPTZ DEFAULT NOW(),
    is_premium BOOLEAN NOT NULL,
    user_status userStatus NOT NULL DEFAULT 'ACTIVE'
);

CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    content VARCHAR NOT NULL,
    post_img VARCHAR DEFAULT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    scheduled_time TIMESTAMPTZ,
    post_status postStatus NOT NULL DEFAULT 'pending',
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE
);