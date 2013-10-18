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

CREATE SEQUENCE chef_role_id_seq
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
  deploy_target_dir text,
  venv_target_dir text,
  pre_activate_hook text,
  post_activate_hook text,
  date_created timestamp without time zone NOT NULL DEFAULT now()
);
CREATE INDEX project_date_created_idx ON projects (date_created);

CREATE TYPE hipchat_settings AS ENUM ('off', 'quiet', 'all');

CREATE TABLE environments (
  environment_id integer NOT NULL
      DEFAULT nextval('environment_id_seq')
      PRIMARY KEY,
  environment_name varchar(255) UNIQUE,
  hipchat_mode hipchat_settings,
  date_created timestamp without time zone NOT NULL DEFAULT now()
);
CREATE INDEX environment_date_created_idx ON environments (date_created);

CREATE TABLE release_candidates (
  release_candidate_id integer NOT NULL
      DEFAULT nextval('release_candidate_id_seq')
      PRIMARY KEY,
  date_created timestamp without time zone NOT NULL DEFAULT now(),
  project_id integer NOT NULL REFERENCES projects (project_id),
  branch_name varchar(255) NOT NULL,
  revision_id varchar(255) NOT NULL,
  code_tarball_location text NOT NULL,
  venv_tarball_location text NOT NULL,
  CONSTRAINT release_candidate_project_reviesion_key UNIQUE (project_id, revision_id)
);
CREATE INDEX release_candidate_date_created_idx ON release_candidates (date_created);

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

CREATE TABLE chef_roles (
  chef_role_id integer NOT NULL
      DEFAULT nextval('environment_id_seq')
      PRIMARY KEY,
  chef_role_name varchar(255) UNIQUE,
  serial_deploy boolean,
  date_created timestamp without time zone NOT NULL DEFAULT now()
);
CREATE INDEX chef_roles_date_created_idx ON chef_roles (date_created);

CREATE TABLE chef_roles_xref_projects (
  project_id integer NOT NULL REFERENCES projects (project_id),
  chef_role_id integer NOT NULL REFERENCES chef_roles (chef_role_id),
  CONSTRAINT chef_role_xref_project_pkey PRIMARY KEY (project_id, chef_role_id)
)
