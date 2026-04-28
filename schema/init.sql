--
-- PostgreSQL database dump
--

\restrict uTvYE3KuwXaLrgOjgkgiXWu5g7czqI42TLLG0ThqVsp6dc5Z4F3icPwJzYwd9mY

-- Dumped from database version 16.13
-- Dumped by pg_dump version 16.13

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: timescaledb; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS timescaledb WITH SCHEMA public;


--
-- Name: EXTENSION timescaledb; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION timescaledb IS 'Enables scalable inserts and complex queries for time-series data (Community Edition)';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: telemetry; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.telemetry (
    "time" timestamp with time zone NOT NULL,
    run_id integer NOT NULL,
    chamber_id integer NOT NULL,
    channel_type text NOT NULL,
    channel_id text,
    value double precision NOT NULL,
    unit text,
    quality smallint DEFAULT 0,
    phase text
);


--
-- Name: _hyper_1_2_chunk; Type: TABLE; Schema: _timescaledb_internal; Owner: -
--

CREATE TABLE _timescaledb_internal._hyper_1_2_chunk (
    CONSTRAINT constraint_2 CHECK ((("time" >= '2026-04-27 00:00:00+00'::timestamp with time zone) AND ("time" < '2026-04-28 00:00:00+00'::timestamp with time zone)))
)
INHERITS (public.telemetry);


--
-- Name: _hyper_1_3_chunk; Type: TABLE; Schema: _timescaledb_internal; Owner: -
--

CREATE TABLE _timescaledb_internal._hyper_1_3_chunk (
    CONSTRAINT constraint_3 CHECK ((("time" >= '2026-04-28 00:00:00+00'::timestamp with time zone) AND ("time" < '2026-04-29 00:00:00+00'::timestamp with time zone)))
)
INHERITS (public.telemetry);


--
-- Name: test_events; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.test_events (
    "time" timestamp with time zone NOT NULL,
    run_id integer NOT NULL,
    event_type text NOT NULL,
    severity text,
    description text NOT NULL,
    metadata jsonb,
    CONSTRAINT test_events_severity_check CHECK ((severity = ANY (ARRAY['info'::text, 'warning'::text, 'critical'::text])))
);


--
-- Name: _hyper_2_1_chunk; Type: TABLE; Schema: _timescaledb_internal; Owner: -
--

CREATE TABLE _timescaledb_internal._hyper_2_1_chunk (
    CONSTRAINT constraint_1 CHECK ((("time" >= '2026-04-23 00:00:00+00'::timestamp with time zone) AND ("time" < '2026-04-30 00:00:00+00'::timestamp with time zone)))
)
INHERITS (public.test_events);


--
-- Name: chambers; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.chambers (
    id integer NOT NULL,
    name text NOT NULL,
    chamber_type text NOT NULL,
    vendor text,
    location text,
    notes text,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: chambers_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.chambers_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: chambers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.chambers_id_seq OWNED BY public.chambers.id;


--
-- Name: test_articles; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.test_articles (
    id integer NOT NULL,
    name text NOT NULL,
    part_number text,
    revision text,
    article_type text,
    risk_tier text,
    created_at timestamp with time zone DEFAULT now(),
    CONSTRAINT test_articles_risk_tier_check CHECK ((risk_tier = ANY (ARRAY['A'::text, 'B'::text, 'C'::text])))
);


--
-- Name: test_articles_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.test_articles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: test_articles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.test_articles_id_seq OWNED BY public.test_articles.id;


--
-- Name: test_runs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.test_runs (
    id integer NOT NULL,
    run_uuid uuid DEFAULT gen_random_uuid() NOT NULL,
    chamber_id integer NOT NULL,
    article_id integer NOT NULL,
    procedure_name text NOT NULL,
    procedure_version text,
    operator text,
    test_level text,
    started_at timestamp with time zone NOT NULL,
    ended_at timestamp with time zone,
    result text,
    abort_reason text,
    notes text,
    CONSTRAINT test_runs_result_check CHECK ((result = ANY (ARRAY['running'::text, 'passed'::text, 'failed'::text, 'aborted'::text]))),
    CONSTRAINT test_runs_test_level_check CHECK ((test_level = ANY (ARRAY['qual'::text, 'acceptance'::text, 'protoflight'::text])))
);


--
-- Name: test_runs_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.test_runs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: test_runs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.test_runs_id_seq OWNED BY public.test_runs.id;


--
-- Name: _hyper_1_2_chunk quality; Type: DEFAULT; Schema: _timescaledb_internal; Owner: -
--

ALTER TABLE ONLY _timescaledb_internal._hyper_1_2_chunk ALTER COLUMN quality SET DEFAULT 0;


--
-- Name: _hyper_1_3_chunk quality; Type: DEFAULT; Schema: _timescaledb_internal; Owner: -
--

ALTER TABLE ONLY _timescaledb_internal._hyper_1_3_chunk ALTER COLUMN quality SET DEFAULT 0;


--
-- Name: chambers id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.chambers ALTER COLUMN id SET DEFAULT nextval('public.chambers_id_seq'::regclass);


--
-- Name: test_articles id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.test_articles ALTER COLUMN id SET DEFAULT nextval('public.test_articles_id_seq'::regclass);


--
-- Name: test_runs id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.test_runs ALTER COLUMN id SET DEFAULT nextval('public.test_runs_id_seq'::regclass);


--
-- Name: chambers chambers_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.chambers
    ADD CONSTRAINT chambers_name_key UNIQUE (name);


--
-- Name: chambers chambers_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.chambers
    ADD CONSTRAINT chambers_pkey PRIMARY KEY (id);


--
-- Name: test_articles test_articles_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.test_articles
    ADD CONSTRAINT test_articles_pkey PRIMARY KEY (id);


--
-- Name: test_runs test_runs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.test_runs
    ADD CONSTRAINT test_runs_pkey PRIMARY KEY (id);


--
-- Name: test_runs test_runs_run_uuid_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.test_runs
    ADD CONSTRAINT test_runs_run_uuid_key UNIQUE (run_uuid);


--
-- Name: _hyper_1_2_chunk_idx_telemetry_chamber_channel; Type: INDEX; Schema: _timescaledb_internal; Owner: -
--

CREATE INDEX _hyper_1_2_chunk_idx_telemetry_chamber_channel ON _timescaledb_internal._hyper_1_2_chunk USING btree (chamber_id, channel_type, "time" DESC);


--
-- Name: _hyper_1_2_chunk_idx_telemetry_run; Type: INDEX; Schema: _timescaledb_internal; Owner: -
--

CREATE INDEX _hyper_1_2_chunk_idx_telemetry_run ON _timescaledb_internal._hyper_1_2_chunk USING btree (run_id, "time" DESC);


--
-- Name: _hyper_1_2_chunk_telemetry_time_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: -
--

CREATE INDEX _hyper_1_2_chunk_telemetry_time_idx ON _timescaledb_internal._hyper_1_2_chunk USING btree ("time" DESC);


--
-- Name: _hyper_1_3_chunk_idx_telemetry_chamber_channel; Type: INDEX; Schema: _timescaledb_internal; Owner: -
--

CREATE INDEX _hyper_1_3_chunk_idx_telemetry_chamber_channel ON _timescaledb_internal._hyper_1_3_chunk USING btree (chamber_id, channel_type, "time" DESC);


--
-- Name: _hyper_1_3_chunk_idx_telemetry_run; Type: INDEX; Schema: _timescaledb_internal; Owner: -
--

CREATE INDEX _hyper_1_3_chunk_idx_telemetry_run ON _timescaledb_internal._hyper_1_3_chunk USING btree (run_id, "time" DESC);


--
-- Name: _hyper_1_3_chunk_telemetry_time_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: -
--

CREATE INDEX _hyper_1_3_chunk_telemetry_time_idx ON _timescaledb_internal._hyper_1_3_chunk USING btree ("time" DESC);


--
-- Name: _hyper_2_1_chunk_idx_events_run; Type: INDEX; Schema: _timescaledb_internal; Owner: -
--

CREATE INDEX _hyper_2_1_chunk_idx_events_run ON _timescaledb_internal._hyper_2_1_chunk USING btree (run_id, "time" DESC);


--
-- Name: _hyper_2_1_chunk_test_events_time_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: -
--

CREATE INDEX _hyper_2_1_chunk_test_events_time_idx ON _timescaledb_internal._hyper_2_1_chunk USING btree ("time" DESC);


--
-- Name: idx_events_run; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_events_run ON public.test_events USING btree (run_id, "time" DESC);


--
-- Name: idx_telemetry_chamber_channel; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_telemetry_chamber_channel ON public.telemetry USING btree (chamber_id, channel_type, "time" DESC);


--
-- Name: idx_telemetry_run; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_telemetry_run ON public.telemetry USING btree (run_id, "time" DESC);


--
-- Name: telemetry_time_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX telemetry_time_idx ON public.telemetry USING btree ("time" DESC);


--
-- Name: test_events_time_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX test_events_time_idx ON public.test_events USING btree ("time" DESC);


--
-- Name: _hyper_2_1_chunk 1_1_test_events_run_id_fkey; Type: FK CONSTRAINT; Schema: _timescaledb_internal; Owner: -
--

ALTER TABLE ONLY _timescaledb_internal._hyper_2_1_chunk
    ADD CONSTRAINT "1_1_test_events_run_id_fkey" FOREIGN KEY (run_id) REFERENCES public.test_runs(id) ON DELETE CASCADE;


--
-- Name: _hyper_1_2_chunk 2_2_telemetry_chamber_id_fkey; Type: FK CONSTRAINT; Schema: _timescaledb_internal; Owner: -
--

ALTER TABLE ONLY _timescaledb_internal._hyper_1_2_chunk
    ADD CONSTRAINT "2_2_telemetry_chamber_id_fkey" FOREIGN KEY (chamber_id) REFERENCES public.chambers(id);


--
-- Name: _hyper_1_2_chunk 2_3_telemetry_run_id_fkey; Type: FK CONSTRAINT; Schema: _timescaledb_internal; Owner: -
--

ALTER TABLE ONLY _timescaledb_internal._hyper_1_2_chunk
    ADD CONSTRAINT "2_3_telemetry_run_id_fkey" FOREIGN KEY (run_id) REFERENCES public.test_runs(id) ON DELETE CASCADE;


--
-- Name: _hyper_1_3_chunk 3_4_telemetry_chamber_id_fkey; Type: FK CONSTRAINT; Schema: _timescaledb_internal; Owner: -
--

ALTER TABLE ONLY _timescaledb_internal._hyper_1_3_chunk
    ADD CONSTRAINT "3_4_telemetry_chamber_id_fkey" FOREIGN KEY (chamber_id) REFERENCES public.chambers(id);


--
-- Name: _hyper_1_3_chunk 3_5_telemetry_run_id_fkey; Type: FK CONSTRAINT; Schema: _timescaledb_internal; Owner: -
--

ALTER TABLE ONLY _timescaledb_internal._hyper_1_3_chunk
    ADD CONSTRAINT "3_5_telemetry_run_id_fkey" FOREIGN KEY (run_id) REFERENCES public.test_runs(id) ON DELETE CASCADE;


--
-- Name: telemetry telemetry_chamber_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.telemetry
    ADD CONSTRAINT telemetry_chamber_id_fkey FOREIGN KEY (chamber_id) REFERENCES public.chambers(id);


--
-- Name: telemetry telemetry_run_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.telemetry
    ADD CONSTRAINT telemetry_run_id_fkey FOREIGN KEY (run_id) REFERENCES public.test_runs(id) ON DELETE CASCADE;


--
-- Name: test_events test_events_run_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.test_events
    ADD CONSTRAINT test_events_run_id_fkey FOREIGN KEY (run_id) REFERENCES public.test_runs(id) ON DELETE CASCADE;


--
-- Name: test_runs test_runs_article_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.test_runs
    ADD CONSTRAINT test_runs_article_id_fkey FOREIGN KEY (article_id) REFERENCES public.test_articles(id);


--
-- Name: test_runs test_runs_chamber_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.test_runs
    ADD CONSTRAINT test_runs_chamber_id_fkey FOREIGN KEY (chamber_id) REFERENCES public.chambers(id);


--
-- PostgreSQL database dump complete
--

\unrestrict uTvYE3KuwXaLrgOjgkgiXWu5g7czqI42TLLG0ThqVsp6dc5Z4F3icPwJzYwd9mY

