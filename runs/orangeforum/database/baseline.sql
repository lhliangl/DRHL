--
-- PostgreSQL database dump
--

\restrict aLRBlorpr56ZwIofNynjwslYANStThKfVuGwnMGjUgvfpxkpP1Wi5YQumhYdEGW

-- Dumped from database version 14.19
-- Dumped by pg_dump version 14.19

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

ALTER TABLE IF EXISTS ONLY public.users DROP CONSTRAINT IF EXISTS users_domain_id_fkey;
ALTER TABLE IF EXISTS ONLY public.topics DROP CONSTRAINT IF EXISTS topics_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.topics DROP CONSTRAINT IF EXISTS topics_category_id_fkey;
ALTER TABLE IF EXISTS ONLY public.topic_subs DROP CONSTRAINT IF EXISTS topic_subs_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.topic_subs DROP CONSTRAINT IF EXISTS topic_subs_topic_id_fkey;
ALTER TABLE IF EXISTS ONLY public.notes DROP CONSTRAINT IF EXISTS notes_domain_id_fkey;
ALTER TABLE IF EXISTS ONLY public.comments DROP CONSTRAINT IF EXISTS comments_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.comments DROP CONSTRAINT IF EXISTS comments_topic_id_fkey;
ALTER TABLE IF EXISTS ONLY public.category_subs DROP CONSTRAINT IF EXISTS category_subs_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.category_subs DROP CONSTRAINT IF EXISTS category_subs_category_id_fkey;
ALTER TABLE IF EXISTS ONLY public.categories DROP CONSTRAINT IF EXISTS categories_domain_id_fkey;
DROP TRIGGER IF EXISTS update_timestamp ON public.users;
DROP TRIGGER IF EXISTS update_timestamp ON public.topics;
DROP TRIGGER IF EXISTS update_timestamp ON public.notes;
DROP TRIGGER IF EXISTS update_timestamp ON public.domains;
DROP TRIGGER IF EXISTS update_timestamp ON public.comments;
DROP TRIGGER IF EXISTS update_timestamp ON public.categories;
DROP INDEX IF EXISTS public.users_supermod_index;
DROP INDEX IF EXISTS public.users_reset_token_index;
DROP INDEX IF EXISTS public.users_otp_token_index;
DROP INDEX IF EXISTS public.users_domain_email_index;
DROP INDEX IF EXISTS public.users_created_index;
DROP INDEX IF EXISTS public.topicsubs_unsub_token_index;
DROP INDEX IF EXISTS public.topicsubs_cat_index;
DROP INDEX IF EXISTS public.topics_category_sticky_activity_index;
DROP INDEX IF EXISTS public.notes_domain_url_index;
DROP INDEX IF EXISTS public.domains_domain_index;
DROP INDEX IF EXISTS public.comments_topic_sticky_created_index;
DROP INDEX IF EXISTS public.catsubs_unsub_token_index;
DROP INDEX IF EXISTS public.catsubs_cat_index;
DROP INDEX IF EXISTS public.categories_domain_index;
ALTER TABLE IF EXISTS ONLY public.users DROP CONSTRAINT IF EXISTS users_pkey;
ALTER TABLE IF EXISTS ONLY public.topics DROP CONSTRAINT IF EXISTS topics_pkey;
ALTER TABLE IF EXISTS ONLY public.topic_subs DROP CONSTRAINT IF EXISTS topic_subs_pkey;
ALTER TABLE IF EXISTS ONLY public.notes DROP CONSTRAINT IF EXISTS notes_pkey;
ALTER TABLE IF EXISTS ONLY public.domains DROP CONSTRAINT IF EXISTS domains_pkey;
ALTER TABLE IF EXISTS ONLY public.domains DROP CONSTRAINT IF EXISTS domains_domain_name_key;
ALTER TABLE IF EXISTS ONLY public.configs DROP CONSTRAINT IF EXISTS configs_pkey;
ALTER TABLE IF EXISTS ONLY public.comments DROP CONSTRAINT IF EXISTS comments_pkey;
ALTER TABLE IF EXISTS ONLY public.category_subs DROP CONSTRAINT IF EXISTS category_subs_pkey;
ALTER TABLE IF EXISTS ONLY public.categories DROP CONSTRAINT IF EXISTS categories_pkey;
ALTER TABLE IF EXISTS public.users ALTER COLUMN user_id DROP DEFAULT;
ALTER TABLE IF EXISTS public.topics ALTER COLUMN topic_id DROP DEFAULT;
ALTER TABLE IF EXISTS public.topic_subs ALTER COLUMN sub_id DROP DEFAULT;
ALTER TABLE IF EXISTS public.notes ALTER COLUMN note_id DROP DEFAULT;
ALTER TABLE IF EXISTS public.domains ALTER COLUMN domain_id DROP DEFAULT;
ALTER TABLE IF EXISTS public.comments ALTER COLUMN comment_id DROP DEFAULT;
ALTER TABLE IF EXISTS public.category_subs ALTER COLUMN sub_id DROP DEFAULT;
ALTER TABLE IF EXISTS public.categories ALTER COLUMN category_id DROP DEFAULT;
DROP SEQUENCE IF EXISTS public.users_user_id_seq;
DROP TABLE IF EXISTS public.users;
DROP SEQUENCE IF EXISTS public.topics_topic_id_seq;
DROP TABLE IF EXISTS public.topics;
DROP SEQUENCE IF EXISTS public.topic_subs_sub_id_seq;
DROP TABLE IF EXISTS public.topic_subs;
DROP SEQUENCE IF EXISTS public.notes_note_id_seq;
DROP TABLE IF EXISTS public.notes;
DROP SEQUENCE IF EXISTS public.domains_domain_id_seq;
DROP TABLE IF EXISTS public.domains;
DROP TABLE IF EXISTS public.configs;
DROP SEQUENCE IF EXISTS public.comments_comment_id_seq;
DROP TABLE IF EXISTS public.comments;
DROP SEQUENCE IF EXISTS public.category_subs_sub_id_seq;
DROP TABLE IF EXISTS public.category_subs;
DROP SEQUENCE IF EXISTS public.categories_category_id_seq;
DROP TABLE IF EXISTS public.categories;
DROP FUNCTION IF EXISTS public.update_modified_timestamp();
--
-- Name: update_modified_timestamp(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.update_modified_timestamp() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
		BEGIN
			new.updated_at := current_timestamp;
			RETURN new;
		END;
		$$;


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: categories; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.categories (
    category_id integer NOT NULL,
    domain_id integer NOT NULL,
    name character varying(250) NOT NULL,
    description character varying(250) NOT NULL,
    header_msg text DEFAULT ''::text NOT NULL,
    num_topics integer DEFAULT 0 NOT NULL,
    is_private boolean DEFAULT false NOT NULL,
    is_readonly boolean DEFAULT false NOT NULL,
    is_restricted boolean DEFAULT false NOT NULL,
    archived_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: categories_category_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.categories_category_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: categories_category_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.categories_category_id_seq OWNED BY public.categories.category_id;


--
-- Name: category_subs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.category_subs (
    sub_id integer NOT NULL,
    category_id integer NOT NULL,
    user_id integer NOT NULL,
    unsub_token character varying(64) DEFAULT ''::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: category_subs_sub_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.category_subs_sub_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: category_subs_sub_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.category_subs_sub_id_seq OWNED BY public.category_subs.sub_id;


--
-- Name: comments; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.comments (
    comment_id integer NOT NULL,
    topic_id integer NOT NULL,
    user_id integer NOT NULL,
    content text DEFAULT ''::text NOT NULL,
    is_sticky boolean DEFAULT false NOT NULL,
    archived_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: comments_comment_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.comments_comment_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: comments_comment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.comments_comment_id_seq OWNED BY public.comments.comment_id;


--
-- Name: configs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.configs (
    name character varying(250) NOT NULL,
    val character varying(250) DEFAULT ''::character varying NOT NULL
);


--
-- Name: domains; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.domains (
    domain_id integer NOT NULL,
    domain_name character varying(250) NOT NULL,
    forum_name character varying(250) DEFAULT 'Orange Forum'::character varying NOT NULL,
    no_regular_signup_msg character varying(250) DEFAULT ''::character varying NOT NULL,
    signup_token character varying(250) DEFAULT ''::character varying NOT NULL,
    edit_window integer DEFAULT 20,
    auto_topic_close_days integer DEFAULT 60,
    user_activity_window integer DEFAULT 3,
    max_num_activity integer DEFAULT 20,
    header_msg text DEFAULT ''::text NOT NULL,
    logo text DEFAULT ''::text NOT NULL,
    icon text DEFAULT ''::text NOT NULL,
    smtp_host character varying(250) DEFAULT ''::character varying NOT NULL,
    smtp_port integer DEFAULT 25 NOT NULL,
    smtp_user character varying(250) DEFAULT ''::character varying NOT NULL,
    smtp_pass character varying(1000) DEFAULT ''::character varying NOT NULL,
    default_from_email character varying(250) DEFAULT ''::character varying NOT NULL,
    is_regular_signup_enabled boolean DEFAULT false NOT NULL,
    is_readonly boolean DEFAULT false NOT NULL,
    enable_group_sub boolean DEFAULT false NOT NULL,
    enable_topic_autosub boolean DEFAULT false NOT NULL,
    enable_comment_autosub boolean DEFAULT false NOT NULL,
    archived_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    is_private boolean DEFAULT false NOT NULL,
    is_regular_signin_enabled boolean DEFAULT true NOT NULL,
    is_auto_user_creation_on_email_signin_enabled boolean DEFAULT false NOT NULL,
    whitelisted_email_domains character varying(250) DEFAULT ''::character varying NOT NULL
);


--
-- Name: domains_domain_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.domains_domain_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: domains_domain_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.domains_domain_id_seq OWNED BY public.domains.domain_id;


--
-- Name: notes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.notes (
    note_id integer NOT NULL,
    domain_id integer NOT NULL,
    name character varying(64) DEFAULT ''::character varying NOT NULL,
    content text DEFAULT ''::text NOT NULL,
    url character varying(64) DEFAULT ''::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: notes_note_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.notes_note_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: notes_note_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.notes_note_id_seq OWNED BY public.notes.note_id;


--
-- Name: topic_subs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.topic_subs (
    sub_id integer NOT NULL,
    topic_id integer NOT NULL,
    user_id integer NOT NULL,
    unsub_token character varying(64) DEFAULT ''::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: topic_subs_sub_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.topic_subs_sub_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: topic_subs_sub_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.topic_subs_sub_id_seq OWNED BY public.topic_subs.sub_id;


--
-- Name: topics; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.topics (
    topic_id integer NOT NULL,
    category_id integer NOT NULL,
    user_id integer NOT NULL,
    title character varying(250) NOT NULL,
    content text DEFAULT ''::text NOT NULL,
    is_sticky boolean DEFAULT false NOT NULL,
    is_readonly boolean DEFAULT false NOT NULL,
    num_comments integer DEFAULT 0 NOT NULL,
    num_views integer DEFAULT 0 NOT NULL,
    activity_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    archived_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: topics_topic_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.topics_topic_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: topics_topic_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.topics_topic_id_seq OWNED BY public.topics.topic_id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    user_id integer NOT NULL,
    domain_id integer NOT NULL,
    email character varying(250) NOT NULL,
    display_name character varying(32) NOT NULL,
    passwd_hash character varying(250) NOT NULL,
    about text DEFAULT ''::text NOT NULL,
    is_superadmin boolean DEFAULT false NOT NULL,
    is_supermod boolean DEFAULT false NOT NULL,
    is_topic_autosubscribe boolean DEFAULT true NOT NULL,
    is_comment_autosubscribe boolean DEFAULT true NOT NULL,
    is_email_notifications_disabled boolean DEFAULT false NOT NULL,
    num_topics integer DEFAULT 0 NOT NULL,
    num_comments integer DEFAULT 0 NOT NULL,
    num_activity integer DEFAULT 0 NOT NULL,
    onetime_login_token character varying(250) DEFAULT ''::character varying NOT NULL,
    onetime_login_token_at timestamp with time zone DEFAULT to_timestamp((0)::double precision) NOT NULL,
    reset_token character varying(250) DEFAULT ''::character varying NOT NULL,
    last_ip character varying(50) DEFAULT ''::character varying NOT NULL,
    activity_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    reset_at timestamp with time zone DEFAULT to_timestamp((0)::double precision) NOT NULL,
    logout_at timestamp with time zone DEFAULT to_timestamp((0)::double precision) NOT NULL,
    banned_at timestamp with time zone,
    archived_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: users_user_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.users_user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: users_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.users_user_id_seq OWNED BY public.users.user_id;


--
-- Name: categories category_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.categories ALTER COLUMN category_id SET DEFAULT nextval('public.categories_category_id_seq'::regclass);


--
-- Name: category_subs sub_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.category_subs ALTER COLUMN sub_id SET DEFAULT nextval('public.category_subs_sub_id_seq'::regclass);


--
-- Name: comments comment_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comments ALTER COLUMN comment_id SET DEFAULT nextval('public.comments_comment_id_seq'::regclass);


--
-- Name: domains domain_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.domains ALTER COLUMN domain_id SET DEFAULT nextval('public.domains_domain_id_seq'::regclass);


--
-- Name: notes note_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notes ALTER COLUMN note_id SET DEFAULT nextval('public.notes_note_id_seq'::regclass);


--
-- Name: topic_subs sub_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.topic_subs ALTER COLUMN sub_id SET DEFAULT nextval('public.topic_subs_sub_id_seq'::regclass);


--
-- Name: topics topic_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.topics ALTER COLUMN topic_id SET DEFAULT nextval('public.topics_topic_id_seq'::regclass);


--
-- Name: users user_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users ALTER COLUMN user_id SET DEFAULT nextval('public.users_user_id_seq'::regclass);


--
-- Data for Name: categories; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.categories (category_id, domain_id, name, description, header_msg, num_topics, is_private, is_readonly, is_restricted, archived_at, created_at, updated_at) FROM stdin;
5	1	8Mt6Nh	THvedY		4	f	f	f	\N	2025-10-24 15:10:52.679695+08	2025-12-02 20:11:57.349146+08
1	1	adw	awd		7	f	f	f	\N	2025-10-23 21:28:06.069277+08	2025-12-02 20:12:00.11367+08
6	1	Hue2fI	QyiX9K		1	f	f	f	\N	2025-10-31 19:21:10.316846+08	2025-12-02 20:12:02.837786+08
4	1	sad	sad		6	f	f	f	\N	2025-10-24 10:47:03.623986+08	2025-12-02 20:12:05.594674+08
2	1	sss	sss		7	f	f	f	\N	2025-10-23 21:30:02.000973+08	2025-12-02 20:12:08.313753+08
7	1	ovDx2R	DhCXPG		0	f	f	f	\N	2025-12-02 20:12:14.029388+08	2025-12-02 20:12:14.029388+08
3	1	wqe	wqe		7	f	f	f	\N	2025-10-24 10:46:58.211662+08	2025-12-02 20:12:21.217552+08
\.


--
-- Data for Name: category_subs; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.category_subs (sub_id, category_id, user_id, unsub_token, created_at) FROM stdin;
\.


--
-- Data for Name: comments; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.comments (comment_id, topic_id, user_id, content, is_sticky, archived_at, created_at, updated_at) FROM stdin;
76	14	1	> IyshoTn6F8wMZCvYhLtq	t	\N	2025-10-31 19:32:30.878176+08	2025-10-31 19:32:30.878176+08
77	24	1	> xYfCGmUSOtE	t	\N	2025-10-31 19:32:49.247356+08	2025-10-31 19:32:49.247356+08
78	24	1	rEOLvo18i4	t	\N	2025-10-31 19:32:53.99309+08	2025-10-31 19:32:53.99309+08
34	9	3	> t4krXAMuCHzRg8EoPxvkDqSAcE6uNM	t	\N	2025-10-24 14:48:53.550121+08	2025-10-31 19:33:10.280992+08
25	9	2	t4krXAMuCHmC9N3dp24G	t	\N	2025-10-24 11:15:12.659756+08	2025-10-31 19:33:15.01259+08
79	9	1	rYMXxcHPzsxj5gPKdcbZ	t	\N	2025-10-31 19:33:05.51836+08	2025-10-31 19:33:23.87114+08
35	9	3	3LKnBtmWsG7TKC3yfAX2	t	\N	2025-10-24 14:48:58.642679+08	2025-10-31 19:33:30.715484+08
24	9	2	> UoD4WMzh7tqJO2SaEo9WtOsS8pU3TB	t	\N	2025-10-24 11:15:07.914018+08	2025-10-31 19:33:35.478477+08
80	25	1	JAvshRNxGj	t	\N	2025-10-31 19:34:04.322898+08	2025-10-31 19:34:04.322898+08
1	1	3	我被修改了hha63F4PtliZJXR5b3mZjHD	t	\N	2025-10-23 21:33:52.696611+08	2025-10-31 19:32:24.066411+08
81	25	1	> awdnlekZpDqHb	t	\N	2025-10-31 19:34:09.053357+08	2025-10-31 19:34:09.053357+08
73	23	1	adwwxTWHu5v2n	t	\N	2025-10-30 20:27:18.12926+08	2025-10-31 19:34:25.440246+08
74	23	1	awdadwfNFynqPGL1	t	\N	2025-10-31 10:30:06.544548+08	2025-10-31 19:34:30.636753+08
82	23	1	Obwuj1XvhU5zg1GFYyn4	t	\N	2025-10-31 19:34:35.365895+08	2025-10-31 19:34:44.226523+08
83	23	1	> awdadwfNFynqPGL1CBznkxqlwU	t	\N	2025-10-31 19:34:53.152542+08	2025-10-31 19:34:53.152542+08
72	23	1	adwuWAUOV9ncj	t	\N	2025-10-30 16:19:08.066809+08	2025-10-31 19:35:02.596443+08
68	17	1	> w2Gskiz8U5supB1lj0DHAd4KcuVCIbl29DCq0ipo	t	\N	2025-10-24 15:20:02.951497+08	2025-12-02 20:12:35.004935+08
22	1	2	JmSKTHqxQUYe4D6imk8ZLOJEPZkNS7	t	\N	2025-10-24 11:14:40.68398+08	2025-10-31 19:32:05.663691+08
19	3	2	jT0oEgkstHRqzAk1Dn9vOHL69qQcsu	t	\N	2025-10-24 11:14:01.2332+08	2025-10-31 19:28:03.682616+08
5	4	4	mt52wN0kxMD2CP9wicIBJxQSf8sH0Y	t	\N	2025-10-24 10:48:54.191334+08	2025-10-31 19:26:01.659712+08
50	13	3	f4Uh07rkX949ByhoDC5MqKy3htcP40	t	\N	2025-10-24 14:51:54.076421+08	2025-10-31 19:24:52.994785+08
70	12	2	ee0k8UEyeBmp	t	\N	2025-10-25 21:21:02.734346+08	2025-10-31 19:29:54.780304+08
65	13	1	bJqjSMc2TEs8HEoLB6z1kijsw7KQWy	t	\N	2025-10-24 15:19:16.198546+08	2025-10-31 19:25:04.535726+08
46	8	3	ztrSoA62HYskizhD5QS1g1l96becRz	t	\N	2025-10-24 14:50:58.853581+08	2025-10-31 19:28:53.427609+08
42	11	3	B8qUZEbFIC3LQZufxSRPb0uhsZjAi4	t	\N	2025-10-24 14:50:10.875441+08	2025-10-31 19:29:02.304191+08
45	5	3	> adwUnI1zx5TyqYf831drpCtkrasnxqTDL	t	\N	2025-10-24 14:50:44.866832+08	2025-10-31 19:26:16.731014+08
53	4	3	> NboF4PrjivoJgInD46yTjNyOraFsMfkUVKTXzsw3	t	\N	2025-10-24 14:52:31.585277+08	2025-10-31 19:25:13.396119+08
26	4	2	NboF4Prjivkscw1MpzjJgMDA25PxB1	t	\N	2025-10-24 11:15:25.916932+08	2025-10-31 19:25:18.108675+08
9	5	4	ktZGU7cRYwmbZRMfs8ng6yTLe3wOXN	t	\N	2025-10-24 10:49:24.646706+08	2025-10-31 19:26:21.444924+08
27	4	2	> wwww6EYFpUSJLbAHDn1LEgIjpFuofEGHiB	t	\N	2025-10-24 11:15:30.863766+08	2025-10-31 19:25:24.93743+08
33	1	3	> hahaZzPLpfs4G3XudTaD905x4lYiUnMArE	t	\N	2025-10-24 14:48:42.316437+08	2025-10-31 19:31:13.020619+08
23	1	2	> NT89d7reXjfnzaC3ImKjm4XEMOFuBtcs29Iqfeah	t	\N	2025-10-24 11:14:58.767525+08	2025-10-31 19:31:22.47954+08
29	7	2	> K9yD6TRLFla7UnFHX0DilDNw4jgmCIQMxfYW0REq	t	\N	2025-10-24 11:15:47.398792+08	2025-10-31 19:23:26.761758+08
63	7	1	rAP23yXEbW9KuqQwN075Tt9z287jZw	t	\N	2025-10-24 15:18:16.199451+08	2025-10-31 19:23:31.47449+08
64	7	1	> RAtjK0i87MmKbuLPQ9ZxaXo0y1n4jxYH6d7a2ZSq	t	\N	2025-10-24 15:18:36.849732+08	2025-10-31 19:23:36.186864+08
20	2	2	FE4uKtXCljyURNxk90XP	t	\N	2025-10-24 11:14:20.032645+08	2025-10-31 19:30:51.9701+08
21	2	2	> sssjAorV9qP0Xf0e4Nj9HGh	t	\N	2025-10-24 11:14:24.795385+08	2025-10-31 19:30:56.682911+08
54	7	3	tbMuyc1sZiHt60DPCJrs7hOuE86AWr	t	\N	2025-10-24 14:52:38.681522+08	2025-10-31 19:23:49.843257+08
55	7	3	> K9yD6TRLFl6vLKElZF5HJ1wspR0DO3B4iPfunosg	t	\N	2025-10-24 14:52:52.9194+08	2025-10-31 19:24:03.466231+08
37	12	3	> 5jZneRxVr2CYGUtsmXZ8OGfe9HUaPL	t	\N	2025-10-24 14:49:11.022642+08	2025-10-31 19:30:11.102134+08
60	16	1	nc5rQIFA4RJPk1qin6fh	t	\N	2025-10-24 15:16:39.758464+08	2025-10-31 19:27:11.140637+08
56	15	1	C5BjL16UzHhrHF1A4eTo	t	\N	2025-10-24 15:11:02.880907+08	2025-10-31 19:21:49.352775+08
41	10	3	> diwDufv0qX5M8DfWjZTwOzCTEDIdAW1SwNkUIxZ2	t	\N	2025-10-24 14:49:56.94994+08	2025-10-31 19:22:00.87669+08
40	10	3	A5S1y2680Z7GMVySpc5NRLixnfokIp	t	\N	2025-10-24 14:49:52.087636+08	2025-10-31 19:22:07.738692+08
13	6	2	> sadE0h6to9DVUzTA3KnRsHCvb4W5NXUxa	t	\N	2025-10-24 11:12:41.494677+08	2025-10-31 19:22:28.222518+08
38	6	3	MeCTPbAxONzmStFM1X6sMiWLwtm6V0	t	\N	2025-10-24 14:49:24.160441+08	2025-10-31 19:22:32.985272+08
39	6	3	> > sadE0h6to9DVU48ro1xtWKEWJEkGpjlcZUOmkKuSv4t	t	\N	2025-10-24 14:49:28.939922+08	2025-10-31 19:22:41.895081+08
28	7	2	RAtjK0i87MclnECj3MB9qLptPQuoBj	t	\N	2025-10-24 11:15:42.651286+08	2025-10-31 19:24:10.244242+08
12	6	2	r1kNPHilpZ46pFhIytiLGNVLpuqP8m	t	\N	2025-10-24 11:12:34.599392+08	2025-10-31 19:22:46.607874+08
67	17	1	iXTMEc48Fh8lZTOBqfXh	t	\N	2025-10-24 15:19:58.170493+08	2025-10-31 19:24:30.545471+08
66	13	1	> 8Ez4dKyHDpObLjBIs5GQsriSLQD40W78eYLBHvPu	t	\N	2025-10-24 15:19:20.983769+08	2025-10-31 19:24:39.422146+08
51	13	3	> 8Ez4dKyHDpPkGstgzpdlEL0sTBi2kaQ14LMklKUB	t	\N	2025-10-24 14:51:59.272585+08	2025-10-31 19:24:48.282307+08
62	4	1	> JeOZBgyLxutYrl8J2KhfqBk3d2PxTSx9yTcFCMnAJYVBSsocut	t	\N	2025-10-24 15:17:52.801911+08	2025-10-31 19:25:31.732014+08
61	4	1	nxRjwrvMTiMHua7C1irscXfIn7gGqw	t	\N	2025-10-24 15:17:29.434792+08	2025-10-31 19:25:36.462144+08
52	4	3	JeOZBgyLxutYrl8J2KhflgcWHEnSek	t	\N	2025-10-24 14:52:11.197072+08	2025-10-31 19:25:43.273567+08
4	4	4	> wwwwzA1GYkwjXq7EyGPTLJQfMkmlXOGHsF	t	\N	2025-10-24 10:48:49.123968+08	2025-10-31 19:25:56.928848+08
15	5	2	> adwu7yrsBGkWgoUK806BLhaOqTGDy06woodEhlBO1Is	t	\N	2025-10-24 11:13:13.334525+08	2025-10-31 19:26:26.140584+08
8	5	4	> adw3fBd5YmD4uek0ZD9VXQPaBtCoJs7uD	t	\N	2025-10-24 10:49:19.537196+08	2025-10-31 19:26:37.049437+08
44	5	3	XwS7ch2IAy7yP83sTcADSUfTYVnRZD	t	\N	2025-10-24 14:50:24.834928+08	2025-10-31 19:26:41.811893+08
14	5	2	R5V2DfWSp30bCGOV1u47j7Bb0pNCcHT18g6w5ROi	t	\N	2025-10-24 11:12:59.448156+08	2025-10-31 19:26:55.43415+08
18	3	2	> ypfEdsZ6jVLv2gmOjHdryiBdW7QbqrNfWy4a09Tx9LIntMNUAT	t	\N	2025-10-24 11:13:47.358463+08	2025-10-31 19:27:24.812341+08
48	3	3	AF7oQTzh3SnKG8JvshgFN4cx9QO0Bl	t	\N	2025-10-24 14:51:21.917162+08	2025-10-31 19:27:29.591924+08
6	3	4	> sadoMDy9k6QEZKdtOERgB3WH3izspOFWl	t	\N	2025-10-24 10:49:05.594385+08	2025-10-31 19:27:45.262702+08
49	3	3	> > ypfEdsZ6jVLv2gmOjHdryiBdW7QbqrNgMbI9Lp0XuG4BZ7IAbx8Qoc0wRVfn	t	\N	2025-10-24 14:51:44.916496+08	2025-10-31 19:27:50.009357+08
7	3	4	ypfEdsZ6jV7FaD5U1x8sCJarpVEFS4	t	\N	2025-10-24 10:49:10.47633+08	2025-10-31 19:27:56.821508+08
59	3	1	pw0HsgnQ7mH3LxhjNnYFTkWfq08xoY	t	\N	2025-10-24 15:15:46.670058+08	2025-10-31 19:28:10.511453+08
17	8	2	3XiOpmaIjEDHw7AB0uyf8mCwsEpx1j	t	\N	2025-10-24 11:13:36.284429+08	2025-10-31 19:28:19.42031+08
57	8	1	QKvOmPbWxN9N2Uc0ZhaBzdGkVZCy5S	t	\N	2025-10-24 15:12:55.683416+08	2025-10-31 19:28:24.150419+08
47	8	3	> 3XiOpmaIjEc4uClpjMQyaZq0zT6rCyPOivTCao8H	t	\N	2025-10-24 14:51:12.67493+08	2025-10-31 19:28:28.897314+08
16	8	2	> fj2MODJuKFADBYcJ4XmRbYqneFZsrOeD1pLHJgSW	t	\N	2025-10-24 11:13:31.434742+08	2025-10-31 19:28:43.934926+08
58	11	1	W5StHwQj4UCRI5wuvzsbCWYJgkpw4v	t	\N	2025-10-24 15:14:50.795184+08	2025-10-31 19:29:07.018662+08
43	11	3	> tjVZf2gePmb7hFayIKg9gHMSVUvch5DdUuxzjpX4	t	\N	2025-10-24 14:50:15.725478+08	2025-10-31 19:29:13.812278+08
36	12	3	F03uQnODjwKAvOPIW4z5	t	\N	2025-10-24 14:49:05.678669+08	2025-10-31 19:29:50.034175+08
71	12	5	jqVfCxIykz9	t	\N	2025-10-25 21:23:10.97535+08	2025-10-31 19:30:17.878861+08
75	2	1	cE8Knz7wfM	t	\N	2025-10-31 19:30:37.747612+08	2025-10-31 19:30:37.747612+08
31	2	3	AF02rdTMuSEBm6NeRO5q	t	\N	2025-10-24 14:48:01.956998+08	2025-10-31 19:30:47.207061+08
30	2	3	> FE4uKtXCljy47M0I82h6uo0Uwsh9O3XkqTQtvacN	t	\N	2025-10-24 14:47:48.053927+08	2025-10-31 19:31:06.142787+08
32	1	3	zxHIcLlfyXYhzBNr1DwisAHoKuEhpV	t	\N	2025-10-24 14:48:11.045354+08	2025-10-31 19:31:17.751032+08
3	1	1	awddPKIM27qrfa	t	\N	2025-10-24 09:56:03.971751+08	2025-10-31 19:31:33.538194+08
2	1	2	hahaZzPLpfs4G3BA8x2ueoEG	t	\N	2025-10-23 21:36:34.863257+08	2025-10-31 19:31:56.137438+08
11	1	4	> hahawJtCgE67h5BlHZVpNuyC	t	\N	2025-10-24 10:49:59.81238+08	2025-10-31 19:32:00.884254+08
10	1	4	NT89d7reXjfnzaC3ImKj2XFnftl7hJ	t	\N	2025-10-24 10:49:45.904261+08	2025-10-31 19:32:10.426969+08
\.


--
-- Data for Name: configs; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.configs (name, val) FROM stdin;
db_version	2
\.


--
-- Data for Name: domains; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.domains (domain_id, domain_name, forum_name, no_regular_signup_msg, signup_token, edit_window, auto_topic_close_days, user_activity_window, max_num_activity, header_msg, logo, icon, smtp_host, smtp_port, smtp_user, smtp_pass, default_from_email, is_regular_signup_enabled, is_readonly, enable_group_sub, enable_topic_autosub, enable_comment_autosub, archived_at, created_at, updated_at, is_private, is_regular_signin_enabled, is_auto_user_creation_on_email_signin_enabled, whitelisted_email_domains) FROM stdin;
1	localhost	Orange Forum			20	60	3	20		IFTsCbw82RxYfJ7X4UBE	jlKuze5VSMND5CSljP8z		25				t	f	f	f	f	\N	2025-10-23 21:21:09.011449+08	2025-12-02 20:11:51.820747+08	f	t	t	OTbSaF
\.


--
-- Data for Name: notes; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.notes (note_id, domain_id, name, content, url, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: topic_subs; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.topic_subs (sub_id, topic_id, user_id, unsub_token, created_at) FROM stdin;
\.


--
-- Data for Name: topics; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.topics (topic_id, category_id, user_id, title, content, is_sticky, is_readonly, num_comments, num_views, activity_at, archived_at, created_at, updated_at) FROM stdin;
24	1	1	xdhbft	x7Vw08Sjsa6	f	t	2	21	2025-10-31 19:32:53.995083+08	\N	2025-10-30 20:02:48.352583+08	2025-12-02 15:30:38.67202+08
3	2	3	gjy	sadoM4xjGaulWKgQqvntVPc	f	t	7	162	2025-10-24 15:15:46.676794+08	\N	2025-10-23 21:33:30.184064+08	2025-10-31 19:28:15.179503+08
6	4	1	sda	sadkdu1gTmR8vDeonTMwsFN	f	t	4	116	2025-10-24 14:49:28.944959+08	\N	2025-10-24 10:47:29.830772+08	2025-12-02 15:33:42.715985+08
16	2	3	EDYeZ6	o8uQWiDXkAD7jtKwTGWLSL3jUrxhAX	f	t	1	27	2025-10-24 15:16:39.764517+08	\N	2025-10-24 14:50:49.790708+08	2025-10-31 19:27:15.769403+08
29	2	1	ZNBvoT	BMPwRtCbUQ	f	t	0	1	2025-10-31 19:27:17.984346+08	\N	2025-10-31 19:27:17.984346+08	2025-10-31 19:27:17.987907+08
11	2	2	Bl0o3m	tjVZf2gePmay8kvKHCLGaxziwWkvTD	f	t	3	58	2025-10-24 15:14:50.797902+08	\N	2025-10-24 11:14:06.211271+08	2025-10-31 19:29:23.181365+08
25	5	1	awd	awdy4bPxXa7lt	f	t	2	18	2025-10-31 19:34:09.055231+08	\N	2025-10-31 16:37:54.63312+08	2025-12-02 15:34:51.706004+08
13	3	2	RNQk3x	8Ez4dKyHDpujxhgeEBdafrYB9Z53EN	f	t	4	83	2025-10-24 15:19:20.98577+08	\N	2025-10-24 11:15:35.726783+08	2025-12-02 15:28:58.989654+08
1	1	1	asd	sadk4avU0GHOu	f	t	9	220	2025-10-24 14:48:42.318518+08	\N	2025-10-23 21:30:09.734509+08	2025-12-02 15:31:49.153982+08
10	4	2	uCgnDt	diwDufv0qXEGNROBvgt01t9G3d7pJO	f	t	2	56	2025-10-24 14:49:56.957085+08	\N	2025-10-24 11:12:48.40222+08	2025-12-02 15:33:57.354492+08
20	2	1	ldMo5E	mfdocjYCXkSKhG3UBt6V	f	t	0	11	2025-10-24 15:15:25.884581+08	\N	2025-10-24 15:15:25.884581+08	2025-10-31 19:29:27.436827+08
31	5	1	LqT1J8	dfqwrX12ve	f	t	0	4	2025-10-31 19:34:18.562072+08	\N	2025-10-31 19:34:18.562072+08	2025-12-02 15:34:55.891758+08
2	1	1	sss	sssOZNq1ouQh9	f	t	5	95	2025-10-31 19:30:37.750112+08	\N	2025-10-23 21:30:43.143499+08	2025-12-02 15:32:47.641288+08
18	4	1	cdPO7b	YupsUQPSbMewWIDsvtQqyZD2tHQYzw	f	t	0	18	2025-10-24 15:09:45.721928+08	\N	2025-10-24 15:09:45.721928+08	2025-12-02 15:34:03.640654+08
21	3	1	EdHrwj	wtyBpWxmi8azGg7v0wUY	f	t	0	14	2025-10-24 15:19:05.162937+08	\N	2025-10-24 15:19:05.162937+08	2025-12-02 15:29:07.342531+08
32	3	1	1lJ3SF	AVsqynOC5M	f	t	0	1	2025-12-02 20:12:21.21598+08	\N	2025-12-02 20:12:21.21598+08	2025-12-02 20:12:21.221495+08
22	5	1	WX9ynS	LgA5vtDBJmJHXAKzd8af	f	t	0	20	2025-10-24 15:20:21.286974+08	\N	2025-10-24 15:20:21.286974+08	2025-12-02 15:34:12.002548+08
30	1	1	nBxITi	HkI8NyiB5m	f	t	0	4	2025-10-31 19:29:34.279689+08	\N	2025-10-31 19:29:34.279689+08	2025-12-02 15:32:51.801111+08
14	1	3	8ujFUS	IyshoTn6F8pmeWHOh1tk	f	t	1	18	2025-10-31 19:32:30.880392+08	\N	2025-10-24 14:47:32.725048+08	2025-12-02 15:31:57.493577+08
17	3	3	wJSvjo	w2Gskiz8U5PpUe6jLCQTsHnyYaD7hrt0JNaYFmWf	f	t	2	47	2025-10-24 15:20:02.953619+08	\N	2025-10-24 14:52:04.170429+08	2025-12-02 20:12:35.007296+08
9	1	4	ZSRHeo	UoD4WMzh7tMHp1E6y8Sn	f	t	5	89	2025-10-31 19:33:05.520207+08	\N	2025-10-24 10:49:38.983345+08	2025-12-02 15:31:06.449584+08
15	4	3	zRocn2	6BYJuqcgNEnCTAY9sQSbHB6fVqCn8o	f	t	1	30	2025-10-24 15:11:02.885065+08	\N	2025-10-24 14:50:01.826801+08	2025-12-02 15:33:13.54106+08
26	6	1	5MZco3	YoOWMtNhzQ	f	t	0	5	2025-10-31 19:21:24.104781+08	\N	2025-10-31 19:21:24.104781+08	2025-12-02 20:15:19.745884+08
8	2	4	TEsY56	fj2MODJuKF6m8eB47NtkCgW7vRSuUO	f	t	5	102	2025-10-24 15:12:55.685813+08	\N	2025-10-24 10:49:31.824641+08	2025-10-31 19:28:53.43069+08
23	5	1	asd	asdhIwq204Mtj	f	t	5	66	2025-10-31 19:34:53.152998+08	\N	2025-10-30 16:14:42.157208+08	2025-12-02 20:15:44.35613+08
27	4	1	MvpJF6	DCM4Wm7cN0	f	t	0	4	2025-10-31 19:21:31.015454+08	\N	2025-10-31 19:21:31.015454+08	2025-12-02 15:33:19.833356+08
19	4	1	6j2aVk	Hv5yujNn7DGsyBMVhYvF	f	t	0	14	2025-10-24 15:11:25.113454+08	\N	2025-10-24 15:11:25.113454+08	2025-12-02 15:33:26.108286+08
4	3	1	www	wwwwsWr1hIktpEweG3Edf49V	f	t	8	181	2025-10-24 15:17:52.803997+08	\N	2025-10-24 10:47:17.405224+08	2025-12-02 15:30:21.598655+08
5	2	1	adw	adwCqwhDAtO8IXoWbAItwDK	f	t	6	145	2025-10-24 14:50:44.869529+08	\N	2025-10-24 10:47:24.58515+08	2025-10-31 19:27:00.093463+08
28	3	1	cSOmlp	5AhFxSCoXJ	f	t	0	4	2025-10-31 19:23:11.139571+08	\N	2025-10-31 19:23:11.139571+08	2025-12-02 15:30:23.680829+08
12	1	2	ZAedWw	5jZneRxVr2jFGdHeAmzg	f	t	4	91	2025-10-25 21:23:10.978959+08	\N	2025-10-24 11:14:13.204914+08	2025-12-02 15:32:16.36471+08
7	3	4	l7GFTQ	K9yD6TRLFlNKs6ocDWJO2FLiVbjoxf	f	t	6	146	2025-10-24 15:18:36.851678+08	\N	2025-10-24 10:48:40.024656+08	2025-12-02 15:29:40.689623+08
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.users (user_id, domain_id, email, display_name, passwd_hash, about, is_superadmin, is_supermod, is_topic_autosubscribe, is_comment_autosubscribe, is_email_notifications_disabled, num_topics, num_comments, num_activity, onetime_login_token, onetime_login_token_at, reset_token, last_ip, activity_at, reset_at, logout_at, banned_at, archived_at, created_at, updated_at) FROM stdin;
2	1	user1@qq.com	User1	$2a$10$Ta4xqpjTNsXAmunoCY0xUeXQz55EBRQzLi5dWfEzZZkZ1ZKcCF2CC		f	f	t	t	f	4	20	0	eb57a609-e09d-48fa-9ab6-8fbae4132743	2025-10-24 11:16:06.334874+08			2025-10-23 21:32:08.964595+08	1970-01-01 08:00:00+08	1970-01-01 08:00:00+08	\N	\N	2025-10-23 21:32:08.964595+08	2025-10-25 21:21:02.738029+08
5	1	user3@qq.com	User3	$2a$10$vwFDD88XhNv0tICMcLprvOr7IaBMeV4MXEezH88OiM4WngwAhzjGm		f	f	t	t	f	0	1	0		1970-01-01 08:00:00+08			2025-10-25 21:18:38.415131+08	1970-01-01 08:00:00+08	1970-01-01 08:00:00+08	\N	\N	2025-10-25 21:18:38.415131+08	2025-10-25 21:23:10.980153+08
1	1	admin@qq.com	Admin	$2a$10$e/NWi6RLOqbDutfGDLia2ObSyeNXrzGqpzfMaJxKVHXjndCd70aJu		t	f	t	t	f	20	26	0	afe7085f-287c-446c-b8fd-b0d08f381e3d	2025-12-02 15:32:56.218446+08			2025-10-23 21:21:49.693555+08	1970-01-01 08:00:00+08	1970-01-01 08:00:00+08	\N	\N	2025-10-23 21:21:49.693555+08	2025-12-02 20:12:21.217795+08
4	1	4875230619@qq.com	4875230619	$2a$10$Fk0TIketHq.qZYCvk2PjjOkubqm2iTXMEDrEzRhHXHqKgjYzTTZSi		f	f	t	t	f	3	8	0		1970-01-01 08:00:00+08			2025-10-24 10:48:18.78427+08	1970-01-01 08:00:00+08	1970-01-01 08:00:00+08	\N	\N	2025-10-24 10:48:18.78427+08	2025-10-24 10:49:59.814437+08
3	1	user2@qq.com	User2	$2a$10$IwlI8nJSoRhhNJKPDzl4huGKuzwg20lQsg.l6wU7aW4xMXnMfiaLi		f	f	t	t	f	5	27	0	b4ac7143-7d91-4422-b5ce-774861b9b3d4	2025-10-24 14:53:18.84802+08			2025-10-23 21:32:44.648995+08	1970-01-01 08:00:00+08	1970-01-01 08:00:00+08	2025-10-24 15:10:30.541517+08	\N	2025-10-23 21:32:44.648995+08	2025-10-24 15:10:30.542808+08
\.


--
-- Name: categories_category_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.categories_category_id_seq', 7, true);


--
-- Name: category_subs_sub_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.category_subs_sub_id_seq', 1, false);


--
-- Name: comments_comment_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.comments_comment_id_seq', 83, true);


--
-- Name: domains_domain_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.domains_domain_id_seq', 1, true);


--
-- Name: notes_note_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.notes_note_id_seq', 1, false);


--
-- Name: topic_subs_sub_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.topic_subs_sub_id_seq', 1, false);


--
-- Name: topics_topic_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.topics_topic_id_seq', 32, true);


--
-- Name: users_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.users_user_id_seq', 5, true);


--
-- Name: categories categories_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_pkey PRIMARY KEY (category_id);


--
-- Name: category_subs category_subs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.category_subs
    ADD CONSTRAINT category_subs_pkey PRIMARY KEY (sub_id);


--
-- Name: comments comments_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comments
    ADD CONSTRAINT comments_pkey PRIMARY KEY (comment_id);


--
-- Name: configs configs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.configs
    ADD CONSTRAINT configs_pkey PRIMARY KEY (name);


--
-- Name: domains domains_domain_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.domains
    ADD CONSTRAINT domains_domain_name_key UNIQUE (domain_name);


--
-- Name: domains domains_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.domains
    ADD CONSTRAINT domains_pkey PRIMARY KEY (domain_id);


--
-- Name: notes notes_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notes
    ADD CONSTRAINT notes_pkey PRIMARY KEY (note_id);


--
-- Name: topic_subs topic_subs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.topic_subs
    ADD CONSTRAINT topic_subs_pkey PRIMARY KEY (sub_id);


--
-- Name: topics topics_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.topics
    ADD CONSTRAINT topics_pkey PRIMARY KEY (topic_id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (user_id);


--
-- Name: categories_domain_index; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX categories_domain_index ON public.categories USING btree (domain_id);


--
-- Name: catsubs_cat_index; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX catsubs_cat_index ON public.category_subs USING btree (category_id);


--
-- Name: catsubs_unsub_token_index; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX catsubs_unsub_token_index ON public.category_subs USING btree (unsub_token);


--
-- Name: comments_topic_sticky_created_index; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX comments_topic_sticky_created_index ON public.comments USING btree (topic_id, is_sticky DESC, created_at);


--
-- Name: domains_domain_index; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX domains_domain_index ON public.domains USING btree (domain_name);


--
-- Name: notes_domain_url_index; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX notes_domain_url_index ON public.notes USING btree (domain_id, url);


--
-- Name: topics_category_sticky_activity_index; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX topics_category_sticky_activity_index ON public.topics USING btree (category_id, is_sticky DESC, activity_at DESC);


--
-- Name: topicsubs_cat_index; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX topicsubs_cat_index ON public.topic_subs USING btree (topic_id);


--
-- Name: topicsubs_unsub_token_index; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX topicsubs_unsub_token_index ON public.topic_subs USING btree (unsub_token);


--
-- Name: users_created_index; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX users_created_index ON public.users USING btree (created_at);


--
-- Name: users_domain_email_index; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX users_domain_email_index ON public.users USING btree (domain_id, email);


--
-- Name: users_otp_token_index; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX users_otp_token_index ON public.users USING btree (onetime_login_token);


--
-- Name: users_reset_token_index; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX users_reset_token_index ON public.users USING btree (reset_token);


--
-- Name: users_supermod_index; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX users_supermod_index ON public.users USING btree (domain_id, is_supermod);


--
-- Name: categories update_timestamp; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER update_timestamp BEFORE UPDATE ON public.categories FOR EACH ROW EXECUTE FUNCTION public.update_modified_timestamp();


--
-- Name: comments update_timestamp; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER update_timestamp BEFORE UPDATE ON public.comments FOR EACH ROW EXECUTE FUNCTION public.update_modified_timestamp();


--
-- Name: domains update_timestamp; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER update_timestamp BEFORE UPDATE ON public.domains FOR EACH ROW EXECUTE FUNCTION public.update_modified_timestamp();


--
-- Name: notes update_timestamp; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER update_timestamp BEFORE UPDATE ON public.notes FOR EACH ROW EXECUTE FUNCTION public.update_modified_timestamp();


--
-- Name: topics update_timestamp; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER update_timestamp BEFORE UPDATE ON public.topics FOR EACH ROW EXECUTE FUNCTION public.update_modified_timestamp();


--
-- Name: users update_timestamp; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER update_timestamp BEFORE UPDATE ON public.users FOR EACH ROW EXECUTE FUNCTION public.update_modified_timestamp();


--
-- Name: categories categories_domain_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_domain_id_fkey FOREIGN KEY (domain_id) REFERENCES public.domains(domain_id) ON DELETE CASCADE;


--
-- Name: category_subs category_subs_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.category_subs
    ADD CONSTRAINT category_subs_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.categories(category_id) ON DELETE CASCADE;


--
-- Name: category_subs category_subs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.category_subs
    ADD CONSTRAINT category_subs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id) ON DELETE CASCADE;


--
-- Name: comments comments_topic_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comments
    ADD CONSTRAINT comments_topic_id_fkey FOREIGN KEY (topic_id) REFERENCES public.topics(topic_id) ON DELETE CASCADE;


--
-- Name: comments comments_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comments
    ADD CONSTRAINT comments_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id) ON DELETE CASCADE;


--
-- Name: notes notes_domain_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notes
    ADD CONSTRAINT notes_domain_id_fkey FOREIGN KEY (domain_id) REFERENCES public.domains(domain_id) ON DELETE CASCADE;


--
-- Name: topic_subs topic_subs_topic_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.topic_subs
    ADD CONSTRAINT topic_subs_topic_id_fkey FOREIGN KEY (topic_id) REFERENCES public.topics(topic_id) ON DELETE CASCADE;


--
-- Name: topic_subs topic_subs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.topic_subs
    ADD CONSTRAINT topic_subs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id) ON DELETE CASCADE;


--
-- Name: topics topics_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.topics
    ADD CONSTRAINT topics_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.categories(category_id) ON DELETE CASCADE;


--
-- Name: topics topics_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.topics
    ADD CONSTRAINT topics_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id) ON DELETE CASCADE;


--
-- Name: users users_domain_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_domain_id_fkey FOREIGN KEY (domain_id) REFERENCES public.domains(domain_id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict aLRBlorpr56ZwIofNynjwslYANStThKfVuGwnMGjUgvfpxkpP1Wi5YQumhYdEGW

