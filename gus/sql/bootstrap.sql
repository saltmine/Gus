CREATE EXTENSION IF NOT EXISTS plpgsql;
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

/* This is redundant, but explicit is better than implicit */
SET default_with_oids = false;

CREATE TABLE versions (
    from_version integer NOT NULL,
    to_version integer NOT NULL,
    date_migrated timestamp without time zone DEFAULT now() NOT NULL
);

CREATE SEQUENCE deploy_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

CREATE TABLE deploys (
  deploy_id integer NOT NULL DEFAULT nextval('deploy_id_seq'),
  delpoy_date timestamp without time zone NOT NULL DEFAULT now(),
  project varchar(256),
  version varchar(256),
  deploying_user varchar(256),
  CONSTRAINT deploy_pkey PRIMARY KEY (deploy_id)
);
CREATE INDEX deploy_project_date ON deploys (project, deploy_date);
