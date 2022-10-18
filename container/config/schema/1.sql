---
--- * Schema: LB Plugins
--- * Migration: 1
---

---
--- Create [table]: plugins
---

CREATE TABLE public.plugins (
    "plugin_id" character varying(64) NOT NULL,
    "provider_id" character varying(64) NOT NULL,
    "name" character varying(64) NOT NULL,
    "type" character varying(64) NOT NULL,
    "repo_url" character varying(128) NOT NULL,
    "branch" character varying(64) NOT NULL,
    "version" character varying(64) NOT NULL,
    "requirements" character varying(128) NOT NULL,
    "created" timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE ONLY public.plugins
    ADD CONSTRAINT plugins_pkey PRIMARY KEY ("plugin_id");

CREATE INDEX plugins_type ON public.plugins USING btree ("type");
