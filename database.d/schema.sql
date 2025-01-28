CREATE DATABASE db_pi;

\c db_pi root

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE SCHEMA PI;

CREATE DOMAIN PI.EMAIL_TYPE AS TEXT;

CREATE TABLE IF NOT EXISTS PI.Client(
    email               PI.EMAIL_TYPE NOT NULL UNIQUE,

    first_name          VARCHAR       NOT NULL,
    last_name           VARCHAR       NOT NULL,
    standart_message    VARCHAR       NOT NULL,

    linkedin_account_id VARCHAR       NOT NULL UNIQUE,

    hash                TEXT          NOT NULL,

    active              BOOL          NOT NULL DEFAULT TRUE,
    deleted             BOOL          NOT NULL DEFAULT FALSE,

    token               UUID                   DEFAULT uuid_generate_v4(),

    PRIMARY KEY (token)
);

CREATE TABLE IF NOT EXISTS PI.Lead(
    owner                      PI.EMAIL_TYPE NOT NULL,

    id                         SERIAL        UNIQUE,

    linkedin_public_identifier VARCHAR       NOT NULL,
    chat_id                    VARCHAR           NULL,

    first_name                 VARCHAR       NOT NULL,
    last_name                  VARCHAR       NOT NULL,

    emails                     VARCHAR[]     NOT NULL,
    phones                     VARCHAR[]     NOT NULL,

    active                     BOOL          NOT NULL DEFAULT TRUE,
    deleted                    BOOL          NOT NULL DEFAULT FALSE,

    UNIQUE(owner, linkedin_public_identifier),

    PRIMARY KEY (owner, linkedin_public_identifier),

    FOREIGN KEY (owner) REFERENCES PI.Client(email) ON DELETE CASCADE
);
