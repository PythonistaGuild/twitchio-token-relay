CREATE TABLE IF NOT EXISTS applications(
    id BIGINT GENERATED ALWAYS AS IDENTITY (START WITH 10000) PRIMARY KEY,
    user_id TEXT NOT NULL,
    client_id TEXT UNIQUE,
    name TEXT NOT NULL,
    scopes TEXT NOT NULL,
    bot_scopes TEXT NOT NULL,
    auths BIGINT,
    UNIQUE (user_id, name)
);

CREATE TABLE IF NOT EXISTS whitelist(
    application_id TEXT NOT NULL,
    allowed TEXT NOT NULL,
    PRIMARY KEY (application_id, allowed)
);