--
-- PostgreSQL database dump
--

\restrict qsCe9HObE6ELxBBRFILJvsc238gNwDSPtp93LviHorXyqh45BXOautEqWwocfKB

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

ALTER TABLE IF EXISTS ONLY public.result_takencourse DROP CONSTRAINT IF EXISTS result_takencourse_student_id_c971277a_fk_accounts_student_id;
ALTER TABLE IF EXISTS ONLY public.result_takencourse DROP CONSTRAINT IF EXISTS result_takencourse_course_id_56fd5eb6_fk_course_course_id;
ALTER TABLE IF EXISTS ONLY public.result_result DROP CONSTRAINT IF EXISTS result_result_student_id_59df1edd_fk_accounts_student_id;
ALTER TABLE IF EXISTS ONLY public.quiz_sitting DROP CONSTRAINT IF EXISTS quiz_sitting_user_id_cfb694f3_fk_accounts_user_id;
ALTER TABLE IF EXISTS ONLY public.quiz_sitting DROP CONSTRAINT IF EXISTS quiz_sitting_quiz_id_a3187627_fk;
ALTER TABLE IF EXISTS ONLY public.quiz_sitting DROP CONSTRAINT IF EXISTS quiz_sitting_course_id_72b033f6_fk_course_course_id;
ALTER TABLE IF EXISTS ONLY public.quiz_quiz DROP CONSTRAINT IF EXISTS quiz_quiz_course_id_dd25aae3_fk_course_course_id;
ALTER TABLE IF EXISTS ONLY public.quiz_question_quiz DROP CONSTRAINT IF EXISTS quiz_question_quiz_quiz_id_eccb418d_fk;
ALTER TABLE IF EXISTS ONLY public.quiz_question_quiz DROP CONSTRAINT IF EXISTS quiz_question_quiz_question_id_2b2637b3_fk;
ALTER TABLE IF EXISTS ONLY public.quiz_progress DROP CONSTRAINT IF EXISTS quiz_progress_user_id_af390dea_fk_accounts_user_id;
ALTER TABLE IF EXISTS ONLY public.quiz_mcquestion DROP CONSTRAINT IF EXISTS quiz_mcquestion_question_ptr_id_7b24b73b_fk;
ALTER TABLE IF EXISTS ONLY public.quiz_essay_question DROP CONSTRAINT IF EXISTS quiz_essay_question_question_ptr_id_448fe6c4_fk;
ALTER TABLE IF EXISTS ONLY public.quiz_choice DROP CONSTRAINT IF EXISTS quiz_choice_question_id_6297ad3f_fk_quiz_mcqu;
ALTER TABLE IF EXISTS ONLY public.payments_invoice DROP CONSTRAINT IF EXISTS payments_invoice_user_id_2f564088_fk_accounts_user_id;
ALTER TABLE IF EXISTS ONLY public.django_admin_log DROP CONSTRAINT IF EXISTS django_admin_log_user_id_c564eba6_fk_accounts_user_id;
ALTER TABLE IF EXISTS ONLY public.django_admin_log DROP CONSTRAINT IF EXISTS django_admin_log_content_type_id_c4bce8eb_fk_django_co;
ALTER TABLE IF EXISTS ONLY public.course_uploadvideo DROP CONSTRAINT IF EXISTS course_uploadvideo_course_id_0725e558_fk;
ALTER TABLE IF EXISTS ONLY public.course_upload DROP CONSTRAINT IF EXISTS course_upload_course_id_624ff4d6_fk;
ALTER TABLE IF EXISTS ONLY public.course_courseoffer DROP CONSTRAINT IF EXISTS course_courseoffer_dep_head_id_e54ea754_fk_accounts_;
ALTER TABLE IF EXISTS ONLY public.course_courseallocation DROP CONSTRAINT IF EXISTS course_courseallocation_session_id_3101be0e_fk;
ALTER TABLE IF EXISTS ONLY public.course_courseallocation DROP CONSTRAINT IF EXISTS course_courseallocation_lecturer_id_ae68368a_fk;
ALTER TABLE IF EXISTS ONLY public.course_courseallocation_courses DROP CONSTRAINT IF EXISTS course_courseallocation_courses_courseallocation_id_e203c2aa_fk;
ALTER TABLE IF EXISTS ONLY public.course_courseallocation_courses DROP CONSTRAINT IF EXISTS course_courseallocation_courses_course_id_74f75d98_fk;
ALTER TABLE IF EXISTS ONLY public.course_course DROP CONSTRAINT IF EXISTS course_course_program_id_dda9b2de_fk;
ALTER TABLE IF EXISTS ONLY public.auth_permission DROP CONSTRAINT IF EXISTS auth_permission_content_type_id_2f476e4b_fk_django_co;
ALTER TABLE IF EXISTS ONLY public.auth_group_permissions DROP CONSTRAINT IF EXISTS auth_group_permissions_group_id_b120cbf9_fk_auth_group_id;
ALTER TABLE IF EXISTS ONLY public.auth_group_permissions DROP CONSTRAINT IF EXISTS auth_group_permissio_permission_id_84c5c92e_fk_auth_perm;
ALTER TABLE IF EXISTS ONLY public.app_semester DROP CONSTRAINT IF EXISTS app_semester_session_id_74165707_fk;
ALTER TABLE IF EXISTS ONLY public.accounts_user_user_permissions DROP CONSTRAINT IF EXISTS accounts_user_user_permissions_user_id_e4f0a161_fk;
ALTER TABLE IF EXISTS ONLY public.accounts_user_user_permissions DROP CONSTRAINT IF EXISTS accounts_user_user_p_permission_id_113bb443_fk_auth_perm;
ALTER TABLE IF EXISTS ONLY public.accounts_user_groups DROP CONSTRAINT IF EXISTS accounts_user_groups_user_id_52b62117_fk;
ALTER TABLE IF EXISTS ONLY public.accounts_user_groups DROP CONSTRAINT IF EXISTS accounts_user_groups_group_id_bd11a704_fk_auth_group_id;
ALTER TABLE IF EXISTS ONLY public.accounts_student DROP CONSTRAINT IF EXISTS accounts_student_student_id_d0d56f60_fk;
ALTER TABLE IF EXISTS ONLY public.accounts_student DROP CONSTRAINT IF EXISTS accounts_student_department_id_69962b56_fk;
ALTER TABLE IF EXISTS ONLY public.accounts_parent DROP CONSTRAINT IF EXISTS accounts_parent_user_id_23ea51f7_fk;
ALTER TABLE IF EXISTS ONLY public.accounts_parent DROP CONSTRAINT IF EXISTS accounts_parent_student_id_554fb6f9_fk;
ALTER TABLE IF EXISTS ONLY public.accounts_departmenthead DROP CONSTRAINT IF EXISTS accounts_departmenthead_user_id_62937520_fk;
ALTER TABLE IF EXISTS ONLY public.accounts_departmenthead DROP CONSTRAINT IF EXISTS accounts_departmenthead_department_id_35df83b0_fk;
DROP INDEX IF EXISTS public.result_takencourse_student_id_c971277a;
DROP INDEX IF EXISTS public.result_takencourse_course_id_56fd5eb6;
DROP INDEX IF EXISTS public.result_result_student_id_59df1edd;
DROP INDEX IF EXISTS public.quiz_sitting_user_id_cfb694f3;
DROP INDEX IF EXISTS public.quiz_sitting_quiz_id_a3187627;
DROP INDEX IF EXISTS public.quiz_sitting_course_id_72b033f6;
DROP INDEX IF EXISTS public.quiz_quiz_slug_bdb6a58e_like;
DROP INDEX IF EXISTS public.quiz_quiz_course_id_dd25aae3;
DROP INDEX IF EXISTS public.quiz_question_quiz_quiz_id_eccb418d;
DROP INDEX IF EXISTS public.quiz_question_quiz_question_id_2b2637b3;
DROP INDEX IF EXISTS public.quiz_choice_question_id_6297ad3f;
DROP INDEX IF EXISTS public.payments_invoice_user_id_2f564088;
DROP INDEX IF EXISTS public.django_session_session_key_c0390e0f_like;
DROP INDEX IF EXISTS public.django_session_expire_date_a5c62663;
DROP INDEX IF EXISTS public.django_admin_log_user_id_c564eba6;
DROP INDEX IF EXISTS public.django_admin_log_content_type_id_c4bce8eb;
DROP INDEX IF EXISTS public.course_uploadvideo_slug_2b0a7fce_like;
DROP INDEX IF EXISTS public.course_uploadvideo_course_id_0725e558;
DROP INDEX IF EXISTS public.course_upload_course_id_624ff4d6;
DROP INDEX IF EXISTS public.course_program_title_76d1dbcf_like;
DROP INDEX IF EXISTS public.course_courseoffer_dep_head_id_e54ea754;
DROP INDEX IF EXISTS public.course_courseallocation_session_id_3101be0e;
DROP INDEX IF EXISTS public.course_courseallocation_lecturer_id_ae68368a;
DROP INDEX IF EXISTS public.course_courseallocation_courses_courseallocation_id_e203c2aa;
DROP INDEX IF EXISTS public.course_courseallocation_courses_course_id_74f75d98;
DROP INDEX IF EXISTS public.course_course_slug_8ca9d9ef_like;
DROP INDEX IF EXISTS public.course_course_program_id_dda9b2de;
DROP INDEX IF EXISTS public.course_course_code_9dd76455_like;
DROP INDEX IF EXISTS public.auth_permission_content_type_id_2f476e4b;
DROP INDEX IF EXISTS public.auth_group_permissions_permission_id_84c5c92e;
DROP INDEX IF EXISTS public.auth_group_permissions_group_id_b120cbf9;
DROP INDEX IF EXISTS public.auth_group_name_a6ea08ec_like;
DROP INDEX IF EXISTS public.app_session_session_7896309d_like;
DROP INDEX IF EXISTS public.app_semester_session_id_74165707;
DROP INDEX IF EXISTS public.accounts_user_username_6088629e_like;
DROP INDEX IF EXISTS public.accounts_user_user_permissions_user_id_e4f0a161;
DROP INDEX IF EXISTS public.accounts_user_user_permissions_permission_id_113bb443;
DROP INDEX IF EXISTS public.accounts_user_groups_user_id_52b62117;
DROP INDEX IF EXISTS public.accounts_user_groups_group_id_bd11a704;
DROP INDEX IF EXISTS public.accounts_student_department_id_69962b56;
DROP INDEX IF EXISTS public.accounts_dephead_department_id_a1dafd87;
ALTER TABLE IF EXISTS ONLY public.result_takencourse DROP CONSTRAINT IF EXISTS result_takencourse_pkey;
ALTER TABLE IF EXISTS ONLY public.result_result DROP CONSTRAINT IF EXISTS result_result_pkey;
ALTER TABLE IF EXISTS ONLY public.quiz_sitting DROP CONSTRAINT IF EXISTS quiz_sitting_pkey;
ALTER TABLE IF EXISTS ONLY public.quiz_quiz DROP CONSTRAINT IF EXISTS quiz_quiz_slug_key;
ALTER TABLE IF EXISTS ONLY public.quiz_quiz DROP CONSTRAINT IF EXISTS quiz_quiz_pkey;
ALTER TABLE IF EXISTS ONLY public.quiz_question_quiz DROP CONSTRAINT IF EXISTS quiz_question_quiz_question_id_quiz_id_3414207a_uniq;
ALTER TABLE IF EXISTS ONLY public.quiz_question_quiz DROP CONSTRAINT IF EXISTS quiz_question_quiz_pkey;
ALTER TABLE IF EXISTS ONLY public.quiz_question DROP CONSTRAINT IF EXISTS quiz_question_pkey;
ALTER TABLE IF EXISTS ONLY public.quiz_progress DROP CONSTRAINT IF EXISTS quiz_progress_user_id_key;
ALTER TABLE IF EXISTS ONLY public.quiz_progress DROP CONSTRAINT IF EXISTS quiz_progress_pkey;
ALTER TABLE IF EXISTS ONLY public.quiz_mcquestion DROP CONSTRAINT IF EXISTS quiz_mcquestion_pkey;
ALTER TABLE IF EXISTS ONLY public.quiz_essay_question DROP CONSTRAINT IF EXISTS quiz_essay_question_pkey;
ALTER TABLE IF EXISTS ONLY public.quiz_choice DROP CONSTRAINT IF EXISTS quiz_choice_pkey;
ALTER TABLE IF EXISTS ONLY public.payments_invoice DROP CONSTRAINT IF EXISTS payments_invoice_pkey;
ALTER TABLE IF EXISTS ONLY public.django_session DROP CONSTRAINT IF EXISTS django_session_pkey;
ALTER TABLE IF EXISTS ONLY public.django_migrations DROP CONSTRAINT IF EXISTS django_migrations_pkey;
ALTER TABLE IF EXISTS ONLY public.django_content_type DROP CONSTRAINT IF EXISTS django_content_type_pkey;
ALTER TABLE IF EXISTS ONLY public.django_content_type DROP CONSTRAINT IF EXISTS django_content_type_app_label_model_76bd3d3b_uniq;
ALTER TABLE IF EXISTS ONLY public.django_admin_log DROP CONSTRAINT IF EXISTS django_admin_log_pkey;
ALTER TABLE IF EXISTS ONLY public.course_uploadvideo DROP CONSTRAINT IF EXISTS course_uploadvideo_slug_key;
ALTER TABLE IF EXISTS ONLY public.course_uploadvideo DROP CONSTRAINT IF EXISTS course_uploadvideo_pkey;
ALTER TABLE IF EXISTS ONLY public.course_upload DROP CONSTRAINT IF EXISTS course_upload_pkey;
ALTER TABLE IF EXISTS ONLY public.course_program DROP CONSTRAINT IF EXISTS course_program_title_key;
ALTER TABLE IF EXISTS ONLY public.course_program DROP CONSTRAINT IF EXISTS course_program_pkey;
ALTER TABLE IF EXISTS ONLY public.course_courseoffer DROP CONSTRAINT IF EXISTS course_courseoffer_pkey;
ALTER TABLE IF EXISTS ONLY public.course_courseallocation DROP CONSTRAINT IF EXISTS course_courseallocation_pkey;
ALTER TABLE IF EXISTS ONLY public.course_courseallocation_courses DROP CONSTRAINT IF EXISTS course_courseallocation_courses_pkey;
ALTER TABLE IF EXISTS ONLY public.course_courseallocation_courses DROP CONSTRAINT IF EXISTS course_courseallocation__courseallocation_id_cour_fc6e91fc_uniq;
ALTER TABLE IF EXISTS ONLY public.course_course DROP CONSTRAINT IF EXISTS course_course_slug_key;
ALTER TABLE IF EXISTS ONLY public.course_course DROP CONSTRAINT IF EXISTS course_course_pkey;
ALTER TABLE IF EXISTS ONLY public.course_course DROP CONSTRAINT IF EXISTS course_course_code_key;
ALTER TABLE IF EXISTS ONLY public.auth_permission DROP CONSTRAINT IF EXISTS auth_permission_pkey;
ALTER TABLE IF EXISTS ONLY public.auth_permission DROP CONSTRAINT IF EXISTS auth_permission_content_type_id_codename_01ab375a_uniq;
ALTER TABLE IF EXISTS ONLY public.auth_group DROP CONSTRAINT IF EXISTS auth_group_pkey;
ALTER TABLE IF EXISTS ONLY public.auth_group_permissions DROP CONSTRAINT IF EXISTS auth_group_permissions_pkey;
ALTER TABLE IF EXISTS ONLY public.auth_group_permissions DROP CONSTRAINT IF EXISTS auth_group_permissions_group_id_permission_id_0cd325b0_uniq;
ALTER TABLE IF EXISTS ONLY public.auth_group DROP CONSTRAINT IF EXISTS auth_group_name_key;
ALTER TABLE IF EXISTS ONLY public.app_session DROP CONSTRAINT IF EXISTS app_session_session_key;
ALTER TABLE IF EXISTS ONLY public.app_session DROP CONSTRAINT IF EXISTS app_session_pkey;
ALTER TABLE IF EXISTS ONLY public.app_semester DROP CONSTRAINT IF EXISTS app_semester_pkey;
ALTER TABLE IF EXISTS ONLY public.app_newsandevents DROP CONSTRAINT IF EXISTS app_newsandevents_pkey;
ALTER TABLE IF EXISTS ONLY public.accounts_user DROP CONSTRAINT IF EXISTS accounts_user_username_key;
ALTER TABLE IF EXISTS ONLY public.accounts_user_user_permissions DROP CONSTRAINT IF EXISTS accounts_user_user_permissions_pkey;
ALTER TABLE IF EXISTS ONLY public.accounts_user_user_permissions DROP CONSTRAINT IF EXISTS accounts_user_user_permi_user_id_permission_id_2ab516c2_uniq;
ALTER TABLE IF EXISTS ONLY public.accounts_user DROP CONSTRAINT IF EXISTS accounts_user_pkey;
ALTER TABLE IF EXISTS ONLY public.accounts_user_groups DROP CONSTRAINT IF EXISTS accounts_user_groups_user_id_group_id_59c0b32f_uniq;
ALTER TABLE IF EXISTS ONLY public.accounts_user_groups DROP CONSTRAINT IF EXISTS accounts_user_groups_pkey;
ALTER TABLE IF EXISTS ONLY public.accounts_student DROP CONSTRAINT IF EXISTS accounts_student_student_id_key;
ALTER TABLE IF EXISTS ONLY public.accounts_student DROP CONSTRAINT IF EXISTS accounts_student_pkey;
ALTER TABLE IF EXISTS ONLY public.accounts_parent DROP CONSTRAINT IF EXISTS accounts_parent_user_id_23ea51f7_uniq;
ALTER TABLE IF EXISTS ONLY public.accounts_parent DROP CONSTRAINT IF EXISTS accounts_parent_student_id_554fb6f9_uniq;
ALTER TABLE IF EXISTS ONLY public.accounts_parent DROP CONSTRAINT IF EXISTS accounts_parent_pkey;
ALTER TABLE IF EXISTS ONLY public.accounts_departmenthead DROP CONSTRAINT IF EXISTS accounts_dephead_user_id_key;
ALTER TABLE IF EXISTS ONLY public.accounts_departmenthead DROP CONSTRAINT IF EXISTS accounts_dephead_pkey;
ALTER TABLE IF EXISTS public.result_takencourse ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.result_result ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.quiz_sitting ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.quiz_quiz ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.quiz_question_quiz ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.quiz_question ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.quiz_progress ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.quiz_choice ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.payments_invoice ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.django_migrations ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.django_content_type ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.django_admin_log ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.course_uploadvideo ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.course_upload ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.course_program ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.course_courseoffer ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.course_courseallocation_courses ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.course_courseallocation ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.course_course ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.auth_permission ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.auth_group_permissions ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.auth_group ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.app_session ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.app_semester ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.app_newsandevents ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.accounts_user_user_permissions ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.accounts_user_groups ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.accounts_user ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.accounts_student ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.accounts_parent ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.accounts_departmenthead ALTER COLUMN id DROP DEFAULT;
DROP SEQUENCE IF EXISTS public.result_takencourse_id_seq;
DROP TABLE IF EXISTS public.result_takencourse;
DROP SEQUENCE IF EXISTS public.result_result_id_seq;
DROP TABLE IF EXISTS public.result_result;
DROP SEQUENCE IF EXISTS public.quiz_sitting_id_seq;
DROP TABLE IF EXISTS public.quiz_sitting;
DROP SEQUENCE IF EXISTS public.quiz_quiz_id_seq;
DROP TABLE IF EXISTS public.quiz_quiz;
DROP SEQUENCE IF EXISTS public.quiz_question_quiz_id_seq;
DROP TABLE IF EXISTS public.quiz_question_quiz;
DROP SEQUENCE IF EXISTS public.quiz_question_id_seq;
DROP TABLE IF EXISTS public.quiz_question;
DROP SEQUENCE IF EXISTS public.quiz_progress_id_seq;
DROP TABLE IF EXISTS public.quiz_progress;
DROP TABLE IF EXISTS public.quiz_mcquestion;
DROP TABLE IF EXISTS public.quiz_essay_question;
DROP SEQUENCE IF EXISTS public.quiz_choice_id_seq;
DROP TABLE IF EXISTS public.quiz_choice;
DROP SEQUENCE IF EXISTS public.payments_invoice_id_seq;
DROP TABLE IF EXISTS public.payments_invoice;
DROP TABLE IF EXISTS public.django_session;
DROP SEQUENCE IF EXISTS public.django_migrations_id_seq;
DROP TABLE IF EXISTS public.django_migrations;
DROP SEQUENCE IF EXISTS public.django_content_type_id_seq;
DROP TABLE IF EXISTS public.django_content_type;
DROP SEQUENCE IF EXISTS public.django_admin_log_id_seq;
DROP TABLE IF EXISTS public.django_admin_log;
DROP SEQUENCE IF EXISTS public.course_uploadvideo_id_seq;
DROP TABLE IF EXISTS public.course_uploadvideo;
DROP SEQUENCE IF EXISTS public.course_upload_id_seq;
DROP TABLE IF EXISTS public.course_upload;
DROP SEQUENCE IF EXISTS public.course_program_id_seq;
DROP TABLE IF EXISTS public.course_program;
DROP SEQUENCE IF EXISTS public.course_courseoffer_id_seq;
DROP TABLE IF EXISTS public.course_courseoffer;
DROP SEQUENCE IF EXISTS public.course_courseallocation_id_seq;
DROP SEQUENCE IF EXISTS public.course_courseallocation_courses_id_seq;
DROP TABLE IF EXISTS public.course_courseallocation_courses;
DROP TABLE IF EXISTS public.course_courseallocation;
DROP SEQUENCE IF EXISTS public.course_course_id_seq;
DROP TABLE IF EXISTS public.course_course;
DROP SEQUENCE IF EXISTS public.auth_permission_id_seq;
DROP TABLE IF EXISTS public.auth_permission;
DROP SEQUENCE IF EXISTS public.auth_group_permissions_id_seq;
DROP TABLE IF EXISTS public.auth_group_permissions;
DROP SEQUENCE IF EXISTS public.auth_group_id_seq;
DROP TABLE IF EXISTS public.auth_group;
DROP SEQUENCE IF EXISTS public.app_session_id_seq;
DROP TABLE IF EXISTS public.app_session;
DROP SEQUENCE IF EXISTS public.app_semester_id_seq;
DROP TABLE IF EXISTS public.app_semester;
DROP SEQUENCE IF EXISTS public.app_newsandevents_id_seq;
DROP TABLE IF EXISTS public.app_newsandevents;
DROP SEQUENCE IF EXISTS public.accounts_user_user_permissions_id_seq;
DROP TABLE IF EXISTS public.accounts_user_user_permissions;
DROP SEQUENCE IF EXISTS public.accounts_user_id_seq;
DROP SEQUENCE IF EXISTS public.accounts_user_groups_id_seq;
DROP TABLE IF EXISTS public.accounts_user_groups;
DROP TABLE IF EXISTS public.accounts_user;
DROP SEQUENCE IF EXISTS public.accounts_student_id_seq;
DROP TABLE IF EXISTS public.accounts_student;
DROP SEQUENCE IF EXISTS public.accounts_parent_id_seq;
DROP TABLE IF EXISTS public.accounts_parent;
DROP SEQUENCE IF EXISTS public.accounts_dephead_id_seq;
DROP SEQUENCE IF EXISTS public.accounts_departmenthead_id_seq;
DROP TABLE IF EXISTS public.accounts_departmenthead;
SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: accounts_departmenthead; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.accounts_departmenthead (
    id bigint NOT NULL,
    department_id bigint,
    user_id bigint NOT NULL
);


--
-- Name: accounts_departmenthead_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.accounts_departmenthead_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: accounts_departmenthead_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.accounts_departmenthead_id_seq OWNED BY public.accounts_departmenthead.id;


--
-- Name: accounts_dephead_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.accounts_dephead_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: accounts_dephead_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.accounts_dephead_id_seq OWNED BY public.accounts_departmenthead.id;


--
-- Name: accounts_parent; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.accounts_parent (
    id bigint NOT NULL,
    relation_ship text NOT NULL,
    student_id bigint,
    user_id bigint NOT NULL,
    email character varying(254),
    first_name character varying(120) NOT NULL,
    last_name character varying(120) NOT NULL,
    phone character varying(60)
);


--
-- Name: accounts_parent_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.accounts_parent_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: accounts_parent_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.accounts_parent_id_seq OWNED BY public.accounts_parent.id;


--
-- Name: accounts_student; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.accounts_student (
    id bigint NOT NULL,
    level character varying(25),
    department_id bigint,
    student_id bigint NOT NULL
);


--
-- Name: accounts_student_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.accounts_student_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: accounts_student_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.accounts_student_id_seq OWNED BY public.accounts_student.id;


--
-- Name: accounts_user; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.accounts_user (
    id bigint NOT NULL,
    password character varying(128) NOT NULL,
    last_login timestamp with time zone,
    is_superuser boolean NOT NULL,
    username character varying(150) NOT NULL,
    first_name character varying(150) NOT NULL,
    last_name character varying(150) NOT NULL,
    is_staff boolean NOT NULL,
    is_active boolean NOT NULL,
    date_joined timestamp with time zone NOT NULL,
    is_student boolean NOT NULL,
    is_lecturer boolean NOT NULL,
    phone character varying(60),
    address character varying(60),
    picture character varying(100),
    email character varying(254),
    is_parent boolean NOT NULL,
    is_dep_head boolean NOT NULL
);


--
-- Name: accounts_user_groups; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.accounts_user_groups (
    id bigint NOT NULL,
    user_id bigint NOT NULL,
    group_id integer NOT NULL
);


--
-- Name: accounts_user_groups_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.accounts_user_groups_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: accounts_user_groups_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.accounts_user_groups_id_seq OWNED BY public.accounts_user_groups.id;


--
-- Name: accounts_user_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.accounts_user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: accounts_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.accounts_user_id_seq OWNED BY public.accounts_user.id;


--
-- Name: accounts_user_user_permissions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.accounts_user_user_permissions (
    id bigint NOT NULL,
    user_id bigint NOT NULL,
    permission_id integer NOT NULL
);


--
-- Name: accounts_user_user_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.accounts_user_user_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: accounts_user_user_permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.accounts_user_user_permissions_id_seq OWNED BY public.accounts_user_user_permissions.id;


--
-- Name: app_newsandevents; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.app_newsandevents (
    id bigint NOT NULL,
    title character varying(200),
    summary text,
    posted_as character varying(10) NOT NULL,
    updated_date timestamp with time zone,
    upload_time timestamp with time zone
);


--
-- Name: app_newsandevents_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.app_newsandevents_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: app_newsandevents_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.app_newsandevents_id_seq OWNED BY public.app_newsandevents.id;


--
-- Name: app_semester; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.app_semester (
    id bigint NOT NULL,
    semester character varying(10) NOT NULL,
    is_current_semester boolean,
    next_semester_begins date,
    session_id bigint
);


--
-- Name: app_semester_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.app_semester_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: app_semester_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.app_semester_id_seq OWNED BY public.app_semester.id;


--
-- Name: app_session; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.app_session (
    id bigint NOT NULL,
    session character varying(200) NOT NULL,
    is_current_session boolean,
    next_session_begins date
);


--
-- Name: app_session_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.app_session_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: app_session_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.app_session_id_seq OWNED BY public.app_session.id;


--
-- Name: auth_group; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.auth_group (
    id integer NOT NULL,
    name character varying(150) NOT NULL
);


--
-- Name: auth_group_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.auth_group_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: auth_group_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.auth_group_id_seq OWNED BY public.auth_group.id;


--
-- Name: auth_group_permissions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.auth_group_permissions (
    id bigint NOT NULL,
    group_id integer NOT NULL,
    permission_id integer NOT NULL
);


--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.auth_group_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.auth_group_permissions_id_seq OWNED BY public.auth_group_permissions.id;


--
-- Name: auth_permission; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.auth_permission (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    content_type_id integer NOT NULL,
    codename character varying(100) NOT NULL
);


--
-- Name: auth_permission_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.auth_permission_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: auth_permission_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.auth_permission_id_seq OWNED BY public.auth_permission.id;


--
-- Name: course_course; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.course_course (
    id bigint NOT NULL,
    slug character varying(50) NOT NULL,
    title character varying(200),
    code character varying(200),
    credit integer,
    summary text,
    level character varying(25),
    year integer NOT NULL,
    semester character varying(200) NOT NULL,
    is_elective boolean,
    program_id bigint NOT NULL
);


--
-- Name: course_course_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.course_course_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: course_course_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.course_course_id_seq OWNED BY public.course_course.id;


--
-- Name: course_courseallocation; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.course_courseallocation (
    id bigint NOT NULL,
    lecturer_id bigint NOT NULL,
    session_id bigint
);


--
-- Name: course_courseallocation_courses; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.course_courseallocation_courses (
    id bigint NOT NULL,
    courseallocation_id bigint NOT NULL,
    course_id bigint NOT NULL
);


--
-- Name: course_courseallocation_courses_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.course_courseallocation_courses_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: course_courseallocation_courses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.course_courseallocation_courses_id_seq OWNED BY public.course_courseallocation_courses.id;


--
-- Name: course_courseallocation_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.course_courseallocation_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: course_courseallocation_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.course_courseallocation_id_seq OWNED BY public.course_courseallocation.id;


--
-- Name: course_courseoffer; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.course_courseoffer (
    id bigint NOT NULL,
    dep_head_id bigint NOT NULL
);


--
-- Name: course_courseoffer_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.course_courseoffer_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: course_courseoffer_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.course_courseoffer_id_seq OWNED BY public.course_courseoffer.id;


--
-- Name: course_program; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.course_program (
    id bigint NOT NULL,
    title character varying(150) NOT NULL,
    summary text
);


--
-- Name: course_program_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.course_program_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: course_program_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.course_program_id_seq OWNED BY public.course_program.id;


--
-- Name: course_upload; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.course_upload (
    id bigint NOT NULL,
    title character varying(100) NOT NULL,
    file character varying(100) NOT NULL,
    updated_date timestamp with time zone,
    upload_time timestamp with time zone,
    course_id bigint NOT NULL
);


--
-- Name: course_upload_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.course_upload_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: course_upload_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.course_upload_id_seq OWNED BY public.course_upload.id;


--
-- Name: course_uploadvideo; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.course_uploadvideo (
    id bigint NOT NULL,
    title character varying(100) NOT NULL,
    slug character varying(50) NOT NULL,
    video character varying(100) NOT NULL,
    summary text,
    "timestamp" timestamp with time zone,
    course_id bigint NOT NULL
);


--
-- Name: course_uploadvideo_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.course_uploadvideo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: course_uploadvideo_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.course_uploadvideo_id_seq OWNED BY public.course_uploadvideo.id;


--
-- Name: django_admin_log; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.django_admin_log (
    id integer NOT NULL,
    action_time timestamp with time zone NOT NULL,
    object_id text,
    object_repr character varying(200) NOT NULL,
    action_flag smallint NOT NULL,
    change_message text NOT NULL,
    content_type_id integer,
    user_id bigint NOT NULL,
    CONSTRAINT django_admin_log_action_flag_check CHECK ((action_flag >= 0))
);


--
-- Name: django_admin_log_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.django_admin_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: django_admin_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.django_admin_log_id_seq OWNED BY public.django_admin_log.id;


--
-- Name: django_content_type; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.django_content_type (
    id integer NOT NULL,
    app_label character varying(100) NOT NULL,
    model character varying(100) NOT NULL
);


--
-- Name: django_content_type_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.django_content_type_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: django_content_type_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.django_content_type_id_seq OWNED BY public.django_content_type.id;


--
-- Name: django_migrations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.django_migrations (
    id bigint NOT NULL,
    app character varying(255) NOT NULL,
    name character varying(255) NOT NULL,
    applied timestamp with time zone NOT NULL
);


--
-- Name: django_migrations_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.django_migrations_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: django_migrations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.django_migrations_id_seq OWNED BY public.django_migrations.id;


--
-- Name: django_session; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.django_session (
    session_key character varying(40) NOT NULL,
    session_data text NOT NULL,
    expire_date timestamp with time zone NOT NULL
);


--
-- Name: payments_invoice; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.payments_invoice (
    id bigint NOT NULL,
    total double precision,
    amount double precision,
    payment_complete boolean NOT NULL,
    invoice_code character varying(200),
    user_id bigint NOT NULL
);


--
-- Name: payments_invoice_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.payments_invoice_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: payments_invoice_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.payments_invoice_id_seq OWNED BY public.payments_invoice.id;


--
-- Name: quiz_choice; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.quiz_choice (
    id bigint NOT NULL,
    choice character varying(1000) NOT NULL,
    correct boolean NOT NULL,
    question_id integer NOT NULL
);


--
-- Name: quiz_choice_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.quiz_choice_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: quiz_choice_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.quiz_choice_id_seq OWNED BY public.quiz_choice.id;


--
-- Name: quiz_essay_question; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.quiz_essay_question (
    question_ptr_id bigint NOT NULL
);


--
-- Name: quiz_mcquestion; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.quiz_mcquestion (
    question_ptr_id bigint NOT NULL,
    choice_order character varying(30)
);


--
-- Name: quiz_progress; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.quiz_progress (
    id bigint NOT NULL,
    score character varying(1024) NOT NULL,
    user_id bigint NOT NULL
);


--
-- Name: quiz_progress_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.quiz_progress_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: quiz_progress_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.quiz_progress_id_seq OWNED BY public.quiz_progress.id;


--
-- Name: quiz_question; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.quiz_question (
    id bigint NOT NULL,
    figure character varying(100),
    content character varying(1000) NOT NULL,
    explanation text NOT NULL
);


--
-- Name: quiz_question_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.quiz_question_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: quiz_question_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.quiz_question_id_seq OWNED BY public.quiz_question.id;


--
-- Name: quiz_question_quiz; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.quiz_question_quiz (
    id bigint NOT NULL,
    question_id bigint NOT NULL,
    quiz_id bigint NOT NULL
);


--
-- Name: quiz_question_quiz_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.quiz_question_quiz_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: quiz_question_quiz_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.quiz_question_quiz_id_seq OWNED BY public.quiz_question_quiz.id;


--
-- Name: quiz_quiz; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.quiz_quiz (
    id bigint NOT NULL,
    title character varying(60) NOT NULL,
    slug character varying(50) NOT NULL,
    description text NOT NULL,
    category text NOT NULL,
    random_order boolean NOT NULL,
    answers_at_end boolean NOT NULL,
    exam_paper boolean NOT NULL,
    single_attempt boolean NOT NULL,
    pass_mark smallint NOT NULL,
    draft boolean NOT NULL,
    "timestamp" timestamp with time zone NOT NULL,
    course_id bigint
);


--
-- Name: quiz_quiz_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.quiz_quiz_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: quiz_quiz_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.quiz_quiz_id_seq OWNED BY public.quiz_quiz.id;


--
-- Name: quiz_sitting; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.quiz_sitting (
    id bigint NOT NULL,
    question_order character varying(1024) NOT NULL,
    question_list character varying(1024) NOT NULL,
    incorrect_questions character varying(1024) NOT NULL,
    current_score integer NOT NULL,
    complete boolean NOT NULL,
    user_answers text NOT NULL,
    start timestamp with time zone NOT NULL,
    "end" timestamp with time zone,
    course_id bigint,
    quiz_id bigint NOT NULL,
    user_id bigint NOT NULL
);


--
-- Name: quiz_sitting_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.quiz_sitting_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: quiz_sitting_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.quiz_sitting_id_seq OWNED BY public.quiz_sitting.id;


--
-- Name: result_result; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.result_result (
    id bigint NOT NULL,
    gpa double precision,
    cgpa double precision,
    semester character varying(100) NOT NULL,
    level character varying(25),
    session character varying(100),
    student_id bigint NOT NULL
);


--
-- Name: result_result_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.result_result_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: result_result_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.result_result_id_seq OWNED BY public.result_result.id;


--
-- Name: result_takencourse; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.result_takencourse (
    id bigint NOT NULL,
    assignment numeric(5,2) NOT NULL,
    mid_exam numeric(5,2) NOT NULL,
    quiz numeric(5,2) NOT NULL,
    attendance numeric(5,2) NOT NULL,
    final_exam numeric(5,2) NOT NULL,
    total numeric(5,2) NOT NULL,
    grade character varying(2) NOT NULL,
    point numeric(5,2) NOT NULL,
    comment character varying(200) NOT NULL,
    course_id bigint NOT NULL,
    student_id bigint NOT NULL
);


--
-- Name: result_takencourse_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.result_takencourse_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: result_takencourse_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.result_takencourse_id_seq OWNED BY public.result_takencourse.id;


--
-- Name: accounts_departmenthead id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.accounts_departmenthead ALTER COLUMN id SET DEFAULT nextval('public.accounts_departmenthead_id_seq'::regclass);


--
-- Name: accounts_parent id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.accounts_parent ALTER COLUMN id SET DEFAULT nextval('public.accounts_parent_id_seq'::regclass);


--
-- Name: accounts_student id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.accounts_student ALTER COLUMN id SET DEFAULT nextval('public.accounts_student_id_seq'::regclass);


--
-- Name: accounts_user id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.accounts_user ALTER COLUMN id SET DEFAULT nextval('public.accounts_user_id_seq'::regclass);


--
-- Name: accounts_user_groups id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.accounts_user_groups ALTER COLUMN id SET DEFAULT nextval('public.accounts_user_groups_id_seq'::regclass);


--
-- Name: accounts_user_user_permissions id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.accounts_user_user_permissions ALTER COLUMN id SET DEFAULT nextval('public.accounts_user_user_permissions_id_seq'::regclass);


--
-- Name: app_newsandevents id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.app_newsandevents ALTER COLUMN id SET DEFAULT nextval('public.app_newsandevents_id_seq'::regclass);


--
-- Name: app_semester id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.app_semester ALTER COLUMN id SET DEFAULT nextval('public.app_semester_id_seq'::regclass);


--
-- Name: app_session id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.app_session ALTER COLUMN id SET DEFAULT nextval('public.app_session_id_seq'::regclass);


--
-- Name: auth_group id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_group ALTER COLUMN id SET DEFAULT nextval('public.auth_group_id_seq'::regclass);


--
-- Name: auth_group_permissions id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_group_permissions ALTER COLUMN id SET DEFAULT nextval('public.auth_group_permissions_id_seq'::regclass);


--
-- Name: auth_permission id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_permission ALTER COLUMN id SET DEFAULT nextval('public.auth_permission_id_seq'::regclass);


--
-- Name: course_course id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.course_course ALTER COLUMN id SET DEFAULT nextval('public.course_course_id_seq'::regclass);


--
-- Name: course_courseallocation id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.course_courseallocation ALTER COLUMN id SET DEFAULT nextval('public.course_courseallocation_id_seq'::regclass);


--
-- Name: course_courseallocation_courses id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.course_courseallocation_courses ALTER COLUMN id SET DEFAULT nextval('public.course_courseallocation_courses_id_seq'::regclass);


--
-- Name: course_courseoffer id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.course_courseoffer ALTER COLUMN id SET DEFAULT nextval('public.course_courseoffer_id_seq'::regclass);


--
-- Name: course_program id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.course_program ALTER COLUMN id SET DEFAULT nextval('public.course_program_id_seq'::regclass);


--
-- Name: course_upload id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.course_upload ALTER COLUMN id SET DEFAULT nextval('public.course_upload_id_seq'::regclass);


--
-- Name: course_uploadvideo id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.course_uploadvideo ALTER COLUMN id SET DEFAULT nextval('public.course_uploadvideo_id_seq'::regclass);


--
-- Name: django_admin_log id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_admin_log ALTER COLUMN id SET DEFAULT nextval('public.django_admin_log_id_seq'::regclass);


--
-- Name: django_content_type id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_content_type ALTER COLUMN id SET DEFAULT nextval('public.django_content_type_id_seq'::regclass);


--
-- Name: django_migrations id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_migrations ALTER COLUMN id SET DEFAULT nextval('public.django_migrations_id_seq'::regclass);


--
-- Name: payments_invoice id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payments_invoice ALTER COLUMN id SET DEFAULT nextval('public.payments_invoice_id_seq'::regclass);


--
-- Name: quiz_choice id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.quiz_choice ALTER COLUMN id SET DEFAULT nextval('public.quiz_choice_id_seq'::regclass);


--
-- Name: quiz_progress id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.quiz_progress ALTER COLUMN id SET DEFAULT nextval('public.quiz_progress_id_seq'::regclass);


--
-- Name: quiz_question id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.quiz_question ALTER COLUMN id SET DEFAULT nextval('public.quiz_question_id_seq'::regclass);


--
-- Name: quiz_question_quiz id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.quiz_question_quiz ALTER COLUMN id SET DEFAULT nextval('public.quiz_question_quiz_id_seq'::regclass);


--
-- Name: quiz_quiz id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.quiz_quiz ALTER COLUMN id SET DEFAULT nextval('public.quiz_quiz_id_seq'::regclass);


--
-- Name: quiz_sitting id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.quiz_sitting ALTER COLUMN id SET DEFAULT nextval('public.quiz_sitting_id_seq'::regclass);


--
-- Name: result_result id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.result_result ALTER COLUMN id SET DEFAULT nextval('public.result_result_id_seq'::regclass);


--
-- Name: result_takencourse id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.result_takencourse ALTER COLUMN id SET DEFAULT nextval('public.result_takencourse_id_seq'::regclass);


--
-- Data for Name: accounts_departmenthead; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.accounts_departmenthead (id, department_id, user_id) FROM stdin;
\.


--
-- Data for Name: accounts_parent; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.accounts_parent (id, relation_ship, student_id, user_id, email, first_name, last_name, phone) FROM stdin;
\.


--
-- Data for Name: accounts_student; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.accounts_student (id, level, department_id, student_id) FROM stdin;
17	Bachloar	12	18
18	Bachloar	12	19
\.


--
-- Data for Name: accounts_user; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.accounts_user (id, password, last_login, is_superuser, username, first_name, last_name, is_staff, is_active, date_joined, is_student, is_lecturer, phone, address, picture, email, is_parent, is_dep_head) FROM stdin;
19	pbkdf2_sha256$320000$DyuSWL8OYpLR8ARmKeGl6s$a/+ZvJrVvrCq9jexsE3DgNkLCRvWA6N3cNnC/OA9zn4=	2026-07-02 22:16:29.217317+08	f	user2	l	hll	f	t	2025-12-02 19:09:50.644316+08	t	f	18522255555	wqeqwe	default.png	user2@qq.com	f	f
18	pbkdf2_sha256$320000$LQHyxTz4NV3O0Zb4beiLMq$ivtSdfoGjTD5EMgIh2MnwQuQYdfR3lmp5g9YujrGyQU=	2026-07-02 22:55:39.669825+08	f	user1	l	hll	f	t	2025-12-02 19:09:28.027709+08	t	f	18522255555	wqeqwe	default.png	user1@qq.com	f	f
9	pbkdf2_sha256$320000$DflYLyCHGSnR8g77rTb5Iu$xhXEOuuaYIm1IVN87808oZY0go3vxQtkVqWxqzn2WV4=	2026-07-03 14:10:19.104956+08	t	admin			t	t	2025-11-04 17:03:08.425995+08	f	f	\N	\N	default.png	admin@qq.com	f	f
\.


--
-- Data for Name: accounts_user_groups; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.accounts_user_groups (id, user_id, group_id) FROM stdin;
\.


--
-- Data for Name: accounts_user_user_permissions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.accounts_user_user_permissions (id, user_id, permission_id) FROM stdin;
\.


--
-- Data for Name: app_newsandevents; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.app_newsandevents (id, title, summary, posted_as, updated_date, upload_time) FROM stdin;
13	DRHL Test Event 01	DRHL generated event/news item 01 for crawler coverage and form testing.	Event	2026-07-02 22:55:15.538901+08	2026-07-02 22:55:15.538901+08
14	DRHL Test Event 02	DRHL generated event/news item 02 for crawler coverage and form testing.	News	2026-07-02 22:55:15.540952+08	2026-07-02 22:55:15.540952+08
15	DRHL Test Event 03	DRHL generated event/news item 03 for crawler coverage and form testing.	Event	2026-07-02 22:55:15.541981+08	2026-07-02 22:55:15.541981+08
16	DRHL Test Event 04	DRHL generated event/news item 04 for crawler coverage and form testing.	News	2026-07-02 22:55:15.541981+08	2026-07-02 22:55:15.541981+08
17	DRHL Test Event 05	DRHL generated event/news item 05 for crawler coverage and form testing.	Event	2026-07-02 22:55:15.543041+08	2026-07-02 22:55:15.543041+08
18	DRHL Test Event 06	DRHL generated event/news item 06 for crawler coverage and form testing.	News	2026-07-02 22:55:15.544114+08	2026-07-02 22:55:15.544114+08
19	DRHL Test Event 07	DRHL generated event/news item 07 for crawler coverage and form testing.	Event	2026-07-02 22:55:15.544114+08	2026-07-02 22:55:15.544114+08
20	DRHL Test Event 08	DRHL generated event/news item 08 for crawler coverage and form testing.	News	2026-07-02 22:55:15.545235+08	2026-07-02 22:55:15.545235+08
21	DRHL Test Event 09	DRHL generated event/news item 09 for crawler coverage and form testing.	Event	2026-07-02 22:55:15.545235+08	2026-07-02 22:55:15.545235+08
22	DRHL Test Event 10	DRHL generated event/news item 10 for crawler coverage and form testing.	News	2026-07-02 22:55:15.546335+08	2026-07-02 22:55:15.546335+08
23	DRHL Test Event 11	DRHL generated event/news item 11 for crawler coverage and form testing.	Event	2026-07-02 22:55:15.546335+08	2026-07-02 22:55:15.546335+08
24	DRHL Test Event 12	DRHL generated event/news item 12 for crawler coverage and form testing.	News	2026-07-02 22:55:15.547441+08	2026-07-02 22:55:15.547441+08
25	DRHL Test Event 13	DRHL generated event/news item 13 for crawler coverage and form testing.	Event	2026-07-02 22:55:15.548522+08	2026-07-02 22:55:15.548522+08
26	DRHL Test Event 14	DRHL generated event/news item 14 for crawler coverage and form testing.	News	2026-07-02 22:55:15.548522+08	2026-07-02 22:55:15.548522+08
27	DRHL Test Event 15	DRHL generated event/news item 15 for crawler coverage and form testing.	Event	2026-07-02 22:55:15.549641+08	2026-07-02 22:55:15.549641+08
\.


--
-- Data for Name: app_semester; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.app_semester (id, semester, is_current_semester, next_semester_begins, session_id) FROM stdin;
2	First	t	2026-02-01	2
3	Second	f	2026-07-01	2
\.


--
-- Data for Name: app_session; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.app_session (id, session, is_current_session, next_session_begins) FROM stdin;
2	2025/2026	t	2026-09-01
\.


--
-- Data for Name: auth_group; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.auth_group (id, name) FROM stdin;
4	JcALQ8
\.


--
-- Data for Name: auth_group_permissions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.auth_group_permissions (id, group_id, permission_id) FROM stdin;
\.


--
-- Data for Name: auth_permission; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.auth_permission (id, name, content_type_id, codename) FROM stdin;
1	Can add log entry	1	add_logentry
2	Can change log entry	1	change_logentry
3	Can delete log entry	1	delete_logentry
4	Can view log entry	1	view_logentry
5	Can add permission	2	add_permission
6	Can change permission	2	change_permission
7	Can delete permission	2	delete_permission
8	Can view permission	2	view_permission
9	Can add group	3	add_group
10	Can change group	3	change_group
11	Can delete group	3	delete_group
12	Can view group	3	view_group
13	Can add content type	4	add_contenttype
14	Can change content type	4	change_contenttype
15	Can delete content type	4	delete_contenttype
16	Can view content type	4	view_contenttype
17	Can add session	5	add_session
18	Can change session	5	change_session
19	Can delete session	5	delete_session
20	Can view session	5	view_session
21	Can add news and events	6	add_newsandevents
22	Can change news and events	6	change_newsandevents
23	Can delete news and events	6	delete_newsandevents
24	Can view news and events	6	view_newsandevents
25	Can add session	7	add_session
26	Can change session	7	change_session
27	Can delete session	7	delete_session
28	Can view session	7	view_session
29	Can add semester	8	add_semester
30	Can change semester	8	change_semester
31	Can delete semester	8	delete_semester
32	Can view semester	8	view_semester
33	Can add user	9	add_user
34	Can change user	9	change_user
35	Can delete user	9	delete_user
36	Can view user	9	view_user
37	Can add student	10	add_student
38	Can change student	10	change_student
39	Can delete student	10	delete_student
40	Can view student	10	view_student
41	Can add parent	11	add_parent
42	Can change parent	11	change_parent
43	Can delete parent	11	delete_parent
44	Can view parent	11	view_parent
45	Can add department head	12	add_departmenthead
46	Can change department head	12	change_departmenthead
47	Can delete department head	12	delete_departmenthead
48	Can view department head	12	view_departmenthead
49	Can add course	13	add_course
50	Can change course	13	change_course
51	Can delete course	13	delete_course
52	Can view course	13	view_course
53	Can add program	14	add_program
54	Can change program	14	change_program
55	Can delete program	14	delete_program
56	Can view program	14	view_program
57	Can add upload	15	add_upload
58	Can change upload	15	change_upload
59	Can delete upload	15	delete_upload
60	Can view upload	15	view_upload
61	Can add course allocation	16	add_courseallocation
62	Can change course allocation	16	change_courseallocation
63	Can delete course allocation	16	delete_courseallocation
64	Can view course allocation	16	view_courseallocation
65	Can add upload video	17	add_uploadvideo
66	Can change upload video	17	change_uploadvideo
67	Can delete upload video	17	delete_uploadvideo
68	Can view upload video	17	view_uploadvideo
69	Can add course offer	18	add_courseoffer
70	Can change course offer	18	change_courseoffer
71	Can delete course offer	18	delete_courseoffer
72	Can view course offer	18	view_courseoffer
73	Can add taken course	19	add_takencourse
74	Can change taken course	19	change_takencourse
75	Can delete taken course	19	delete_takencourse
76	Can view taken course	19	view_takencourse
77	Can add result	20	add_result
78	Can change result	20	change_result
79	Can delete result	20	delete_result
80	Can view result	20	view_result
81	Can add Question	21	add_question
82	Can change Question	21	change_question
83	Can delete Question	21	delete_question
84	Can view Question	21	view_question
85	Can add Quiz	22	add_quiz
86	Can change Quiz	22	change_quiz
87	Can delete Quiz	22	delete_quiz
88	Can view Quiz	22	view_quiz
89	Can add Essay style question	23	add_essay_question
90	Can change Essay style question	23	change_essay_question
91	Can delete Essay style question	23	delete_essay_question
92	Can view Essay style question	23	view_essay_question
93	Can add Multiple Choice Question	24	add_mcquestion
94	Can change Multiple Choice Question	24	change_mcquestion
95	Can delete Multiple Choice Question	24	delete_mcquestion
96	Can view Multiple Choice Question	24	view_mcquestion
97	Can add sitting	25	add_sitting
98	Can change sitting	25	change_sitting
99	Can delete sitting	25	delete_sitting
100	Can view sitting	25	view_sitting
101	Can see completed exams.	25	view_sittings
102	Can add User Progress	26	add_progress
103	Can change User Progress	26	change_progress
104	Can delete User Progress	26	delete_progress
105	Can view User Progress	26	view_progress
106	Can add Choice	27	add_choice
107	Can change Choice	27	change_choice
108	Can delete Choice	27	delete_choice
109	Can view Choice	27	view_choice
110	Can add invoice	28	add_invoice
111	Can change invoice	28	change_invoice
112	Can delete invoice	28	delete_invoice
113	Can view invoice	28	view_invoice
\.


--
-- Data for Name: course_course; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.course_course (id, slug, title, code, credit, summary, level, year, semester, is_elective, program_id) FROM stdin;
6	introduction-to-programming	Introduction to Programming	DRHL101	3	Introduction to Programming generated for DRHL access-control experiments.	Bachloar	1	First	f	12
7	discrete-mathematics	Discrete Mathematics	DRHL102	3	Discrete Mathematics generated for DRHL access-control experiments.	Bachloar	1	First	f	12
8	computer-organization	Computer Organization	DRHL103	3	Computer Organization generated for DRHL access-control experiments.	Bachloar	1	First	f	12
9	data-structures	Data Structures	DRHL104	3	Data Structures generated for DRHL access-control experiments.	Bachloar	2	First	f	12
10	database-systems	Database Systems	DRHL105	3	Database Systems generated for DRHL access-control experiments.	Bachloar	2	First	f	12
11	web-application-security	Web Application Security	DRHL106	3	Web Application Security generated for DRHL access-control experiments.	Bachloar	3	First	f	12
12	object-oriented-design	Object Oriented Design	DRHL201	3	Object Oriented Design generated for DRHL access-control experiments.	Bachloar	1	Second	f	12
13	operating-systems	Operating Systems	DRHL202	3	Operating Systems generated for DRHL access-control experiments.	Bachloar	2	Second	f	12
14	computer-networks	Computer Networks	DRHL203	3	Computer Networks generated for DRHL access-control experiments.	Bachloar	2	Second	f	12
15	software-testing	Software Testing	DRHL204	3	Software Testing generated for DRHL access-control experiments.	Bachloar	3	Second	f	13
16	machine-learning-basics	Machine Learning Basics	DRHL205	3	Machine Learning Basics generated for DRHL access-control experiments.	Bachloar	3	Second	f	12
17	secure-software-engineering	Secure Software Engineering	DRHL206	3	Secure Software Engineering generated for DRHL access-control experiments.	Bachloar	4	Second	f	13
\.


--
-- Data for Name: course_courseallocation; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.course_courseallocation (id, lecturer_id, session_id) FROM stdin;
2	9	2
\.


--
-- Data for Name: course_courseallocation_courses; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.course_courseallocation_courses (id, courseallocation_id, course_id) FROM stdin;
2	2	6
3	2	7
4	2	8
5	2	9
6	2	10
7	2	11
8	2	12
9	2	13
10	2	14
11	2	15
12	2	16
13	2	17
\.


--
-- Data for Name: course_courseoffer; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.course_courseoffer (id, dep_head_id) FROM stdin;
\.


--
-- Data for Name: course_program; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.course_program (id, title, summary) FROM stdin;
11	YZicKI	fv4aUCZ0YP
12	Computer Science	DRHL baseline program for access-control testing.
13	Software Engineering	Second DRHL baseline program for navigation and search testing.
\.


--
-- Data for Name: course_upload; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.course_upload (id, title, file, updated_date, upload_time, course_id) FROM stdin;
\.


--
-- Data for Name: course_uploadvideo; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.course_uploadvideo (id, title, slug, video, summary, "timestamp", course_id) FROM stdin;
\.


--
-- Data for Name: django_admin_log; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.django_admin_log (id, action_time, object_id, object_repr, action_flag, change_message, content_type_id, user_id) FROM stdin;
38	2025-11-04 17:04:24.202014+08	8	user2 (l hl)	3		9	9
39	2025-11-04 17:04:24.204527+08	7	user1 (l hl)	3		9	9
40	2025-11-04 17:12:30.428974+08	3	64rHIZ	1	[{"added": {}}]	3	9
41	2025-11-04 17:13:15.359784+08	5	BkHyQV	1	[{"added": {}}]	14	9
42	2025-11-04 17:14:26.335236+08	1	Result object (1)	1	[{"added": {}}]	20	9
43	2025-11-04 17:14:57.44454+08	2	admin	1	[{"added": {}}]	11	9
44	2025-11-04 17:16:34.401958+08	2	3bNEPu	2	[{"changed": {"fields": ["Explanation"]}}]	23	9
45	2025-11-04 17:16:56.417261+08	2	3bNEPu	3		23	9
46	2025-11-04 17:17:19.288005+08	1	Result object (1)	2	[{"changed": {"fields": ["Semester"]}}]	20	9
47	2025-11-04 17:18:04.421412+08	1	Result object (1)	3		20	9
48	2025-11-04 17:18:27.230135+08	2	user1	2	[{"changed": {"fields": ["User", "Relation ship"]}}]	11	9
49	2025-11-04 17:19:10.541678+08	2	user1	3		11	9
50	2025-11-04 17:19:33.145949+08	5	BkHyQV	2	[{"changed": {"fields": ["Summary"]}}]	14	9
51	2025-11-04 17:20:16.499+08	5	BkHyQV	3		14	9
52	2025-11-04 17:20:47.741628+08	3	64rHIZ	2	[]	3	9
53	2025-11-04 17:21:31.220918+08	3	64rHIZ	3		3	9
54	2025-11-04 17:23:56.30978+08	5	xcv	2	[{"changed": {"fields": ["Summary"]}}]	6	9
55	2025-11-04 17:24:18.356886+08	5	xcv	3		6	9
56	2025-11-04 17:25:49.538172+08	5	Progress object (5)	3		26	9
57	2025-11-04 17:26:40.580935+08	2	xpSymK (5SbxKp)	1	[{"added": {}}]	13	9
58	2025-11-04 17:28:17.037878+08	2	xpSymK (5SbxKp)	2	[{"changed": {"fields": ["Summary", "Level", "Year", "Is elective"]}}]	13	9
59	2025-11-04 17:29:00.659978+08	2	xpSymK (5SbxKp)	3		13	9
60	2025-11-04 17:30:37.934151+08	11	user2 (l hl)	3		9	9
61	2025-11-04 17:31:34.769882+08	3	VNTJAO	1	[{"added": {}}]	23	9
62	2025-11-04 17:34:02.412536+08	6	EpGmbs	1	[{"added": {}}]	6	9
63	2025-11-04 19:02:21.00202+08	10	user1 (l hl)	3		9	9
64	2025-11-06 15:03:32.305143+08	14	lecturer1 (l hl)	3		9	9
65	2025-11-06 15:03:32.309248+08	13	user2 (l hl)	3		9	9
66	2025-11-06 15:03:32.310346+08	12	user1 (l hl)	3		9	9
67	2025-11-06 15:12:46.640225+08	3	admin	1	[{"added": {}}]	11	9
68	2025-11-06 15:13:29.425254+08	3	admin	2	[{"changed": {"fields": ["Student", "Relation ship"]}}]	11	9
69	2025-11-06 15:14:12.811531+08	3	admin	3		11	9
70	2025-11-06 15:15:23.780383+08	11	0GwHq6	1	[{"added": {}}]	6	9
71	2025-11-06 15:17:34.747916+08	6	EpGmbs	2	[{"changed": {"fields": ["Summary", "Posted as"]}}]	6	9
72	2025-11-06 15:18:18.246687+08	6	EpGmbs	3		6	9
73	2025-11-06 15:18:41.391353+08	3	ur4Lp5 (AM8xSz)	1	[{"added": {}}]	13	9
74	2025-11-06 15:19:53.376583+08	6	Progress object (6)	3		26	9
75	2025-11-06 15:20:35.809392+08	8	UTfiyY	1	[{"added": {}}]	14	9
76	2025-11-06 15:29:33.580606+08	16	user2 (l hl)	3		9	9
77	2025-11-06 15:31:46.557631+08	4	pEXzkR	1	[{"added": {}}]	23	9
78	2025-11-06 15:34:07.396791+08	1	l hl	1	[{"added": {}}]	16	9
79	2025-11-06 15:34:30.308364+08	3	VNTJAO	2	[{"changed": {"fields": ["Explanation"]}}]	23	9
80	2025-11-06 15:34:52.431458+08	3	VNTJAO	3		23	9
81	2025-11-06 15:35:15.280699+08	1	admin	2	[{"changed": {"fields": ["Lecturer"]}}]	16	9
82	2025-11-06 15:35:37.518441+08	1	admin	3		16	9
83	2025-11-06 15:37:32.388276+08	2	Result object (2)	1	[{"added": {}}]	20	9
84	2025-11-06 15:39:14.328966+08	1	ur4Lp5 (AM8xSz)	1	[{"added": {}}]	19	9
85	2025-11-06 15:39:37.32231+08	4	JcALQ8	1	[{"added": {}}]	3	9
86	2025-12-02 19:08:35.386082+08	17	user2 (l hl)	3		9	9
87	2025-12-02 19:08:35.389289+08	15	user1 (l hl)	3		9	9
\.


--
-- Data for Name: django_content_type; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.django_content_type (id, app_label, model) FROM stdin;
1	admin	logentry
2	auth	permission
3	auth	group
4	contenttypes	contenttype
5	sessions	session
6	app	newsandevents
7	app	session
8	app	semester
9	accounts	user
10	accounts	student
11	accounts	parent
12	accounts	departmenthead
13	course	course
14	course	program
15	course	upload
16	course	courseallocation
17	course	uploadvideo
18	course	courseoffer
19	result	takencourse
20	result	result
21	quiz	question
22	quiz	quiz
23	quiz	essay_question
24	quiz	mcquestion
25	quiz	sitting
26	quiz	progress
27	quiz	choice
28	payments	invoice
\.


--
-- Data for Name: django_migrations; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.django_migrations (id, app, name, applied) FROM stdin;
1	app	0001_initial	2025-10-16 16:39:53.947487+08
2	accounts	0001_initial	2025-10-16 16:39:53.969803+08
3	course	0001_initial	2025-10-16 16:39:54.054146+08
4	course	0002_uploadvideo	2025-10-16 16:39:54.076916+08
5	course	0003_auto_20200803_1335	2025-10-16 16:39:54.082313+08
6	course	0004_auto_20200822_2238	2025-10-16 16:39:54.089516+08
7	contenttypes	0001_initial	2025-10-16 16:39:54.105647+08
8	contenttypes	0002_remove_content_type_name	2025-10-16 16:39:54.1169+08
9	auth	0001_initial	2025-10-16 16:39:54.159651+08
10	auth	0002_alter_permission_name_max_length	2025-10-16 16:39:54.162669+08
11	auth	0003_alter_user_email_max_length	2025-10-16 16:39:54.167052+08
12	auth	0004_alter_user_username_opts	2025-10-16 16:39:54.17052+08
13	auth	0005_alter_user_last_login_null	2025-10-16 16:39:54.173744+08
14	auth	0006_require_contenttypes_0002	2025-10-16 16:39:54.175891+08
15	auth	0007_alter_validators_add_error_messages	2025-10-16 16:39:54.178249+08
16	auth	0008_alter_user_username_max_length	2025-10-16 16:39:54.182851+08
17	auth	0009_alter_user_last_name_max_length	2025-10-16 16:39:54.185847+08
18	auth	0010_alter_group_name_max_length	2025-10-16 16:39:54.192533+08
19	auth	0011_update_proxy_permissions	2025-10-16 16:39:54.20099+08
20	accounts	0002_auto_20200729_1825	2025-10-16 16:39:54.256458+08
21	accounts	0003_auto_20200730_0740	2025-10-16 16:39:54.265907+08
22	accounts	0004_auto_20200822_2238	2025-10-16 16:39:54.271365+08
23	accounts	0005_auto_20200822_2246	2025-10-16 16:39:54.276492+08
24	accounts	0006_auto_20200822_2308	2025-10-16 16:39:54.280593+08
25	accounts	0007_auto_20200825_1248	2025-10-16 16:39:54.286647+08
26	accounts	0008_auto_20200831_1315	2025-10-16 16:39:54.334255+08
27	accounts	0009_auto_20200906_1403	2025-10-16 16:39:54.361696+08
28	accounts	0010_auto_20210401_1718	2025-10-16 16:39:54.400187+08
29	accounts	0011_auto_20210823_0825	2025-10-16 16:39:54.425315+08
30	accounts	0012_auto_20230112_2238	2025-10-16 16:39:54.466002+08
31	accounts	0013_alter_departmenthead_id_alter_parent_id_and_more	2025-10-16 16:39:54.654878+08
32	accounts	0014_alter_user_managers	2025-10-16 16:39:54.680696+08
33	accounts	0015_alter_user_managers	2025-10-16 16:39:54.689824+08
34	admin	0001_initial	2025-10-16 16:39:54.713414+08
35	admin	0002_logentry_remove_auto_add	2025-10-16 16:39:54.720503+08
36	admin	0003_logentry_add_action_flag_choices	2025-10-16 16:39:54.727975+08
37	app	0002_auto_20200730_0746	2025-10-16 16:39:54.738201+08
38	app	0003_auto_20200730_0756	2025-10-16 16:39:54.743373+08
39	app	0004_alter_newsandevents_id_alter_semester_id_and_more	2025-10-16 16:39:54.808596+08
40	auth	0012_alter_user_first_name_max_length	2025-10-16 16:39:54.820193+08
41	course	0005_alter_course_id_alter_courseallocation_id_and_more	2025-10-16 16:39:55.03901+08
42	course	0006_courseoffer	2025-10-16 16:39:55.100174+08
43	payments	0001_initial	2025-10-16 16:39:55.122709+08
44	payments	0002_testclass_array	2025-10-16 16:39:55.129769+08
45	payments	0003_delete_testclass	2025-10-16 16:39:55.132261+08
46	payments	0004_alter_invoice_id	2025-10-16 16:39:55.149517+08
47	quiz	0001_initial	2025-10-16 16:39:55.285853+08
48	quiz	0002_alter_choice_id_alter_progress_id_alter_question_id_and_more	2025-10-16 16:39:55.463746+08
49	result	0001_initial	2025-10-16 16:39:55.528948+08
50	result	0002_auto_20200729_2233	2025-10-16 16:39:55.547682+08
51	result	0003_auto_20200822_2238	2025-10-16 16:39:55.555486+08
52	result	0004_auto_20200825_1248	2025-10-16 16:39:55.563648+08
53	result	0005_alter_result_id_alter_takencourse_id	2025-10-16 16:39:55.596755+08
54	sessions	0001_initial	2025-10-16 16:39:55.615858+08
\.


--
-- Data for Name: payments_invoice; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.payments_invoice (id, total, amount, payment_complete, invoice_code, user_id) FROM stdin;
\.


--
-- Data for Name: quiz_choice; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.quiz_choice (id, choice, correct, question_id) FROM stdin;
\.


--
-- Data for Name: quiz_essay_question; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.quiz_essay_question (question_ptr_id) FROM stdin;
4
\.


--
-- Data for Name: quiz_mcquestion; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.quiz_mcquestion (question_ptr_id, choice_order) FROM stdin;
\.


--
-- Data for Name: quiz_progress; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.quiz_progress (id, score, user_id) FROM stdin;
7		9
8		18
\.


--
-- Data for Name: quiz_question; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.quiz_question (id, figure, content, explanation) FROM stdin;
4		pEXzkR	MQxJCo2iEK
\.


--
-- Data for Name: quiz_question_quiz; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.quiz_question_quiz (id, question_id, quiz_id) FROM stdin;
\.


--
-- Data for Name: quiz_quiz; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.quiz_quiz (id, title, slug, description, category, random_order, answers_at_end, exam_paper, single_attempt, pass_mark, draft, "timestamp", course_id) FROM stdin;
\.


--
-- Data for Name: quiz_sitting; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.quiz_sitting (id, question_order, question_list, incorrect_questions, current_score, complete, user_answers, start, "end", course_id, quiz_id, user_id) FROM stdin;
\.


--
-- Data for Name: result_result; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.result_result (id, gpa, cgpa, semester, level, session, student_id) FROM stdin;
3	3.5	3.5	First	Bachloar	2025/2026	17
4	3.4	3.45	Second	Bachloar	2025/2026	17
5	3.6	3.6	First	Bachloar	2025/2026	18
6	3.5	3.5500000000000003	Second	Bachloar	2025/2026	18
\.


--
-- Data for Name: result_takencourse; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.result_takencourse (id, assignment, mid_exam, quiz, attendance, final_exam, total, grade, point, comment, course_id, student_id) FROM stdin;
2	18.00	17.00	8.00	9.00	42.00	94.00	A+	12.00	PASS	6	17
3	18.00	17.00	8.00	9.00	42.00	94.00	A+	12.00	PASS	7	17
4	18.00	17.00	8.00	9.00	42.00	94.00	A+	12.00	PASS	8	17
5	18.00	17.00	8.00	9.00	42.00	94.00	A+	12.00	PASS	9	17
6	18.00	17.00	8.00	9.00	42.00	94.00	A+	12.00	PASS	10	17
7	18.00	17.00	8.00	9.00	42.00	94.00	A+	12.00	PASS	11	17
8	18.00	17.00	8.00	9.00	42.00	94.00	A+	12.00	PASS	12	17
9	18.00	17.00	8.00	9.00	42.00	94.00	A+	12.00	PASS	13	17
10	19.00	18.00	8.00	9.00	41.00	95.00	A+	12.00	PASS	6	18
11	19.00	18.00	8.00	9.00	41.00	95.00	A+	12.00	PASS	7	18
12	19.00	18.00	8.00	9.00	41.00	95.00	A+	12.00	PASS	8	18
13	19.00	18.00	8.00	9.00	41.00	95.00	A+	12.00	PASS	9	18
14	19.00	18.00	8.00	9.00	41.00	95.00	A+	12.00	PASS	10	18
15	19.00	18.00	8.00	9.00	41.00	95.00	A+	12.00	PASS	11	18
16	19.00	18.00	8.00	9.00	41.00	95.00	A+	12.00	PASS	12	18
17	19.00	18.00	8.00	9.00	41.00	95.00	A+	12.00	PASS	13	18
\.


--
-- Name: accounts_departmenthead_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.accounts_departmenthead_id_seq', 1, false);


--
-- Name: accounts_dephead_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.accounts_dephead_id_seq', 1, false);


--
-- Name: accounts_parent_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.accounts_parent_id_seq', 3, true);


--
-- Name: accounts_student_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.accounts_student_id_seq', 18, true);


--
-- Name: accounts_user_groups_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.accounts_user_groups_id_seq', 1, false);


--
-- Name: accounts_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.accounts_user_id_seq', 19, true);


--
-- Name: accounts_user_user_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.accounts_user_user_permissions_id_seq', 2, true);


--
-- Name: app_newsandevents_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.app_newsandevents_id_seq', 27, true);


--
-- Name: app_semester_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.app_semester_id_seq', 3, true);


--
-- Name: app_session_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.app_session_id_seq', 2, true);


--
-- Name: auth_group_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.auth_group_id_seq', 4, true);


--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.auth_group_permissions_id_seq', 1, false);


--
-- Name: auth_permission_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.auth_permission_id_seq', 113, true);


--
-- Name: course_course_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.course_course_id_seq', 17, true);


--
-- Name: course_courseallocation_courses_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.course_courseallocation_courses_id_seq', 13, true);


--
-- Name: course_courseallocation_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.course_courseallocation_id_seq', 2, true);


--
-- Name: course_courseoffer_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.course_courseoffer_id_seq', 1, false);


--
-- Name: course_program_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.course_program_id_seq', 13, true);


--
-- Name: course_upload_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.course_upload_id_seq', 1, false);


--
-- Name: course_uploadvideo_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.course_uploadvideo_id_seq', 1, false);


--
-- Name: django_admin_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.django_admin_log_id_seq', 87, true);


--
-- Name: django_content_type_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.django_content_type_id_seq', 28, true);


--
-- Name: django_migrations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.django_migrations_id_seq', 54, true);


--
-- Name: payments_invoice_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.payments_invoice_id_seq', 1, false);


--
-- Name: quiz_choice_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.quiz_choice_id_seq', 1, false);


--
-- Name: quiz_progress_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.quiz_progress_id_seq', 8, true);


--
-- Name: quiz_question_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.quiz_question_id_seq', 4, true);


--
-- Name: quiz_question_quiz_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.quiz_question_quiz_id_seq', 1, false);


--
-- Name: quiz_quiz_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.quiz_quiz_id_seq', 1, false);


--
-- Name: quiz_sitting_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.quiz_sitting_id_seq', 1, false);


--
-- Name: result_result_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.result_result_id_seq', 6, true);


--
-- Name: result_takencourse_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.result_takencourse_id_seq', 17, true);


--
-- Name: accounts_departmenthead accounts_dephead_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.accounts_departmenthead
    ADD CONSTRAINT accounts_dephead_pkey PRIMARY KEY (id);


--
-- Name: accounts_departmenthead accounts_dephead_user_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.accounts_departmenthead
    ADD CONSTRAINT accounts_dephead_user_id_key UNIQUE (user_id);


--
-- Name: accounts_parent accounts_parent_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.accounts_parent
    ADD CONSTRAINT accounts_parent_pkey PRIMARY KEY (id);


--
-- Name: accounts_parent accounts_parent_student_id_554fb6f9_uniq; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.accounts_parent
    ADD CONSTRAINT accounts_parent_student_id_554fb6f9_uniq UNIQUE (student_id);


--
-- Name: accounts_parent accounts_parent_user_id_23ea51f7_uniq; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.accounts_parent
    ADD CONSTRAINT accounts_parent_user_id_23ea51f7_uniq UNIQUE (user_id);


--
-- Name: accounts_student accounts_student_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.accounts_student
    ADD CONSTRAINT accounts_student_pkey PRIMARY KEY (id);


--
-- Name: accounts_student accounts_student_student_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.accounts_student
    ADD CONSTRAINT accounts_student_student_id_key UNIQUE (student_id);


--
-- Name: accounts_user_groups accounts_user_groups_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.accounts_user_groups
    ADD CONSTRAINT accounts_user_groups_pkey PRIMARY KEY (id);


--
-- Name: accounts_user_groups accounts_user_groups_user_id_group_id_59c0b32f_uniq; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.accounts_user_groups
    ADD CONSTRAINT accounts_user_groups_user_id_group_id_59c0b32f_uniq UNIQUE (user_id, group_id);


--
-- Name: accounts_user accounts_user_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.accounts_user
    ADD CONSTRAINT accounts_user_pkey PRIMARY KEY (id);


--
-- Name: accounts_user_user_permissions accounts_user_user_permi_user_id_permission_id_2ab516c2_uniq; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.accounts_user_user_permissions
    ADD CONSTRAINT accounts_user_user_permi_user_id_permission_id_2ab516c2_uniq UNIQUE (user_id, permission_id);


--
-- Name: accounts_user_user_permissions accounts_user_user_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.accounts_user_user_permissions
    ADD CONSTRAINT accounts_user_user_permissions_pkey PRIMARY KEY (id);


--
-- Name: accounts_user accounts_user_username_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.accounts_user
    ADD CONSTRAINT accounts_user_username_key UNIQUE (username);


--
-- Name: app_newsandevents app_newsandevents_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.app_newsandevents
    ADD CONSTRAINT app_newsandevents_pkey PRIMARY KEY (id);


--
-- Name: app_semester app_semester_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.app_semester
    ADD CONSTRAINT app_semester_pkey PRIMARY KEY (id);


--
-- Name: app_session app_session_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.app_session
    ADD CONSTRAINT app_session_pkey PRIMARY KEY (id);


--
-- Name: app_session app_session_session_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.app_session
    ADD CONSTRAINT app_session_session_key UNIQUE (session);


--
-- Name: auth_group auth_group_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_group
    ADD CONSTRAINT auth_group_name_key UNIQUE (name);


--
-- Name: auth_group_permissions auth_group_permissions_group_id_permission_id_0cd325b0_uniq; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_permission_id_0cd325b0_uniq UNIQUE (group_id, permission_id);


--
-- Name: auth_group_permissions auth_group_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_pkey PRIMARY KEY (id);


--
-- Name: auth_group auth_group_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_group
    ADD CONSTRAINT auth_group_pkey PRIMARY KEY (id);


--
-- Name: auth_permission auth_permission_content_type_id_codename_01ab375a_uniq; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_codename_01ab375a_uniq UNIQUE (content_type_id, codename);


--
-- Name: auth_permission auth_permission_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_pkey PRIMARY KEY (id);


--
-- Name: course_course course_course_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.course_course
    ADD CONSTRAINT course_course_code_key UNIQUE (code);


--
-- Name: course_course course_course_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.course_course
    ADD CONSTRAINT course_course_pkey PRIMARY KEY (id);


--
-- Name: course_course course_course_slug_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.course_course
    ADD CONSTRAINT course_course_slug_key UNIQUE (slug);


--
-- Name: course_courseallocation_courses course_courseallocation__courseallocation_id_cour_fc6e91fc_uniq; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.course_courseallocation_courses
    ADD CONSTRAINT course_courseallocation__courseallocation_id_cour_fc6e91fc_uniq UNIQUE (courseallocation_id, course_id);


--
-- Name: course_courseallocation_courses course_courseallocation_courses_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.course_courseallocation_courses
    ADD CONSTRAINT course_courseallocation_courses_pkey PRIMARY KEY (id);


--
-- Name: course_courseallocation course_courseallocation_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.course_courseallocation
    ADD CONSTRAINT course_courseallocation_pkey PRIMARY KEY (id);


--
-- Name: course_courseoffer course_courseoffer_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.course_courseoffer
    ADD CONSTRAINT course_courseoffer_pkey PRIMARY KEY (id);


--
-- Name: course_program course_program_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.course_program
    ADD CONSTRAINT course_program_pkey PRIMARY KEY (id);


--
-- Name: course_program course_program_title_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.course_program
    ADD CONSTRAINT course_program_title_key UNIQUE (title);


--
-- Name: course_upload course_upload_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.course_upload
    ADD CONSTRAINT course_upload_pkey PRIMARY KEY (id);


--
-- Name: course_uploadvideo course_uploadvideo_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.course_uploadvideo
    ADD CONSTRAINT course_uploadvideo_pkey PRIMARY KEY (id);


--
-- Name: course_uploadvideo course_uploadvideo_slug_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.course_uploadvideo
    ADD CONSTRAINT course_uploadvideo_slug_key UNIQUE (slug);


--
-- Name: django_admin_log django_admin_log_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_pkey PRIMARY KEY (id);


--
-- Name: django_content_type django_content_type_app_label_model_76bd3d3b_uniq; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_content_type
    ADD CONSTRAINT django_content_type_app_label_model_76bd3d3b_uniq UNIQUE (app_label, model);


--
-- Name: django_content_type django_content_type_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_content_type
    ADD CONSTRAINT django_content_type_pkey PRIMARY KEY (id);


--
-- Name: django_migrations django_migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_migrations
    ADD CONSTRAINT django_migrations_pkey PRIMARY KEY (id);


--
-- Name: django_session django_session_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_session
    ADD CONSTRAINT django_session_pkey PRIMARY KEY (session_key);


--
-- Name: payments_invoice payments_invoice_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payments_invoice
    ADD CONSTRAINT payments_invoice_pkey PRIMARY KEY (id);


--
-- Name: quiz_choice quiz_choice_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.quiz_choice
    ADD CONSTRAINT quiz_choice_pkey PRIMARY KEY (id);


--
-- Name: quiz_essay_question quiz_essay_question_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.quiz_essay_question
    ADD CONSTRAINT quiz_essay_question_pkey PRIMARY KEY (question_ptr_id);


--
-- Name: quiz_mcquestion quiz_mcquestion_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.quiz_mcquestion
    ADD CONSTRAINT quiz_mcquestion_pkey PRIMARY KEY (question_ptr_id);


--
-- Name: quiz_progress quiz_progress_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.quiz_progress
    ADD CONSTRAINT quiz_progress_pkey PRIMARY KEY (id);


--
-- Name: quiz_progress quiz_progress_user_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.quiz_progress
    ADD CONSTRAINT quiz_progress_user_id_key UNIQUE (user_id);


--
-- Name: quiz_question quiz_question_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.quiz_question
    ADD CONSTRAINT quiz_question_pkey PRIMARY KEY (id);


--
-- Name: quiz_question_quiz quiz_question_quiz_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.quiz_question_quiz
    ADD CONSTRAINT quiz_question_quiz_pkey PRIMARY KEY (id);


--
-- Name: quiz_question_quiz quiz_question_quiz_question_id_quiz_id_3414207a_uniq; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.quiz_question_quiz
    ADD CONSTRAINT quiz_question_quiz_question_id_quiz_id_3414207a_uniq UNIQUE (question_id, quiz_id);


--
-- Name: quiz_quiz quiz_quiz_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.quiz_quiz
    ADD CONSTRAINT quiz_quiz_pkey PRIMARY KEY (id);


--
-- Name: quiz_quiz quiz_quiz_slug_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.quiz_quiz
    ADD CONSTRAINT quiz_quiz_slug_key UNIQUE (slug);


--
-- Name: quiz_sitting quiz_sitting_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.quiz_sitting
    ADD CONSTRAINT quiz_sitting_pkey PRIMARY KEY (id);


--
-- Name: result_result result_result_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.result_result
    ADD CONSTRAINT result_result_pkey PRIMARY KEY (id);


--
-- Name: result_takencourse result_takencourse_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.result_takencourse
    ADD CONSTRAINT result_takencourse_pkey PRIMARY KEY (id);


--
-- Name: accounts_dephead_department_id_a1dafd87; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX accounts_dephead_department_id_a1dafd87 ON public.accounts_departmenthead USING btree (department_id);


--
-- Name: accounts_student_department_id_69962b56; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX accounts_student_department_id_69962b56 ON public.accounts_student USING btree (department_id);


--
-- Name: accounts_user_groups_group_id_bd11a704; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX accounts_user_groups_group_id_bd11a704 ON public.accounts_user_groups USING btree (group_id);


--
-- Name: accounts_user_groups_user_id_52b62117; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX accounts_user_groups_user_id_52b62117 ON public.accounts_user_groups USING btree (user_id);


--
-- Name: accounts_user_user_permissions_permission_id_113bb443; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX accounts_user_user_permissions_permission_id_113bb443 ON public.accounts_user_user_permissions USING btree (permission_id);


--
-- Name: accounts_user_user_permissions_user_id_e4f0a161; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX accounts_user_user_permissions_user_id_e4f0a161 ON public.accounts_user_user_permissions USING btree (user_id);


--
-- Name: accounts_user_username_6088629e_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX accounts_user_username_6088629e_like ON public.accounts_user USING btree (username varchar_pattern_ops);


--
-- Name: app_semester_session_id_74165707; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX app_semester_session_id_74165707 ON public.app_semester USING btree (session_id);


--
-- Name: app_session_session_7896309d_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX app_session_session_7896309d_like ON public.app_session USING btree (session varchar_pattern_ops);


--
-- Name: auth_group_name_a6ea08ec_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX auth_group_name_a6ea08ec_like ON public.auth_group USING btree (name varchar_pattern_ops);


--
-- Name: auth_group_permissions_group_id_b120cbf9; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX auth_group_permissions_group_id_b120cbf9 ON public.auth_group_permissions USING btree (group_id);


--
-- Name: auth_group_permissions_permission_id_84c5c92e; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX auth_group_permissions_permission_id_84c5c92e ON public.auth_group_permissions USING btree (permission_id);


--
-- Name: auth_permission_content_type_id_2f476e4b; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX auth_permission_content_type_id_2f476e4b ON public.auth_permission USING btree (content_type_id);


--
-- Name: course_course_code_9dd76455_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX course_course_code_9dd76455_like ON public.course_course USING btree (code varchar_pattern_ops);


--
-- Name: course_course_program_id_dda9b2de; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX course_course_program_id_dda9b2de ON public.course_course USING btree (program_id);


--
-- Name: course_course_slug_8ca9d9ef_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX course_course_slug_8ca9d9ef_like ON public.course_course USING btree (slug varchar_pattern_ops);


--
-- Name: course_courseallocation_courses_course_id_74f75d98; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX course_courseallocation_courses_course_id_74f75d98 ON public.course_courseallocation_courses USING btree (course_id);


--
-- Name: course_courseallocation_courses_courseallocation_id_e203c2aa; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX course_courseallocation_courses_courseallocation_id_e203c2aa ON public.course_courseallocation_courses USING btree (courseallocation_id);


--
-- Name: course_courseallocation_lecturer_id_ae68368a; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX course_courseallocation_lecturer_id_ae68368a ON public.course_courseallocation USING btree (lecturer_id);


--
-- Name: course_courseallocation_session_id_3101be0e; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX course_courseallocation_session_id_3101be0e ON public.course_courseallocation USING btree (session_id);


--
-- Name: course_courseoffer_dep_head_id_e54ea754; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX course_courseoffer_dep_head_id_e54ea754 ON public.course_courseoffer USING btree (dep_head_id);


--
-- Name: course_program_title_76d1dbcf_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX course_program_title_76d1dbcf_like ON public.course_program USING btree (title varchar_pattern_ops);


--
-- Name: course_upload_course_id_624ff4d6; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX course_upload_course_id_624ff4d6 ON public.course_upload USING btree (course_id);


--
-- Name: course_uploadvideo_course_id_0725e558; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX course_uploadvideo_course_id_0725e558 ON public.course_uploadvideo USING btree (course_id);


--
-- Name: course_uploadvideo_slug_2b0a7fce_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX course_uploadvideo_slug_2b0a7fce_like ON public.course_uploadvideo USING btree (slug varchar_pattern_ops);


--
-- Name: django_admin_log_content_type_id_c4bce8eb; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX django_admin_log_content_type_id_c4bce8eb ON public.django_admin_log USING btree (content_type_id);


--
-- Name: django_admin_log_user_id_c564eba6; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX django_admin_log_user_id_c564eba6 ON public.django_admin_log USING btree (user_id);


--
-- Name: django_session_expire_date_a5c62663; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX django_session_expire_date_a5c62663 ON public.django_session USING btree (expire_date);


--
-- Name: django_session_session_key_c0390e0f_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX django_session_session_key_c0390e0f_like ON public.django_session USING btree (session_key varchar_pattern_ops);


--
-- Name: payments_invoice_user_id_2f564088; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX payments_invoice_user_id_2f564088 ON public.payments_invoice USING btree (user_id);


--
-- Name: quiz_choice_question_id_6297ad3f; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX quiz_choice_question_id_6297ad3f ON public.quiz_choice USING btree (question_id);


--
-- Name: quiz_question_quiz_question_id_2b2637b3; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX quiz_question_quiz_question_id_2b2637b3 ON public.quiz_question_quiz USING btree (question_id);


--
-- Name: quiz_question_quiz_quiz_id_eccb418d; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX quiz_question_quiz_quiz_id_eccb418d ON public.quiz_question_quiz USING btree (quiz_id);


--
-- Name: quiz_quiz_course_id_dd25aae3; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX quiz_quiz_course_id_dd25aae3 ON public.quiz_quiz USING btree (course_id);


--
-- Name: quiz_quiz_slug_bdb6a58e_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX quiz_quiz_slug_bdb6a58e_like ON public.quiz_quiz USING btree (slug varchar_pattern_ops);


--
-- Name: quiz_sitting_course_id_72b033f6; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX quiz_sitting_course_id_72b033f6 ON public.quiz_sitting USING btree (course_id);


--
-- Name: quiz_sitting_quiz_id_a3187627; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX quiz_sitting_quiz_id_a3187627 ON public.quiz_sitting USING btree (quiz_id);


--
-- Name: quiz_sitting_user_id_cfb694f3; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX quiz_sitting_user_id_cfb694f3 ON public.quiz_sitting USING btree (user_id);


--
-- Name: result_result_student_id_59df1edd; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX result_result_student_id_59df1edd ON public.result_result USING btree (student_id);


--
-- Name: result_takencourse_course_id_56fd5eb6; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX result_takencourse_course_id_56fd5eb6 ON public.result_takencourse USING btree (course_id);


--
-- Name: result_takencourse_student_id_c971277a; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX result_takencourse_student_id_c971277a ON public.result_takencourse USING btree (student_id);


--
-- Name: accounts_departmenthead accounts_departmenthead_department_id_35df83b0_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.accounts_departmenthead
    ADD CONSTRAINT accounts_departmenthead_department_id_35df83b0_fk FOREIGN KEY (department_id) REFERENCES public.course_program(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: accounts_departmenthead accounts_departmenthead_user_id_62937520_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.accounts_departmenthead
    ADD CONSTRAINT accounts_departmenthead_user_id_62937520_fk FOREIGN KEY (user_id) REFERENCES public.accounts_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: accounts_parent accounts_parent_student_id_554fb6f9_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.accounts_parent
    ADD CONSTRAINT accounts_parent_student_id_554fb6f9_fk FOREIGN KEY (student_id) REFERENCES public.accounts_student(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: accounts_parent accounts_parent_user_id_23ea51f7_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.accounts_parent
    ADD CONSTRAINT accounts_parent_user_id_23ea51f7_fk FOREIGN KEY (user_id) REFERENCES public.accounts_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: accounts_student accounts_student_department_id_69962b56_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.accounts_student
    ADD CONSTRAINT accounts_student_department_id_69962b56_fk FOREIGN KEY (department_id) REFERENCES public.course_program(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: accounts_student accounts_student_student_id_d0d56f60_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.accounts_student
    ADD CONSTRAINT accounts_student_student_id_d0d56f60_fk FOREIGN KEY (student_id) REFERENCES public.accounts_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: accounts_user_groups accounts_user_groups_group_id_bd11a704_fk_auth_group_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.accounts_user_groups
    ADD CONSTRAINT accounts_user_groups_group_id_bd11a704_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES public.auth_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: accounts_user_groups accounts_user_groups_user_id_52b62117_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.accounts_user_groups
    ADD CONSTRAINT accounts_user_groups_user_id_52b62117_fk FOREIGN KEY (user_id) REFERENCES public.accounts_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: accounts_user_user_permissions accounts_user_user_p_permission_id_113bb443_fk_auth_perm; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.accounts_user_user_permissions
    ADD CONSTRAINT accounts_user_user_p_permission_id_113bb443_fk_auth_perm FOREIGN KEY (permission_id) REFERENCES public.auth_permission(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: accounts_user_user_permissions accounts_user_user_permissions_user_id_e4f0a161_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.accounts_user_user_permissions
    ADD CONSTRAINT accounts_user_user_permissions_user_id_e4f0a161_fk FOREIGN KEY (user_id) REFERENCES public.accounts_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: app_semester app_semester_session_id_74165707_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.app_semester
    ADD CONSTRAINT app_semester_session_id_74165707_fk FOREIGN KEY (session_id) REFERENCES public.app_session(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_group_permissions auth_group_permissio_permission_id_84c5c92e_fk_auth_perm; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissio_permission_id_84c5c92e_fk_auth_perm FOREIGN KEY (permission_id) REFERENCES public.auth_permission(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_group_permissions auth_group_permissions_group_id_b120cbf9_fk_auth_group_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_b120cbf9_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES public.auth_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_permission auth_permission_content_type_id_2f476e4b_fk_django_co; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_2f476e4b_fk_django_co FOREIGN KEY (content_type_id) REFERENCES public.django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: course_course course_course_program_id_dda9b2de_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.course_course
    ADD CONSTRAINT course_course_program_id_dda9b2de_fk FOREIGN KEY (program_id) REFERENCES public.course_program(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: course_courseallocation_courses course_courseallocation_courses_course_id_74f75d98_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.course_courseallocation_courses
    ADD CONSTRAINT course_courseallocation_courses_course_id_74f75d98_fk FOREIGN KEY (course_id) REFERENCES public.course_course(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: course_courseallocation_courses course_courseallocation_courses_courseallocation_id_e203c2aa_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.course_courseallocation_courses
    ADD CONSTRAINT course_courseallocation_courses_courseallocation_id_e203c2aa_fk FOREIGN KEY (courseallocation_id) REFERENCES public.course_courseallocation(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: course_courseallocation course_courseallocation_lecturer_id_ae68368a_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.course_courseallocation
    ADD CONSTRAINT course_courseallocation_lecturer_id_ae68368a_fk FOREIGN KEY (lecturer_id) REFERENCES public.accounts_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: course_courseallocation course_courseallocation_session_id_3101be0e_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.course_courseallocation
    ADD CONSTRAINT course_courseallocation_session_id_3101be0e_fk FOREIGN KEY (session_id) REFERENCES public.app_session(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: course_courseoffer course_courseoffer_dep_head_id_e54ea754_fk_accounts_; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.course_courseoffer
    ADD CONSTRAINT course_courseoffer_dep_head_id_e54ea754_fk_accounts_ FOREIGN KEY (dep_head_id) REFERENCES public.accounts_departmenthead(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: course_upload course_upload_course_id_624ff4d6_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.course_upload
    ADD CONSTRAINT course_upload_course_id_624ff4d6_fk FOREIGN KEY (course_id) REFERENCES public.course_course(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: course_uploadvideo course_uploadvideo_course_id_0725e558_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.course_uploadvideo
    ADD CONSTRAINT course_uploadvideo_course_id_0725e558_fk FOREIGN KEY (course_id) REFERENCES public.course_course(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: django_admin_log django_admin_log_content_type_id_c4bce8eb_fk_django_co; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_content_type_id_c4bce8eb_fk_django_co FOREIGN KEY (content_type_id) REFERENCES public.django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: django_admin_log django_admin_log_user_id_c564eba6_fk_accounts_user_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_user_id_c564eba6_fk_accounts_user_id FOREIGN KEY (user_id) REFERENCES public.accounts_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: payments_invoice payments_invoice_user_id_2f564088_fk_accounts_user_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payments_invoice
    ADD CONSTRAINT payments_invoice_user_id_2f564088_fk_accounts_user_id FOREIGN KEY (user_id) REFERENCES public.accounts_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: quiz_choice quiz_choice_question_id_6297ad3f_fk_quiz_mcqu; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.quiz_choice
    ADD CONSTRAINT quiz_choice_question_id_6297ad3f_fk_quiz_mcqu FOREIGN KEY (question_id) REFERENCES public.quiz_mcquestion(question_ptr_id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: quiz_essay_question quiz_essay_question_question_ptr_id_448fe6c4_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.quiz_essay_question
    ADD CONSTRAINT quiz_essay_question_question_ptr_id_448fe6c4_fk FOREIGN KEY (question_ptr_id) REFERENCES public.quiz_question(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: quiz_mcquestion quiz_mcquestion_question_ptr_id_7b24b73b_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.quiz_mcquestion
    ADD CONSTRAINT quiz_mcquestion_question_ptr_id_7b24b73b_fk FOREIGN KEY (question_ptr_id) REFERENCES public.quiz_question(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: quiz_progress quiz_progress_user_id_af390dea_fk_accounts_user_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.quiz_progress
    ADD CONSTRAINT quiz_progress_user_id_af390dea_fk_accounts_user_id FOREIGN KEY (user_id) REFERENCES public.accounts_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: quiz_question_quiz quiz_question_quiz_question_id_2b2637b3_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.quiz_question_quiz
    ADD CONSTRAINT quiz_question_quiz_question_id_2b2637b3_fk FOREIGN KEY (question_id) REFERENCES public.quiz_question(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: quiz_question_quiz quiz_question_quiz_quiz_id_eccb418d_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.quiz_question_quiz
    ADD CONSTRAINT quiz_question_quiz_quiz_id_eccb418d_fk FOREIGN KEY (quiz_id) REFERENCES public.quiz_quiz(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: quiz_quiz quiz_quiz_course_id_dd25aae3_fk_course_course_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.quiz_quiz
    ADD CONSTRAINT quiz_quiz_course_id_dd25aae3_fk_course_course_id FOREIGN KEY (course_id) REFERENCES public.course_course(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: quiz_sitting quiz_sitting_course_id_72b033f6_fk_course_course_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.quiz_sitting
    ADD CONSTRAINT quiz_sitting_course_id_72b033f6_fk_course_course_id FOREIGN KEY (course_id) REFERENCES public.course_course(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: quiz_sitting quiz_sitting_quiz_id_a3187627_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.quiz_sitting
    ADD CONSTRAINT quiz_sitting_quiz_id_a3187627_fk FOREIGN KEY (quiz_id) REFERENCES public.quiz_quiz(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: quiz_sitting quiz_sitting_user_id_cfb694f3_fk_accounts_user_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.quiz_sitting
    ADD CONSTRAINT quiz_sitting_user_id_cfb694f3_fk_accounts_user_id FOREIGN KEY (user_id) REFERENCES public.accounts_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: result_result result_result_student_id_59df1edd_fk_accounts_student_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.result_result
    ADD CONSTRAINT result_result_student_id_59df1edd_fk_accounts_student_id FOREIGN KEY (student_id) REFERENCES public.accounts_student(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: result_takencourse result_takencourse_course_id_56fd5eb6_fk_course_course_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.result_takencourse
    ADD CONSTRAINT result_takencourse_course_id_56fd5eb6_fk_course_course_id FOREIGN KEY (course_id) REFERENCES public.course_course(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: result_takencourse result_takencourse_student_id_c971277a_fk_accounts_student_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.result_takencourse
    ADD CONSTRAINT result_takencourse_student_id_c971277a_fk_accounts_student_id FOREIGN KEY (student_id) REFERENCES public.accounts_student(id) DEFERRABLE INITIALLY DEFERRED;


--
-- PostgreSQL database dump complete
--

\unrestrict qsCe9HObE6ELxBBRFILJvsc238gNwDSPtp93LviHorXyqh45BXOautEqWwocfKB

