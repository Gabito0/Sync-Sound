--
-- PostgreSQL database dump
--

-- Dumped from database version 14.11 (Ubuntu 14.11-0ubuntu0.22.04.1)
-- Dumped by pg_dump version 14.11 (Ubuntu 14.11-0ubuntu0.22.04.1)

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
-- Name: sync_and_sound; Type: SCHEMA; Schema: -; Owner: gabito
--

CREATE SCHEMA sync_and_sound;


ALTER SCHEMA sync_and_sound OWNER TO gabito;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: songs; Type: TABLE; Schema: public; Owner: gabito
--

CREATE TABLE public.songs (
    id integer NOT NULL,
    name text NOT NULL,
    artist text NOT NULL,
    song_id text NOT NULL,
    song_uri text NOT NULL
);


ALTER TABLE public.songs OWNER TO gabito;

--
-- Name: songs_id_seq; Type: SEQUENCE; Schema: public; Owner: gabito
--

CREATE SEQUENCE public.songs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.songs_id_seq OWNER TO gabito;

--
-- Name: songs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: gabito
--

ALTER SEQUENCE public.songs_id_seq OWNED BY public.songs.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: gabito
--

CREATE TABLE public.users (
    id integer NOT NULL,
    first_name text NOT NULL,
    last_name text NOT NULL,
    username text NOT NULL,
    email text NOT NULL,
    password text NOT NULL
);


ALTER TABLE public.users OWNER TO gabito;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: gabito
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_id_seq OWNER TO gabito;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: gabito
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: users_song; Type: TABLE; Schema: public; Owner: gabito
--

CREATE TABLE public.users_song (
    id integer NOT NULL,
    user_id integer,
    song_id integer
);


ALTER TABLE public.users_song OWNER TO gabito;

--
-- Name: users_song_id_seq; Type: SEQUENCE; Schema: public; Owner: gabito
--

CREATE SEQUENCE public.users_song_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_song_id_seq OWNER TO gabito;

--
-- Name: users_song_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: gabito
--

ALTER SEQUENCE public.users_song_id_seq OWNED BY public.users_song.id;


--
-- Name: songs id; Type: DEFAULT; Schema: public; Owner: gabito
--

ALTER TABLE ONLY public.songs ALTER COLUMN id SET DEFAULT nextval('public.songs_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: gabito
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: users_song id; Type: DEFAULT; Schema: public; Owner: gabito
--

ALTER TABLE ONLY public.users_song ALTER COLUMN id SET DEFAULT nextval('public.users_song_id_seq'::regclass);


--
-- Name: songs songs_pkey; Type: CONSTRAINT; Schema: public; Owner: gabito
--

ALTER TABLE ONLY public.songs
    ADD CONSTRAINT songs_pkey PRIMARY KEY (id);


--
-- Name: songs songs_song_id_key; Type: CONSTRAINT; Schema: public; Owner: gabito
--

ALTER TABLE ONLY public.songs
    ADD CONSTRAINT songs_song_id_key UNIQUE (song_id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: gabito
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: gabito
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users_song users_song_pkey; Type: CONSTRAINT; Schema: public; Owner: gabito
--

ALTER TABLE ONLY public.users_song
    ADD CONSTRAINT users_song_pkey PRIMARY KEY (id);


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: gabito
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: users_song users_song_song_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: gabito
--

ALTER TABLE ONLY public.users_song
    ADD CONSTRAINT users_song_song_id_fkey FOREIGN KEY (song_id) REFERENCES public.songs(id);


--
-- Name: users_song users_song_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: gabito
--

ALTER TABLE ONLY public.users_song
    ADD CONSTRAINT users_song_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- PostgreSQL database dump complete
--

