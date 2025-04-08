CREATE TABLE IF NOT EXISTS users(
    id BIGINT GENERATED ALWAYS AS IDENTITY (START WITH 10000) PRIMARY KEY,
    twitch_id TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    token TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS applications(
    id TEXT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    client_id TEXT UNIQUE,
    name TEXT NOT NULL,
    scopes TEXT NOT NULL,
    bot_scopes TEXT NOT NULL,
    auths BIGINT,
    UNIQUE (user_id, name),
    CONSTRAINT fk_applications_users FOREIGN KEY (user_id) REFERENCES users (id)
);

CREATE TABLE IF NOT EXISTS whitelist(
    application_id TEXT NOT NULL,
    allowed TEXT NOT NULL,
    PRIMARY KEY (application_id, allowed),
    CONSTRAINT fk_whitelist_applications FOREIGN KEY (application_id) REFERENCES applications (id)
);