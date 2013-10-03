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

CREATE SEQUENCE project_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

CREATE SEQUENCE release_candidate_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

CREATE SEQUENCE environment_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

CREATE TABLE projects (
  project_id integer NOT NULL
      DEFAULT nextval('project_id_seq')
      PRIMARY KEY,
  project_name varchar(255) UNIQUE,
  date_created timestamp without time zone NOT NULL DEFAULT now()
);

CREATE TYPE hipchat_settings AS ENUM ('off', 'quiet', 'all');

CREATE TABLE environments (
  environment_id integer NOT NULL
      DEFAULT nextval('environment_id_seq')
      PRIMARY KEY,
  environment_name varchar(255) UNIQUE,
  hipchat_mode hipchat_settings,
  date_created timestamp without time zone NOT NULL DEFAULT now()
);

CREATE TABLE release_candidates (
  release_candidate_id integer NOT NULL
      DEFAULT nextval('release_candidate_id_seq')
      PRIMARY KEY,
  date_created timestamp without time zone NOT NULL DEFAULT now(),
  project_id integer NOT NULL REFERENCES projects (project_id),
  branch_name varchar(255) NOT NULL,
  revision_id varchar(255) NOT NULL,
  code_tarball_location text NOT NULL,
  venv_tarball_location text NOT NULL
);

CREATE TABLE deploys (
  deploy_id integer NOT NULL
      DEFAULT nextval('deploy_id_seq')
      PRIMARY KEY,
  deploy_date timestamp without time zone NOT NULL DEFAULT now(),
  release_candidate_id integer NOT NULL
      REFERENCES release_candidates (release_candidate_id),
  environment_id integer NOT NULL REFERENCES environments (environment_id),
  deploying_user varchar(256)
);
