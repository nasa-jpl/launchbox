---
--- * Schema: LB Manager
--- * Migration: 0
---

---
--- Create [table]: auth
---

CREATE TABLE public.auth (
    "user_id" character varying(64) NOT NULL,
    "token" character varying(64) NOT NULL,
    "created" timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE ONLY public.auth
    ADD CONSTRAINT auth_pkey PRIMARY KEY ("token");

CREATE INDEX auth_user_id ON public.auth USING btree ("user_id");

---
--- Create [table]: deploy_services
---

CREATE TABLE public.deploy_services (
    "deploy_id" character varying(64) NOT NULL,
    "service_id" character varying(64) NOT NULL,
    "build" character varying(128) DEFAULT ''::character varying NOT NULL,
    "commit_sha" character varying(64) NOT NULL,
    "status" character varying(64) NOT NULL,
    "created" timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE ONLY public.deploy_services
    ADD CONSTRAINT deploy_services_pkey PRIMARY KEY ("deploy_id");

CREATE INDEX deploy_services_service_id ON public.deploy_services USING btree ("service_id");
CREATE INDEX deploy_services_commit_sha ON public.deploy_services USING btree ("commit_sha");
CREATE INDEX deploy_services_status ON public.deploy_services USING btree ("status");
CREATE INDEX deploy_services_created ON public.deploy_services USING btree ("created");

---
--- Create [table]: deploy_services_actions

CREATE TABLE public.deploy_services_actions (
    "action_id" character varying(64) NOT NULL,
    "container_id" character varying(64) NOT NULL,
    "deploy_id" character varying(64) NOT NULL,
    "step" character varying(64) NOT NULL,
    "text" character varying(256) NOT NULL,
    "metadata" jsonb NOT NULL,
    "status" character varying(64) NOT NULL,
    "created" timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE ONLY public.deploy_services_actions
    ADD CONSTRAINT deploy_services_actions_pkey PRIMARY KEY ("action_id");

CREATE INDEX deploy_services_actions_container_id ON public.deploy_services_actions USING btree ("container_id");
CREATE INDEX deploy_services_actions_deploy_id ON public.deploy_services_actions USING btree ("deploy_id");
CREATE INDEX deploy_services_actions_step ON public.deploy_services_actions USING btree ("step");
CREATE INDEX deploy_services_actions_created ON public.deploy_services_actions USING btree ("created");

---
--- Create [table]: deploy_sites
---

CREATE TABLE public.deploy_sites (
    "deploy_id" character varying(64) NOT NULL,
    "site_id" character varying(64) NOT NULL,
    "status" character varying(64) NOT NULL,
    "created" timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX deploy_sites_deploy_id ON public.deploy_sites USING btree ("deploy_id");
CREATE INDEX deploy_sites_site_id ON public.deploy_sites USING btree ("site_id");
CREATE INDEX deploy_sites_status ON public.deploy_sites USING btree ("status");
CREATE INDEX deploy_sites_created ON public.deploy_sites USING btree ("created");

---
--- Create [table]: deploy_sites_actions

CREATE TABLE public.deploy_sites_actions (
    "action_id" character varying(64) NOT NULL,
    "container_id" character varying(64) NOT NULL,
    "deploy_id" character varying(64) NOT NULL,
    "site_id" character varying(64) NOT NULL,
    "step" character varying(64) NOT NULL,
    "text" character varying(256) NOT NULL,
    "metadata" jsonb NOT NULL,
    "status" character varying(64) NOT NULL,
    "created" timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE ONLY public.deploy_sites_actions
    ADD CONSTRAINT deploy_sites_actions_pkey PRIMARY KEY ("action_id");

CREATE INDEX deploy_sites_actions_container_id ON public.deploy_sites_actions USING btree ("container_id");
CREATE INDEX deploy_sites_actions_deploy_id ON public.deploy_sites_actions USING btree ("deploy_id");
CREATE INDEX deploy_sites_actions_site_id ON public.deploy_sites_actions USING btree ("site_id");
CREATE INDEX deploy_sites_actions_step ON public.deploy_sites_actions USING btree ("step");
CREATE INDEX deploy_sites_actions_created ON public.deploy_sites_actions USING btree ("created");

---
--- Create [table]: events
---

CREATE TABLE public.events (
    "site_id" character varying(64) NOT NULL,
    "user_id" character varying(64) DEFAULT ''::character varying NOT NULL,
    "source" character varying(64) NOT NULL,
    "action" character varying(64) NOT NULL,
    "kind" character varying(64) NOT NULL,
    "metadata" jsonb NOT NULL,
    "timestamp" timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX events_site_id ON public.events USING btree ("site_id");
CREATE INDEX events_user_id ON public.events USING btree ("user_id");
CREATE INDEX events_kind ON public.events USING btree ("kind");
CREATE INDEX events_source ON public.events USING btree ("source");
CREATE INDEX events_timestamp ON public.events USING btree ("timestamp");

---
--- Create [table]: hostnames
---

CREATE TABLE public.hostnames (
    "site_id" character varying(64) NOT NULL,
    "name" character varying(64) NOT NULL,
    "ssl_cert" text DEFAULT ''::text NOT NULL,
    "ssl_expires" bigint DEFAULT '-1'::integer NOT NULL,
    "ssl_req_id" text DEFAULT ''::text NOT NULL,
    "primary" integer DEFAULT 0 NOT NULL
);

ALTER TABLE ONLY public.hostnames
    ADD CONSTRAINT hostnames_pkey PRIMARY KEY ("name");

CREATE INDEX hostnames_site_id ON public.hostnames USING btree ("site_id");

---
--- Create [table]: metadata
---

CREATE TABLE public.metadata (
    "schema" integer NOT NULL
);

--- Ensures only one schema row is allowed
CREATE UNIQUE INDEX metadata_schema ON public.metadata USING btree ((("schema" IS NOT NULL)));
INSERT INTO metadata("schema") VALUES(0);

---
--- Create [table]: notes
---

CREATE TABLE public.notes (
    "note_id" character varying(64) NOT NULL,
    "site_id" character varying(64) NOT NULL,
    "user_id" character varying(64) NOT NULL,
    "text" text DEFAULT ''::text NOT NULL,
    "timestamp" timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE ONLY public.notes
    ADD CONSTRAINT notes_pkey PRIMARY KEY ("note_id");

CREATE INDEX notes_site_id ON public.notes USING btree ("site_id");
CREATE INDEX notes_timestamp ON public.notes USING btree ("timestamp");

---
--- Create [table]: services
---

CREATE TABLE public.services (
    "service_id" character varying(64) NOT NULL,
    "provider_id" character varying(64) NOT NULL,
    "name" character varying(64) NOT NULL,
    "repo_url" character varying(128) NOT NULL,
    "branch" character varying(64) NOT NULL,
    "env_name" character varying(64) NOT NULL,
    "options" jsonb NOT NULL
);

ALTER TABLE ONLY public.services
    ADD CONSTRAINT services_pkey PRIMARY KEY ("service_id");

CREATE INDEX services_name ON public.services USING btree ("name");
CREATE INDEX services_repo_url ON public.services USING btree ("repo_url");

---
--- Create [table]: sites
---

CREATE TABLE public.sites (
    "site_id" character varying(64) NOT NULL,
    "service_id" character varying(64) NOT NULL,
    "name" text DEFAULT ''::text NOT NULL,
    "desc" text DEFAULT ''::text NOT NULL
);

ALTER TABLE ONLY public.sites
    ADD CONSTRAINT sites_pkey PRIMARY KEY ("site_id");

CREATE INDEX sites_service_id ON public.sites USING btree ("service_id");

---
--- Create [table]: stats
---

CREATE TABLE public.stats (
    "container_id" character varying(64) NOT NULL,
    "data" jsonb NOT NULL,
    "timestamp" timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX stats_container_id ON public.stats USING btree ("container_id");
CREATE INDEX stats_timestamp ON public.stats USING btree ("timestamp");

---
--- Create [table]: users
---

CREATE TABLE public.users (
    "user_id" character varying(64) NOT NULL,
    "provider" character varying(64) NOT NULL,
    "first_name" character varying(64) NOT NULL,
    "last_name" character varying(64) NOT NULL,
    "password" character varying(128) DEFAULT ''::character varying NOT NULL
);

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY ("user_id");
