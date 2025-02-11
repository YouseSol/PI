CREATE DATABASE db_pi;

\c db_pi root

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE SCHEMA PI;

CREATE DOMAIN PI.EMAIL_TYPE AS TEXT;

CREATE TABLE IF NOT EXISTS PI.Client(
    email               PI.EMAIL_TYPE NOT NULL UNIQUE,

    first_name          VARCHAR       NOT NULL,
    last_name           VARCHAR       NOT NULL,

    hash                TEXT          NOT NULL,

    linkedin_account_id VARCHAR       NOT NULL UNIQUE,

    standard_message    VARCHAR       NOT NULL,

    active              BOOL          NOT NULL DEFAULT TRUE,

    created_at          TIMESTAMP     NOT NULL,

    deleted             BOOL          NOT NULL DEFAULT FALSE,
    deleted_at          TIMESTAMP         NULL,

    token               UUID                   DEFAULT uuid_generate_v4(),

    CHECK (deleted = FALSE OR deleted_at IS NOT NULL),

    PRIMARY KEY (token)
);

CREATE UNIQUE INDEX unique_not_deleted_client_email ON PI.Client (email) WHERE deleted = FALSE;
CREATE UNIQUE INDEX unique_not_deleted_client_linkedin_account_id ON PI.Client (linkedin_account_id) WHERE deleted = FALSE;

CREATE TABLE IF NOT EXISTS PI.SalesRepresentative(
    id                         SERIAL        UNIQUE,

    owner                      PI.EMAIL_TYPE NOT NULL UNIQUE,

    first_name                 VARCHAR       NOT NULL,
    last_name                  VARCHAR       NOT NULL,

    email                      VARCHAR       NOT NULL,

    active                     BOOL          NOT NULL DEFAULT TRUE,

    created_at                 TIMESTAMP     NOT NULL,

    deleted                    BOOL          NOT NULL DEFAULT FALSE,
    deleted_at                 TIMESTAMP         NULL,

    CHECK (deleted = FALSE OR deleted_at IS NOT NULL),

    PRIMARY KEY (id),

    FOREIGN KEY (owner) REFERENCES PI.Client(email) ON DELETE CASCADE
);

CREATE UNIQUE INDEX unique_not_deleted_sales_representative_client_and_email ON PI.SalesRepresentative (owner, email) WHERE deleted = FALSE;

CREATE TABLE IF NOT EXISTS PI.Campaign(
    id                         SERIAL        UNIQUE,

    owner                      PI.EMAIL_TYPE NOT NULL,

    name                       VARCHAR       NOT NULL,

    active                     BOOL          NOT NULL DEFAULT TRUE,

    created_at                 TIMESTAMP     NOT NULL,

    deleted                    BOOL          NOT NULL DEFAULT FALSE,
    deleted_at                 TIMESTAMP         NULL,

    CHECK (deleted = FALSE OR deleted_at IS NOT NULL),

    PRIMARY KEY (id),

    FOREIGN KEY (owner) REFERENCES PI.Client(email) ON DELETE CASCADE
);

CREATE UNIQUE INDEX unique_not_deleted_campaigns ON PI.Campaign (owner, name) WHERE deleted = FALSE;

CREATE TABLE IF NOT EXISTS PI.Lead(
    id                         SERIAL        UNIQUE,

    campaign                   INTEGER       NOT NULL,

    linkedin_public_identifier VARCHAR       NOT NULL,
    chat_id                    VARCHAR           NULL,

    first_name                 VARCHAR       NOT NULL,
    last_name                  VARCHAR       NOT NULL,

    emails                     VARCHAR[]     NOT NULL,
    phones                     VARCHAR[]     NOT NULL,

    active                     BOOL          NOT NULL DEFAULT TRUE,

    deleted                    BOOL          NOT NULL DEFAULT FALSE,
    deleted_at                 TIMESTAMP         NULL,

    CHECK (deleted = FALSE OR deleted_at IS NOT NULL),

    PRIMARY KEY (id),

    FOREIGN KEY (campaign) REFERENCES PI.Campaign(id) ON DELETE CASCADE
);

CREATE UNIQUE INDEX unique_not_deleted_leads ON PI.Lead (campaign, linkedin_public_identifier) WHERE deleted = FALSE;

CREATE TABLE IF NOT EXISTS PI.FailedLead(
    campaign                   INTEGER       NOT NULL,

    id                         SERIAL        UNIQUE,

    first_name                 VARCHAR       NOT NULL,
    last_name                  VARCHAR       NOT NULL,
    profile_url                VARCHAR       NOT NULL,

    PRIMARY KEY (id),

    FOREIGN KEY (campaign) REFERENCES PI.Campaign(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS PI.MessageSent(
    id                         VARCHAR       NOT NULL UNIQUE,
    lead                       INTEGER       NOT NULL,
    sent_at                    TIMESTAMP     NOT NULL,

    PRIMARY KEY (id),

    FOREIGN KEY (lead) REFERENCES PI.Lead(id) ON DELETE CASCADE
);
