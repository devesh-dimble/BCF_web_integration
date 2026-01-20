--
-- PostgreSQL database dump
--

-- Dumped from database version 17.5
-- Dumped by pg_dump version 17.5

-- Started on 2025-08-13 12:07:08

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 218 (class 1259 OID 16416)
-- Name: comments; Type: TABLE; Schema: public; Owner: bcfuser
--

CREATE TABLE public.comments (
    id character varying NOT NULL,
    topic_id character varying,
    author character varying,
    date timestamp without time zone,
    comment character varying
);


ALTER TABLE public.comments OWNER TO bcfuser;

--
-- TOC entry 217 (class 1259 OID 16409)
-- Name: topics; Type: TABLE; Schema: public; Owner: bcfuser
--

CREATE TABLE public.topics (
    id character varying NOT NULL,
    project_id character varying,
    title character varying,
    status character varying,
    creation_author character varying,
    creation_date timestamp without time zone,
    modified_author character varying,
    modified_date timestamp without time zone
);


ALTER TABLE public.topics OWNER TO bcfuser;

--
-- TOC entry 4896 (class 0 OID 16416)
-- Dependencies: 218
-- Data for Name: comments; Type: TABLE DATA; Schema: public; Owner: bcfuser
--

COPY public.comments (id, topic_id, author, date, comment) FROM stdin;
b4ccf130-51f9-44f0-9bbb-5841763f4ca6	30aa6cb4-432e-4b36-8503-fe79ee467119	fafal	2025-05-21 13:42:52	this is a test comment to check
bf8dc9b5-add2-4e91-80dc-ec88cc74d7d4	30aa6cb4-432e-4b36-8503-fe79ee467119	fafal	2025-05-21 13:43:01	[changed TopicStatus : 'Open' to 'In Progress']
54aa3fd4-3454-42c0-aaa8-ecf5f4e8734a	abc123	fafal	\N	This is a test comment from curl
c85c98f3-231b-4d77-a1d9-d9aef4e8139a	abc123	fafal	\N	This is a test comment from curl
\.


--
-- TOC entry 4895 (class 0 OID 16409)
-- Dependencies: 217
-- Data for Name: topics; Type: TABLE DATA; Schema: public; Owner: bcfuser
--

COPY public.topics (id, project_id, title, status, creation_author, creation_date, modified_author, modified_date) FROM stdin;
30aa6cb4-432e-4b36-8503-fe79ee467119	123	Pillar to big	In Progress	fafal	2025-05-21 13:41:44	fafal	2025-05-21 13:43:01
7599f042-f492-4f2f-97fd-ba2895bfd7e4	123	New Pillar Issue	Open	fafal	\N	\N	\N
168bd604-0a09-4d01-8bd3-b3b4be49483b	123	New Pillar Issue	Open	fafal	\N	\N	\N
661a7d95-a2bf-4671-9eac-b7daa2afd6e5	123	New Pillar Issue	Open	fafal	\N	\N	\N
5cbb5d9e-740c-473c-a014-75d123afe907	123	New Pillar Issue	Open	fafal	\N	\N	\N
abc123	123	Updated Pillar Issue	Closed	fafal	\N	fafal	2025-07-07 07:00:21.068853
11ad330b-00de-4ba2-9eae-7ce6cdb0978a	123	Issue Title	Open	Author Name	\N	\N	\N
\.


--
-- TOC entry 4748 (class 2606 OID 16422)
-- Name: comments comments_pkey; Type: CONSTRAINT; Schema: public; Owner: bcfuser
--

ALTER TABLE ONLY public.comments
    ADD CONSTRAINT comments_pkey PRIMARY KEY (id);


--
-- TOC entry 4746 (class 2606 OID 16415)
-- Name: topics topics_pkey; Type: CONSTRAINT; Schema: public; Owner: bcfuser
--

ALTER TABLE ONLY public.topics
    ADD CONSTRAINT topics_pkey PRIMARY KEY (id);


--
-- TOC entry 4749 (class 2606 OID 16423)
-- Name: comments comments_topic_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: bcfuser
--

ALTER TABLE ONLY public.comments
    ADD CONSTRAINT comments_topic_id_fkey FOREIGN KEY (topic_id) REFERENCES public.topics(id);


-- Completed on 2025-08-13 12:07:08

--
-- PostgreSQL database dump complete
--

