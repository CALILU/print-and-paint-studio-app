--
-- PostgreSQL database dump
--

-- Dumped from database version 13.20 (Debian 13.20-1.pgdg120+1)
-- Dumped by pg_dump version 13.20 (Debian 13.20-1.pgdg120+1)

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: favorites; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.favorites (
    id integer NOT NULL,
    user_id integer NOT NULL,
    video_id integer NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.favorites OWNER TO postgres;

--
-- Name: favorites_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.favorites_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.favorites_id_seq OWNER TO postgres;

--
-- Name: favorites_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.favorites_id_seq OWNED BY public.favorites.id;


--
-- Name: techniques; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.techniques (
    id integer NOT NULL,
    video_id integer NOT NULL,
    name character varying(100) NOT NULL,
    start_time integer NOT NULL,
    end_time integer NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.techniques OWNER TO postgres;

--
-- Name: techniques_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.techniques_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.techniques_id_seq OWNER TO postgres;

--
-- Name: techniques_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.techniques_id_seq OWNED BY public.techniques.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    username character varying(50) NOT NULL,
    email character varying(100) NOT NULL,
    password_hash character varying(255) NOT NULL,
    role character varying(20) DEFAULT 'user'::character varying,
    experience_level character varying(20) DEFAULT 'beginner'::character varying,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_id_seq OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: videos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.videos (
    id integer NOT NULL,
    title character varying(255) NOT NULL,
    description text,
    video_id character varying(20) NOT NULL,
    channel character varying(100),
    category character varying(50) DEFAULT 'Sin categor├¡a'::character varying,
    technique_start_time integer DEFAULT 0,
    technique_end_time integer,
    difficulty_level character varying(20) DEFAULT 'beginner'::character varying,
    published_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    version integer DEFAULT 1
);


ALTER TABLE public.videos OWNER TO postgres;

--
-- Name: videos_copia; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.videos_copia (
    id integer,
    title character varying(255),
    description text,
    video_id character varying(20),
    channel character varying(100),
    category character varying(50),
    technique_start_time integer,
    technique_end_time integer,
    difficulty_level character varying(20),
    published_at timestamp without time zone,
    created_at timestamp without time zone
);


ALTER TABLE public.videos_copia OWNER TO postgres;

--
-- Name: videos_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.videos_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.videos_id_seq OWNER TO postgres;

--
-- Name: videos_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.videos_id_seq OWNED BY public.videos.id;


--
-- Name: favorites id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.favorites ALTER COLUMN id SET DEFAULT nextval('public.favorites_id_seq'::regclass);


--
-- Name: techniques id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.techniques ALTER COLUMN id SET DEFAULT nextval('public.techniques_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: videos id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.videos ALTER COLUMN id SET DEFAULT nextval('public.videos_id_seq'::regclass);


--
-- Data for Name: favorites; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.favorites (id, user_id, video_id, created_at) FROM stdin;
6	3	82	2025-04-22 19:30:58.971994
7	2	2	2025-04-22 21:05:18.571041
8	2	38	2025-04-22 21:05:20.121921
9	5	82	2025-04-24 14:36:50.55125
10	5	89	2025-04-24 14:36:51.927255
\.


--
-- Data for Name: techniques; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.techniques (id, video_id, name, start_time, end_time, created_at) FROM stdin;
20	82	Sombreado base rojo	130	500	2025-04-22 21:31:30.504545
21	82	Luces	180	310	2025-04-24 14:27:36.461965
22	96	Como personalice mi aer├│grafo y mas cosas	305	366	2025-04-24 16:21:01.059233
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, username, email, password_hash, role, experience_level, created_at) FROM stdin;
5	isidro	isidromislata@gmail.com	pbkdf2:sha256:260000$JfYWhyXdo8Sn905M$e6a4e07928b8039daa49dbbe763a04b88cc6ccadcb2ec0cd0bae0d593c6b8c8e	user	expert	2025-04-21 10:08:54.018703
1	admin	admin@printandpaint.com	pbkdf2:sha256:260000$pqwDX7YsoUvDEt1O$5c1842c75ad217b04fd5334b98771b1e16d205f5545f556c79c070fc9bcc90ef	admin	expert	2025-04-20 16:27:55.224901
2	calilu1	CALILU@GMAIL.COM	pbkdf2:sha256:260000$xoEm7fBjxCP7GANX$85b76c3ea0220e54758d591ce66ac4e5ec6cbed032c7ec1e7f5b888bfd06b278	user	beginner	2025-04-20 16:31:39.535115
4	juan	juan@gmail.com	pbkdf2:sha256:260000$F8TEhOsIbCx5NnOo$cf2b7fcb5efc17389a14aa684fd0ff97733a914a292be01fb088b39c281e0d02	user	intermediate	2025-04-20 18:00:07.152762
3	pepe	pepe@gmail.con	pbkdf2:sha256:260000$AOtLQMYjpljGmpUz$caed73e73d61cdff00c08fb79fd1ad31140f1cdc3d2ec3c4479c45ab4e1ec5f3	user	expert	2025-04-20 16:32:03.883092
\.


--
-- Data for Name: videos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.videos (id, title, description, video_id, channel, category, technique_start_time, technique_end_time, difficulty_level, published_at, created_at, version) FROM stdin;
94	How to Paint Batmobile Diorama//Timelapse Airbrush	How to Paint Batmobile Diorama//Timelapse Airbrush	XVuN6ygbOC8	Print and Paint Studio	Sombreado	71	213	beginner	2025-04-24 14:22:34.179932	2025-04-24 14:22:34.179935	1
2	Lavado y Curado de resina Uniformation GKtwo. Puesta en marcha y funcionamiento	Lavado y Curado de resina Uniformation GKtwo. Puesta en marcha y funcionamiento	dU2YoAcBb98	Print&Paint Studio	Pintura Base	290	360	beginner	2024-06-18 19:08:16	2025-04-22 19:08:16	1
82	How to Paint Batmobile Diorama//Timelapse Airbrush	How to Paint Batmobile Diorama//Timelapse Airbrush	XVuN6ygbOC8	Print&Paint Studio	Pintura Base	250	380	expert	2025-04-22 19:08:16	2025-04-22 19:08:16	1
86	How to paint Freddy Krueger Diorama// Timelapse Airbrush//Part 1	How to paint Freddy Krueger Diorama// Timelapse Airbrush//Part 1	v_IDAWv8X2U	Print&Paint Studio	Barnizado	0	0	expert	2020-11-13 19:08:16	2025-04-22 19:08:16	1
89	3D Print and Paint Spider-Man VS Venom Bust//Part 1	3D Print and Paint Spider-Man VS Venom Bust//Part 1	MtdgNxIJSHY	Print&Paint Studio	Sombreado	0	0	expert	2020-10-23 19:08:16	2025-04-22 19:08:16	1
96	Lavado y Curado de resina Uniformation GKtwo. Puesta en marcha y funcionamiento	Lavado y Curado de resina Uniformation GKtwo. Puesta en marcha y funcionamiento	dU2YoAcBb98	Print and Paint Studio	Iluminaci├│n	122	284	intermediate	2025-04-24 16:20:38.608268	2025-04-24 16:20:38.608271	1
81	How to paint Iron Man Base 1/8//Timelapse Airbrush// Pat One	How to paint Iron Man Base 1/8//Timelapse Airbrush// Pat One	mNOw4krVvF0	Print&Paint Studio	Sombreado	0	0	intermediate	2025-04-22 19:08:16	2025-04-22 19:08:16	1
83	How to paint Facehugger and Alien Egg// Timelapse Airbrush	How to paint Facehugger and Alien Egg// Timelapse Airbrush	ribKHdQCMV4	Print&Paint Studio	Detalles	0	0	beginner	2025-04-22 19:08:16	2025-04-22 19:08:16	1
85	How to paint Freddy Krueger // Timelapse Airbrush//Part 2	How to paint Freddy Krueger // Timelapse Airbrush//Part 2	I_QdyG3y4og	Print&Paint Studio	Efectos Especiales	0	0	intermediate	2020-11-20 19:08:16	2025-04-22 19:08:16	1
87	Painting Robocop Bust// Timelapse Airbrush	Painting Robocop Bust// Timelapse Airbrush	h7Mh1iLttVQ	Print&Paint Studio	Peanas	0	0	beginner	2020-11-06 19:08:16	2025-04-22 19:08:16	1
88	3D Print and Paint Spider-Man VS Venom Bust//Part 2	3D Print and Paint Spider-Man VS Venom Bust//Part 2	eJ0WxrTQs7s	Print&Paint Studio	Pintura Base	0	0	intermediate	2020-10-30 19:08:16	2025-04-22 19:08:16	1
3	Studio Pro aprende a pintar estatuas premium	Studio Pro aprende a pintar estatuas premium	P1OTTPIK5lU	Print&Paint Studio	Sombreado	0	0	beginner	2024-06-07 19:08:16	2025-04-22 19:08:16	1
35	Pintando una Base de Dragon Ball en el menor tiempo posible/Impresi├│n de resina 3D/aerograf├¡a	Pintando una Base de Dragon Ball en el menor tiempo posible/Impresi├│n de resina 3D/aerograf├¡a	gejM5LCVqXU	Print&Paint Studio	Iluminacion	0	0	intermediate	2023-06-23 19:08:16	2025-04-22 19:08:16	1
39	Como escalar figuras de impresion 3D facil y r├ípido/How to scale 3D printing figures easy and fast.	Como escalar figuras de impresion 3D facil y r├ípido/How to scale 3D printing figures easy and fast.	0Zvqzxw7ahA	Print&Paint Studio	Barnizado	0	0	intermediate	2023-05-12 19:08:16	2025-04-22 19:08:16	1
41	Como pintar She Hulk realista impresi├│n 3D resina/Como pintar impresiones 3D de resina/ Vx- labs.	Como pintar She Hulk realista impresi├│n 3D resina/Como pintar impresiones 3D de resina/ Vx- labs.	bZqzeX5sdWs	Print&Paint Studio	Pintura Base	0	0	beginner	2025-04-22 19:08:16	2025-04-22 19:08:16	1
42	Objetivo 3D Printer Party 2023/ Directo 12H, Estatua underworld de 1m de altura impresa en resina 3D	Objetivo 3D Printer Party 2023/ Directo 12H, Estatua underworld de 1m de altura impresa en resina 3D	7e2cahXz6bY	Print&Paint Studio	Sombreado	0	0	intermediate	2023-03-06 19:08:16	2025-04-22 19:08:16	1
44	Como preparar y usar paleta humeda. Para que sirve la paleta humeda?/impresion 3d/STL Gratis.	Como preparar y usar paleta humeda. Para que sirve la paleta humeda?/impresion 3d/STL Gratis.	Y_yGRtSLGJU	Print&Paint Studio	Detalles	0	0	beginner	2025-04-22 19:08:16	2025-04-22 19:08:16	1
45	Como pintar piel negra realista en figuras 1/6 facil/Paint realistic black skin on 1/6 figures	Como pintar piel negra realista en figuras 1/6 facil/Paint realistic black skin on 1/6 figures	oW-uviCH6wI	Print&Paint Studio	Efectos Especiales	0	0	intermediate	2025-04-22 19:08:16	2025-04-22 19:08:16	1
38	Tutorial de chitubox facil 2023 Orientaci├│n, piezas Huecas y Agujeros/impresi├│n de resina 3d.	Tutorial de chitubox facil 2023 Orientaci├│n, piezas Huecas y Agujeros/impresi├│n de resina 3d.	p2QkZZBQlcQ	Print&Paint Studio	Efectos Especiales	0	0	beginner	2023-05-19 19:08:16	2025-04-22 19:08:16	1
36	­ƒöÑComo conseguir m├íxima transparencia en impresi├│n 3D facil/­ƒöÑHow to get transparency in 3D printing	­ƒöÑComo conseguir m├íxima transparencia en impresi├│n 3D facil/­ƒöÑHow to get transparency in 3D printing	VlAGF0U4Cv4	Print&Paint Studio	Detalles	0	0	expert	2023-06-16 19:08:16	2025-04-22 19:08:16	1
40	Como pintar Joker Arkham impreso en resina 3d/tutorial aerograf├¡a en espa├▒ol/Impresi├│n 3D	Como pintar Joker Arkham impreso en resina 3d/tutorial aerograf├¡a en espa├▒ol/Impresi├│n 3D	Vss8rd8xQMc	Print&Paint Studio	Peanas	0	0	expert	2025-04-22 19:08:16	2025-04-22 19:08:16	1
43	Como pintar Majin Vegeta Dragon ball impreso en resina 3d/Paint Majin Vegeta printed in 3d resin	Como pintar Majin Vegeta Dragon ball impreso en resina 3d/Paint Majin Vegeta printed in 3d resin	lVlGkE6vCsk	Print&Paint Studio	Iluminacion	0	0	expert	2023-02-03 19:08:16	2025-04-22 19:08:16	1
60	Como pintar efecto metal realista//Impresi├│n 3D resina//Tutorial aerograf├¡a espa├▒ol	Como pintar efecto metal realista//Impresi├│n 3D resina//Tutorial aerograf├¡a espa├▒ol	4LSLmF1VhUQ	Print&Paint Studio	Detalles	0	0	intermediate	2021-11-12 19:08:16	2025-04-22 19:08:16	1
84	How to paint The Mask//Timelapse Airbrush	How to paint The Mask//Timelapse Airbrush	vvMSg9-6M6U	Print&Paint Studio	Efectos Especiales	0	0	intermediate	2020-11-27 19:08:16	2025-04-22 19:08:16	1
57	Como pintar pieles realistas en impresiones 3D//Parte 2 textura realista y lavados//Aerograf├¡a	Como pintar pieles realistas en impresiones 3D//Parte 2 textura realista y lavados//Aerograf├¡a	ychOJ8P8s_M	Print&Paint Studio	Peanas	0	0	beginner	2025-04-22 19:08:16	2025-04-22 19:08:16	1
58	Como pintar pieles realistas en impresiones 3D//Parte 1//Color base y sombreado b├ísico//Aerografia	Como pintar pieles realistas en impresiones 3D//Parte 1//Color base y sombreado b├ísico//Aerografia	lBnITz1NyBU	Print&Paint Studio	Pintura Base	0	0	intermediate	2025-04-22 19:08:16	2025-04-22 19:08:16	1
56	Como pintar piel femenina en impresiones 3d­ƒÄ¿//Figura Lara Croft Angelina Jolie escala 1/5 ­ƒÿì	Como pintar piel femenina en impresiones 3d­ƒÄ¿//Figura Lara Croft Angelina Jolie escala 1/5 ­ƒÿì	WaWRJ-bUuis	Print&Paint Studio	Barnizado	0	0	expert	2022-02-21 19:08:16	2025-04-22 19:08:16	1
34	Geeetech Alkaid Impresora de resina con buena calidad precio por menos de 100 euros	Geeetech Alkaid Impresora de resina con buena calidad precio por menos de 100 euros	FhWCiNzgsGk	Print&Paint Studio	Detalles	0	0	expert	2023-06-27 19:08:16	2025-04-22 19:08:16	1
79	Como pintar casco de Iron Man metalizado// impresion 3D resina// Tutorial en espa├▒ol	Como pintar casco de Iron Man metalizado// impresion 3D resina// Tutorial en espa├▒ol	XW5UBhK1QBU	Print&Paint Studio	Peanas	0	0	expert	2025-04-22 19:08:16	2025-04-22 19:08:16	1
46	Resumen El reto de octubre/entra a formar parte de la comunidad/Tem├ítica Halloween/impresi├│n 3D	Resumen El reto de octubre/entra a formar parte de la comunidad/Tem├ítica Halloween/impresi├│n 3D	J_P2H18lNsc	Print&Paint Studio	Barnizado	0	0	expert	2022-11-18 19:08:16	2025-04-22 19:08:16	1
49	Como pintar figuras disney impresas en 3D/Pintando aladd├¡n resina/tutorial aerografia/impresion 3D	Como pintar figuras disney impresas en 3D/Pintando aladd├¡n resina/tutorial aerografia/impresion 3D	NwVL73q0zqw	Print&Paint Studio	Sombreado	0	0	expert	2022-11-04 19:08:16	2025-04-22 19:08:16	1
59	Como Quitar l├¡neas de uni├│n y preparar para pintar impresiones 3D//Postprocesado impresi├│n de resina	Como Quitar l├¡neas de uni├│n y preparar para pintar impresiones 3D//Postprocesado impresi├│n de resina	Ik8kepP_K3c	Print&Paint Studio	Sombreado	0	0	expert	2021-11-26 19:08:16	2025-04-22 19:08:16	1
30	­ƒîî­ƒöÑPintar piel Thanos realista impreso en resina 3D/­ƒîî­ƒöÑPaint realistic Thanos skin printed in 3D resin	­ƒîî­ƒöÑPintar piel Thanos realista impreso en resina 3D/­ƒîî­ƒöÑPaint realistic Thanos skin printed in 3D resin	k4jTJkoLV74	Print&Paint Studio	Pintura Base	0	0	intermediate	2025-04-22 19:08:16	2025-04-22 19:08:16	1
32	Pintar efecto madera hiperrealista en impresi├│n 3D/Paint hyperrealistic wood effect in 3D printing	Pintar efecto madera hiperrealista en impresi├│n 3D/Paint hyperrealistic wood effect in 3D printing	EALMV1klhlU	Print&Paint Studio	Sombreado	0	0	beginner	2023-07-07 19:08:16	2025-04-22 19:08:16	1
33	Pintar efecto fuego realista en resina transparente/Paint realistic fire effect in transparent resin	Pintar efecto fuego realista en resina transparente/Paint realistic fire effect in transparent resin	LJPeG-LbyVI	Print&Paint Studio	Iluminacion	0	0	intermediate	2023-06-30 19:08:16	2025-04-22 19:08:16	1
66	Repintado Robocop Hot Toys Diecast	Repintado Robocop Hot Toys Diecast	9kBOEUn8CaQ	Print&Paint Studio	Efectos Especiales	0	0	beginner	2021-07-23 19:08:16	2025-04-22 19:08:16	1
78	How to paint Iron Man//Como pintar Iron Man 1/8//Timelapse airbrush//Part 2	How to paint Iron Man//Como pintar Iron Man 1/8//Timelapse airbrush//Part 2	UuoE3GXejuc	Print&Paint Studio	Barnizado	0	0	intermediate	2021-02-05 19:08:16	2025-04-22 19:08:16	1
80	Como pintar caras realistas para nuestras figuras //Tony Stark//Tutorial en espa├▒ol.	Como pintar caras realistas para nuestras figuras //Tony Stark//Tutorial en espa├▒ol.	w_eQEeSSa-o	Print&Paint Studio	Pintura Base	0	0	beginner	2025-04-22 19:08:16	2025-04-22 19:08:16	1
47	An├ílisis actualidad nuevos Stl noviembre 2022/patreons para impresi├│n 3d/archivos impresi├│n 3D	An├ílisis actualidad nuevos Stl noviembre 2022/patreons para impresi├│n 3d/archivos impresi├│n 3D	VxF5Vjh6QIo	Print&Paint Studio	Peanas	0	0	beginner	2022-11-13 19:08:16	2025-04-22 19:08:16	1
48	Como pintar spider-man impreso en resina 3D facil/How to paint spider-man 3d print/Airbrush tutorial	Como pintar spider-man impreso en resina 3D facil/How to paint spider-man 3d print/Airbrush tutorial	jpPay1-zYMM	Print&Paint Studio	Pintura Base	0	0	intermediate	2022-11-11 19:08:16	2025-04-22 19:08:16	1
77	Como Pintar The Mandalorian/Parte uno/tutorial espa├▒ol airbrush	Como Pintar The Mandalorian/Parte uno/tutorial espa├▒ol airbrush	ToczWtX8QLg	Print&Paint Studio	Iluminacion	0	0	beginner	2021-02-26 19:08:16	2025-04-22 19:08:16	1
61	Como pintar Hulk realista//Impresi├│n 3d resina//Tutorial aer├│grafo en espa├▒ol	Como pintar Hulk realista//Impresi├│n 3d resina//Tutorial aer├│grafo en espa├▒ol	y8mkmK9wHD0	Print&Paint Studio	Iluminacion	0	0	beginner	2021-11-05 19:08:16	2025-04-22 19:08:16	1
62	Como hacer limpiador aer├│grafo casero barato// limpieza aer├│grafo f├ícil//Aerograf├¡a en espa├▒ol	Como hacer limpiador aer├│grafo casero barato// limpieza aer├│grafo f├ícil//Aerograf├¡a en espa├▒ol	feCLklW2tWI	Print&Paint Studio	Detalles	0	0	intermediate	2025-04-22 19:08:16	2025-04-22 19:08:16	1
5	Ojos profesionales en tus figuras Facil y rapido!/ Impresion 3D	Ojos profesionales en tus figuras Facil y rapido!/ Impresion 3D	zJOFSe1KCLQ	Print&Paint Studio	Sombreado	0	0	expert	2024-05-10 19:08:16	2025-04-22 19:08:16	1
8	Sacamos Nuestra nueva estatua de la serie dinosaurios. Prefieres en Kit o terminada?	Sacamos Nuestra nueva estatua de la serie dinosaurios. Prefieres en Kit o terminada?	3-R904Zgu_c	Print&Paint Studio	Efectos Especiales	0	0	expert	2025-04-22 19:08:16	2025-04-22 19:08:16	1
11	Pintando resina oficial de Crisanta del videojuego blasphemous/gu├¡a Aerograf├¡a en estatuas	Pintando resina oficial de Crisanta del videojuego blasphemous/gu├¡a Aerograf├¡a en estatuas	5zY-Y8yGCWY	Print&Paint Studio	Pintura Base	0	0	expert	2024-03-18 19:08:16	2025-04-22 19:08:16	1
4	­ƒÄ¿vallejo game air mi opini├│n despu├®s de 5 meses + tutorial pintando mickey mouse impreso en resina	­ƒÄ¿vallejo game air mi opini├│n despu├®s de 5 meses + tutorial pintando mickey mouse impreso en resina	PPT28NzmGqo	Print&Paint Studio	Pintura Base	0	0	intermediate	2024-05-19 19:08:16	2025-04-22 19:08:16	1
6	Como conseguir STL gratis y de pago en 2024 para imprimir en 3D. Descarga los mejores STL 2024	Como conseguir STL gratis y de pago en 2024 para imprimir en 3D. Descarga los mejores STL 2024	2wi6ROJo-gI	Print&Paint Studio	Iluminacion	0	0	beginner	2024-05-03 19:08:16	2025-04-22 19:08:16	1
7	Como pintar fuego con efecto OSL/Ghost rider impresion 3/DHow to paint fire with OSL/Ghost Rider	Como pintar fuego con efecto OSL/Ghost rider impresion 3/DHow to paint fire with OSL/Ghost Rider	iamJMus2N3g	Print&Paint Studio	Detalles	0	0	intermediate	2025-04-22 19:08:16	2025-04-22 19:08:16	1
9	Como pintar al Correcaminos impreso en resina 3d/How to paint the Road Runner printed in 3D resin.	Como pintar al Correcaminos impreso en resina 3d/How to paint the Road Runner printed in 3D resin.	n_g4FetyXzc	Print&Paint Studio	Barnizado	0	0	beginner	2025-04-22 19:08:16	2025-04-22 19:08:16	1
10	Como pintar a Piccolo impresi├│n en resina 3D/ Lucas Perez patreon	Como pintar a Piccolo impresi├│n en resina 3D/ Lucas Perez patreon	RP4T5-IN95A	Print&Paint Studio	Peanas	0	0	intermediate	2024-03-29 19:08:16	2025-04-22 19:08:16	1
12	Como pintar baby yoda realista impreso en resina 3d con pintura acrilica	Como pintar baby yoda realista impreso en resina 3d con pintura acrilica	CSfifryg6HA	Print&Paint Studio	Sombreado	0	0	beginner	2024-02-09 19:08:16	2025-04-22 19:08:16	1
13	Como pintar Goku namek facil y rapido impreso en resina 3D con acrilicos/impresion 3D	Como pintar Goku namek facil y rapido impreso en resina 3D con acrilicos/impresion 3D	z8PEz4jI93s	Print&Paint Studio	Iluminacion	0	0	intermediate	2024-02-02 19:08:16	2025-04-22 19:08:16	1
14	Como pintar estilo cartoon nivel f├ícil y r├ípido en impresiones 3d /Pato lucas looney tunes.	Como pintar estilo cartoon nivel f├ícil y r├ípido en impresiones 3d /Pato lucas looney tunes.	pDoxeo5DrxE	Print&Paint Studio	Detalles	0	0	Expert	2025-04-22 19:08:16	2025-04-22 19:08:16	1
15	Aerografos Gaahleri Ace GHAD-98D y Advanced GHAD-68. Buena calidad precio?	Aerografos Gaahleri Ace GHAD-98D y Advanced GHAD-68. Buena calidad precio?	TdUlOdM7Zk4	Print&Paint Studio	Efectos Especiales	0	0	beginner	2025-04-22 19:08:16	2025-04-22 19:08:16	1
16	Como pintar lampara aladdin impresa en 3d facil/How to paint Aladdin lamp printed in 3D easy	Como pintar lampara aladdin impresa en 3d facil/How to paint Aladdin lamp printed in 3D easy	sHSTquuTHFo	Print&Paint Studio	Barnizado	0	0	intermediate	2025-04-22 19:08:16	2025-04-22 19:08:16	1
17	Como pintar c3po impreso en 3d Facil y rapido/How to paint c3po printed in 3d Easy and fast/3d print	Como pintar c3po impreso en 3d Facil y rapido/How to paint c3po printed in 3d Easy and fast/3d print	aOQ7TIM34do	Print&Paint Studio	Peanas	0	0	Expert	2025-04-22 19:08:16	2025-04-22 19:08:16	1
18	Como pintar cell Dragon ball impreso en resina 3d/Paint cell printed in 3d resin	Como pintar cell Dragon ball impreso en resina 3d/Paint cell printed in 3d resin	s--u3qiNolg	Print&Paint Studio	Pintura Base	0	0	beginner	2025-04-22 19:08:16	2025-04-22 19:08:16	1
19	Easythreed k7 Impresora econ├│mica para principiantes. Todo lo que necesitas saber antes de comprarla	Easythreed k7 Impresora econ├│mica para principiantes. Todo lo que necesitas saber antes de comprarla	32_abjrxQqo	Print&Paint Studio	Sombreado	0	0	intermediate	2025-04-22 19:08:16	2025-04-22 19:08:16	1
20	TwoTrees SP-5 V3 imprimiendo Terminator a tama├▒o real (Busto)	TwoTrees SP-5 V3 imprimiendo Terminator a tama├▒o real (Busto)	SGsg7Jf2RFc	Print&Paint Studio	Iluminacion	0	0	Expert	2023-11-24 19:08:16	2025-04-22 19:08:16	1
21	Como pintar Kame Hame Ha y efectos de energ├¡a en figuras impresas en resina 3D transparente.	Como pintar Kame Hame Ha y efectos de energ├¡a en figuras impresas en resina 3D transparente.	t4Qn7pKmNEo	Print&Paint Studio	Detalles	0	0	beginner	2023-11-10 19:08:16	2025-04-22 19:08:16	1
22	Pinta armas realistas a escala impresas en resina /Paint realistic scale weapons printed in 3d resin	Pinta armas realistas a escala impresas en resina /Paint realistic scale weapons printed in 3d resin	g2Y3sAzVj4Y	Print&Paint Studio	Efectos Especiales	0	0	intermediate	2025-04-22 19:08:16	2025-04-22 19:08:16	1
23	uniformation GK2 Impresi├│n de resina en 8K. Realmente imprime tan bien? Opini├│n sincera.	uniformation GK2 Impresi├│n de resina en 8K. Realmente imprime tan bien? Opini├│n sincera.	SZYWeO0rKhA	Print&Paint Studio	Barnizado	0	0	Expert	2025-04-22 19:08:16	2025-04-22 19:08:16	1
24	Experiencia como colaboradores en Freak wars 2023. Resumen del evento y nuestro stand.	Experiencia como colaboradores en Freak wars 2023. Resumen del evento y nuestro stand.	w83a04XcO3M	Print&Paint Studio	Peanas	0	0	beginner	2025-04-22 19:08:16	2025-04-22 19:08:16	1
25	UniFormation GKtwo todo lo que necesitas saber sobre su montaje y puesta en marcha.	UniFormation GKtwo todo lo que necesitas saber sobre su montaje y puesta en marcha.	DVOxFWQGPrg	Print&Paint Studio	Pintura Base	0	0	intermediate	2025-04-22 19:08:16	2025-04-22 19:08:16	1
26	buzz lightyear repaint/ convierte un juguete en figura de colecci├│n premium. Parte 2	buzz lightyear repaint/ convierte un juguete en figura de colecci├│n premium. Parte 2	746L8Hyhm9E	Print&Paint Studio	Sombreado	0	0	Expert	2025-04-21 19:08:16	2025-04-22 19:08:16	1
27	buzz lightyear repaint/ convierte un juguete en figura de colecci├│n premium. Parte 1	buzz lightyear repaint/ convierte un juguete en figura de colecci├│n premium. Parte 1	enytEp6Bfp8	Print&Paint Studio	Iluminacion	0	0	beginner	2025-04-22 19:08:16	2025-04-22 19:08:16	1
28	Cambios Importantes en el canal. Nueva etapa, no te pierdas este video.	Cambios Importantes en el canal. Nueva etapa, no te pierdas este video.	vA-cOUzHgF8	Print&Paint Studio	Detalles	0	0	intermediate	2025-04-22 19:08:16	2025-04-22 19:08:16	1
29	­ƒîî­ƒöÑPintar Thanos realista impreso en 3D parte 2/­ƒîî­ƒöÑPaint realistic Thanos printed in 3D part 2	­ƒîî­ƒöÑPintar Thanos realista impreso en 3D parte 2/­ƒîî­ƒöÑPaint realistic Thanos printed in 3D part 2	_UszZR7JvAk	Print&Paint Studio	Efectos Especiales	0	0	Expert	2025-04-22 19:08:16	2025-04-22 19:08:16	1
1	Ya tengo la GK 3 Ultra !! - Uniformation GK 3 ultra review	Ya tengo la GK 3 Ultra !! - Uniformation GK 3 ultra review	GaENeBmHQUc	Print&Paint Studio	Barnizado	50	110	beginner	2025-04-22 19:08:16	2025-04-22 19:08:16	1
50	Como pintar walter white 1/6 de breaking bad impreso en resina 3D/Figura custom/tutorial aerograf├¡a.	Como pintar walter white 1/6 de breaking bad impreso en resina 3D/Figura custom/tutorial aerograf├¡a.	rI7dENIqU9U	Print&Paint Studio	Peanas	0	0	Expert	2022-10-28 19:08:16	2025-04-22 19:08:16	1
51	Como pintar efecto oxido y corrosi├│n con acrilicos f├ícil y r├ípido en impresiones 3d/Aerografia	Como pintar efecto oxido y corrosi├│n con acrilicos f├ícil y r├ípido en impresiones 3d/Aerografia	crvcqSh6Kto	Print&Paint Studio	Iluminacion	0	0	beginner	2022-10-21 19:08:16	2025-04-22 19:08:16	1
52	Participa en El Reto de la Comunidad y ├ílzate con el trofeo!!!/entra a formar parte de la comunidad	Participa en El Reto de la Comunidad y ├ílzate con el trofeo!!!/entra a formar parte de la comunidad	XtpSpLMqFhQ	Print&Paint Studio	Detalles	0	0	intermediate	2022-10-14 19:08:16	2025-04-22 19:08:16	1
53	Como pintar Majin Buu Dragon ball impreso en resina 3d/tutorial aerografia en espa├▒ol/impresi├│n 3d	Como pintar Majin Buu Dragon ball impreso en resina 3d/tutorial aerografia en espa├▒ol/impresi├│n 3d	EXmEO0aVbNk	Print&Paint Studio	Efectos Especiales	0	0	Expert	2022-10-07 19:08:16	2025-04-22 19:08:16	1
54	Como pintar Superman metalizado realista//Impresi├│n resina 3d//tutorial aerograf├¡a espa├▒ol	Como pintar Superman metalizado realista//Impresi├│n resina 3d//tutorial aerograf├¡a espa├▒ol	MQLWSMlkPqE	Print&Paint Studio	Barnizado	0	0	beginner	2025-04-22 19:08:16	2025-04-22 19:08:16	1
55	Como hacer efecto agua en impresiones 3d/Diorama con agua/tutorial aerograf├¡a/impresi├│n resina 3D	Como hacer efecto agua en impresiones 3d/Diorama con agua/tutorial aerograf├¡a/impresi├│n resina 3D	clRQy3Ahg3E	Print&Paint Studio	Peanas	0	0	intermediate	2025-04-22 19:08:16	2025-04-22 19:08:16	1
69	Como Pintar Darth Maul realista impreso en 3D//Tutorial aer├│grafo en espa├▒ol	Como Pintar Darth Maul realista impreso en 3D//Tutorial aer├│grafo en espa├▒ol	HCZV7HRnsQs	Print&Paint Studio	Detalles	0	0	Expert	2021-05-28 19:08:16	2025-04-22 19:08:16	1
63	Como pintar Darth Vader 3/3 // Efecto lava con iluminacion led//Impresion 3D resina//aerograf├¡a	Como pintar Darth Vader 3/3 // Efecto lava con iluminacion led//Impresion 3D resina//aerograf├¡a	ecu6v8zH6jQ	Print&Paint Studio	Efectos Especiales	0	0	Expert	2025-04-22 19:08:16	2025-04-22 19:08:16	1
64	Como pintar Darth Vader 2/3 // Cara realista e iluminaci├│n forzada//Impresion 3D resina//aerograf├¡a	Como pintar Darth Vader 2/3 // Cara realista e iluminaci├│n forzada//Impresion 3D resina//aerograf├¡a	K6RJyGI9GGw	Print&Paint Studio	Barnizado	0	0	beginner	2025-04-22 19:08:16	2025-04-22 19:08:16	1
37	Como poner soportes en chitubox Facil 2023/Impresi├│n de resina 3D	Como poner soportes en chitubox Facil 2023/Impresi├│n de resina 3D	m08DuQzPh_E	Print&Paint Studio	Peanas	0	0	intermediate	2023-05-26 19:08:16	2025-04-22 19:08:16	1
65	Como pintar Darth Vader 1/3 //Impresi├│n 3d resina//tutorial aer├│grafo en espa├▒ol.	Como pintar Darth Vader 1/3 //Impresi├│n 3d resina//tutorial aer├│grafo en espa├▒ol.	PZ5oB8Lid30	Print&Paint Studio	Pintura Base	0	0	Expert	2025-04-22 19:08:16	2025-04-22 19:08:16	1
67	Como hacer moldes de silicona de doble cara//Robocop 1/6 Hot Toys//Tutorial moldes en espa├▒ol	Como hacer moldes de silicona de doble cara//Robocop 1/6 Hot Toys//Tutorial moldes en espa├▒ol	_V_gdFP7YaU	Print&Paint Studio	Sombreado	0	0	beginner	2021-07-16 19:08:16	2025-04-22 19:08:16	1
68	Como hacer diluyente acr├¡lico casero para aer├│grafo//Tutorial aer├│grafo en espa├▒ol//impresion 3D	Como hacer diluyente acr├¡lico casero para aer├│grafo//Tutorial aer├│grafo en espa├▒ol//impresion 3D	od_hBpxfCWA	Print&Paint Studio	Iluminacion	0	0	intermediate	2021-06-04 19:08:16	2025-04-22 19:08:16	1
70	Como cambiar el FEP r├ípido y sencillo a tu impresora de resina//Elegoo mars//Tutorial impresion 3d	Como cambiar el FEP r├ípido y sencillo a tu impresora de resina//Elegoo mars//Tutorial impresion 3d	tvpIByDpWB0	Print&Paint Studio	Efectos Especiales	0	0	beginner	2021-05-21 19:08:16	2025-04-22 19:08:16	1
71	Elegoo Saturn, como nivelar la cama y prueba de calidad//Impresora de resina 4k mono//Impresi├│n 3D	Elegoo Saturn, como nivelar la cama y prueba de calidad//Impresora de resina 4k mono//Impresi├│n 3D	j-ijacTdxcU	Print&Paint Studio	Barnizado	0	0	intermediate	2021-05-14 19:08:16	2025-04-22 19:08:16	1
72	Como pintar Wolverine realista impreso en 3D//Tutorial aer├│grafo en espa├▒ol	Como pintar Wolverine realista impreso en 3D//Tutorial aer├│grafo en espa├▒ol	zU3NClCpcoI	Print&Paint Studio	Peanas	0	0	Expert	2021-05-07 19:08:16	2025-04-22 19:08:16	1
73	Como pintar Batman realista impreso en 3D//Tutorial aer├│grafo en espa├▒ol//impresi├│n 3D	Como pintar Batman realista impreso en 3D//Tutorial aer├│grafo en espa├▒ol//impresi├│n 3D	VjUy1T7t6Hg	Print&Paint Studio	Pintura Base	0	0	beginner	2025-04-22 19:08:16	2025-04-22 19:08:16	1
74	Postprocesado de impresiones 3D FDM 2021 / Alisado con resina/ Tutorial en espa├▒ol	Postprocesado de impresiones 3D FDM 2021 / Alisado con resina/ Tutorial en espa├▒ol	xeGk31nfT7Q	Print&Paint Studio	Sombreado	0	0	intermediate	2025-04-22 19:08:16	2025-04-22 19:08:16	1
75	Como Pintar The Mandalorian/Parte 3/Tutorial Diorama Espa├▒ol Airbrush	Como Pintar The Mandalorian/Parte 3/Tutorial Diorama Espa├▒ol Airbrush	JuSHR4f7_so	Print&Paint Studio	Iluminacion	0	0	Expert	2021-03-26 19:08:16	2025-04-22 19:08:16	1
76	Como Pintar The Mandalorian/Parte dos/Tutorial espa├▒ol airbrush	Como Pintar The Mandalorian/Parte dos/Tutorial espa├▒ol airbrush	slDu8BcxWFc	Print&Paint Studio	Detalles	0	0	beginner	2021-03-12 19:08:16	2025-04-22 19:08:16	1
31	­ƒöÑCrea carteles para imprimir en 3D facil sin saber modelar­ƒÿë/impresi├│n 3D	­ƒöÑCrea carteles para imprimir en 3D facil sin saber modelar­ƒÿë/impresi├│n 3D	wbk0Upc6aT8	Print&Paint Studio	Efectos Especiales	0	0	Expert	2023-07-28 19:08:16	2025-04-22 19:08:16	1
\.


--
-- Data for Name: videos_copia; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.videos_copia (id, title, description, video_id, channel, category, technique_start_time, technique_end_time, difficulty_level, published_at, created_at) FROM stdin;
20	Elegoo Mars 5 Ultra - Ideal para imprimir miniaturas - unboxing y prueba	En el video de hoy ponemos a prueba la elegoo mars 5 ultra, impresora de resina con camara IA para miniaturas y figuras sin lineas de impresion.­ƒæçEnlaces de ...	Wh-M6XNVmuE	Print and Paint Studio	\N	\N	\N	\N	2025-04-21 13:00:32	\N
22	Como pintar a Deadpool impreso en resina 3D - STL Gratis	En el video de hoy te ense├▒o a pintar un busto de deadpool impreso en resina 3D y que puedes descargar el STL gratis.­ƒæçEnlaces de compra y descarga mas abajo...	8lRCg16ICaY	Print and Paint Studio	\N	\N	\N	\N	2025-04-21 13:00:36	\N
23	Pintura rapida y facil Goku Kid  impresa en resina	En el video de hoy te ense├▒o acomo pintar rapido y facil este Goku kid impreso en resina 3D, Ideal para iniciarse.­ƒæçEnlaces de compra y descarga mas abajo ­ƒæç...	C7PvQjhzJdQ	Print and Paint Studio	\N	\N	\N	\N	2025-04-21 13:00:38	\N
24	Ya tengo la GK 3  Ultra !! - Uniformation GK 3 ultra review	En el video de hoy veremos como es la nueva impresora de resina de gran formato Uniformation GK3 Ultra y todo lo que es capaz de hacer.­ƒæçEnlaces de compra y ...	GaENeBmHQUc	Print and Paint Studio	\N	\N	\N	\N	2025-04-21 13:00:39	\N
25	Studio Pro aprende a pintar estatuas premium	En el video de hoy te cuento como formarte y aprender el funcionamiento de un estudio de pintura profesional.Enlace directo a patreon   patreon.com/printandp...	P1OTTPIK5lU	Print and Paint Studio	\N	\N	\N	\N	2025-04-21 13:00:41	\N
27	Ojos profesionales en tus figuras Facil y rapido!/ Impresion 3D	En el video de hoy te ense├▒o a Como poner sticker en los ojos de tus figuras de manera facil y rapida en tus figuras impresas en 3D­ƒæçEnlaces de compra y desc...	zJOFSe1KCLQ	Print and Paint Studio	\N	\N	\N	\N	2025-04-21 13:00:45	\N
28	Como conseguir STL gratis y de pago en 2024 para imprimir en 3D. Descarga los mejores STL 2024	En el video de hoy te digo varias webs y patreons donde conseguir los mejores stl de 2024 gratis y de pago.­ƒæçEnlaces de compra y descarga mas abajo ­ƒæçMi tien...	2wi6ROJo-gI	Print and Paint Studio	\N	\N	\N	\N	2025-04-21 13:00:46	\N
29	Como pintar fuego con efecto OSL/Ghost rider impresion 3/DHow to paint fire with OSL/Ghost Rider	En el video de hoy te ense├▒o a como pintar fuego con efecto osl en un ghost rider impreso en resina 3d de una manera r├ípida y sencilla.­ƒæçEnlaces de compra y ...	iamJMus2N3g	Print and Paint Studio	\N	\N	\N	\N	2025-04-21 13:00:48	\N
30	Sacamos Nuestra nueva estatua de la serie dinosaurios. Prefieres en Kit o terminada?	En el video de hoy ense├▒amos nuestro nuevo proyecto, una figura basada en la seri de Dinosaurios de los a├▒os 90.Correo para informacion comercialprintpaintst...	3-R904Zgu_c	Print and Paint Studio	\N	\N	\N	\N	2025-04-21 13:00:50	\N
31	Como pintar al Correcaminos impreso en resina 3d/How to paint the Road Runner printed in 3D resin.	En el video de hoy aprenderemos a como pintar al correcaminos de los looney tunes impreso en resina 3D con pinturas acrilicas.­ƒæçEnlaces de compra y descarga ...	n_g4FetyXzc	Print and Paint Studio	\N	\N	\N	\N	2025-04-21 13:00:51	\N
19	Personalice mi aer├│grafo con el Xtool F1	En el video de hoy te ense├▒o como funciona el grabador lasr Xtool F1 y como personalice mi aerografo y mas cosas.­ƒæçEnlaces de compra y descarga mas abajo ­ƒæçL...	fBk8FUxvQSI	Print and Paint Studio	Otros	27	402	beginner	2025-04-21 13:00:30	\N
21	La mejor resoluci├│n en impresi├│n 3D - Uniformation GK3 Ultra	En el video de hoy veremos como imprime la nueva impresora de resina de gran formato Uniformation GK3 Ultra y todo lo que es capaz de hacer. impresiones 3d a...	GQesJdIuG1A	Print and Paint Studio	Otros	27	200	beginner	2025-04-21 13:00:34	\N
32	Como pintar a Piccolo impresi├│n en resina 3D/ Lucas Perez patreon	En el video de hoy aprenderemos a como pintar una figura impresa en resina 3d de piccolo esculpida por el patreon de Lucas Perez. Dragon Ball­ƒæçEnlaces de com...	RP4T5-IN95A	Print and Paint Studio	\N	\N	\N	\N	2025-04-21 13:00:53	\N
33	Pintando resina oficial de Crisanta del videojuego blasphemous/gu├¡a Aerograf├¡a en estatuas	En el video de hoy pintamos esta figura oficial en resina del personaje Crisanta del videojuego Blaphemous.­ƒæçEnlaces de compra y descarga mas abajo ­ƒæçCompra ...	5zY-Y8yGCWY	Print and Paint Studio	\N	\N	\N	\N	2025-04-21 13:00:55	\N
34	Como pintar baby yoda realista impreso en resina 3d con pintura acrilica	En el video de hoy aprenderemos a pintar con estilo realista este baby yoda impreso en resina 3d y que pintamos con pinturas acrilicas usando pincel y aerogr...	CSfifryg6HA	Print and Paint Studio	\N	\N	\N	\N	2025-04-21 13:00:56	\N
35	Como pintar Goku namek facil y rapido impreso en resina 3D con acrilicos/impresion 3D	En el video de hoy te ense├▒o de una manera facil y rapida como pintar este Goku namek impreso en resina 3d con acrilicos.­ƒæçEnlaces de compra y descarga mas a...	z8PEz4jI93s	Print and Paint Studio	\N	\N	\N	\N	2025-04-21 13:00:58	\N
36	Como pintar estilo cartoon nivel f├ícil y r├ípido en impresiones 3d /Pato lucas looney tunes.	En el video de hoy aprenderemos a pintar estilo cartoon a nivel de principiante, facil y rapido sobre este pato lucas impreso en resina 3d.­ƒæçEnlaces de compr...	pDoxeo5DrxE	Print and Paint Studio	\N	\N	\N	\N	2025-04-21 13:01:00	\N
37	Aerografos Gaahleri Ace GHAD-98D y Advanced GHAD-68. Buena calidad precio?	En el video de hoy veremos los aerografos Gaahleri Ace GHAD-98D y Advanced GHAD-68,  buena calidad precio y aptos para iniciaci├│n.­ƒæçEnlaces de compra y desca...	TdUlOdM7Zk4	Print and Paint Studio	\N	\N	\N	\N	2025-04-21 13:01:02	\N
38	Como pintar lampara aladdin impresa en 3d facil/How to paint Aladdin lamp printed in 3D easy	En el video de hoy aprenderemos a pintar la lampara y el genio de la pel├¡cula aladdin a tama├▒o real impresa en resina 3d de manera f├ícil y sencilla­ƒæçEnlaces ...	sHSTquuTHFo	Print and Paint Studio	\N	\N	\N	\N	2025-04-21 13:01:03	\N
39	Como pintar c3po impreso en 3d Facil y rapido/How to paint c3po printed in 3d Easy and fast/3d print	En el video de hoy te ense├▒o a pintar con aer├│grafo esta figura de c3po de star wars impresa en resina con pinturas acrilicas.   ­ƒæçEnlaces de compra y descar...	aOQ7TIM34do	Print and Paint Studio	\N	\N	\N	\N	2025-04-21 13:01:05	\N
40	Como pintar cell Dragon ball impreso en resina 3d/Paint cell printed in 3d resin	En el video de hoy te ense├▒o  a pintar este busto de cell de dragon ball impreso en resina de una manera simple y rapida.­ƒæçEnlaces de compra y descarga mas a...	s--u3qiNolg	Print and Paint Studio	\N	\N	\N	\N	2025-04-21 13:01:07	\N
41	Easythreed k7 Impresora econ├│mica para principiantes. Todo lo que necesitas saber antes de comprarla	EN el video de hoy prbamos la Easythreed k7, impresora economica y que se indica para principiantes. Merece la pena? Regalos para navidad y a├▒o nuevo.­ƒæçEnlac...	32_abjrxQqo	Print and Paint Studio	\N	\N	\N	\N	2025-04-21 13:01:09	\N
42	TwoTrees SP-5 V3 imprimiendo Terminator a tama├▒o real (Busto)	En el video de hoy pondremos a prueba la TwoTrees SP-5 V3 imprimiendo u busto de terminator a escala real.Compra SP-5V3 on the online shop:https://bit.ly/40Z...	SGsg7Jf2RFc	Print and Paint Studio	\N	\N	\N	\N	2025-04-21 13:01:11	\N
43	Como pintar  Kame Hame Ha y efectos de energ├¡a en figuras impresas en resina 3D transparente.	En el video de hoy te ense├▒o a pintar con aer├│grafo efectos Kame Hame Ha y de energia para figuras de dragon ball impresas en resina 3d Discord ­ƒæçEnlaces de ...	t4Qn7pKmNEo	Print and Paint Studio	\N	\N	\N	\N	2025-04-21 13:01:12	\N
44	Pinta armas realistas a escala impresas en resina /Paint realistic scale weapons printed in 3d resin	En el video de hoy aprenderemos a pintar armas a escala para nuestras figuras e impresas en 3d.­ƒæçEnlaces de compra y descarga mas abajo ­ƒæçDiscord https://dis...	g2Y3sAzVj4Y	Print and Paint Studio	\N	\N	\N	\N	2025-04-21 13:01:14	\N
45	uniformation GK2 Impresi├│n de resina en 8K. Realmente imprime tan bien? Opini├│n sincera.	En el video de hoy pondremos a prueba UniFormation GKtwo , sacaremos diferentes impresiones con configuraciones diferentes, unas a m├íxima calidad y otras a m...	SZYWeO0rKhA	Print and Paint Studio	\N	\N	\N	\N	2025-04-21 13:01:16	\N
46	Experiencia como colaboradores en Freak wars 2023. Resumen del evento y nuestro stand.	En el video de hoy hacemos un resumen de lo que vivimos en el evento freak wars 2023­ƒæçEnlaces de compra y descarga mas abajo ­ƒæçDiscord https://discord.gg/Ju2...	w83a04XcO3M	Print and Paint Studio	\N	\N	\N	\N	2025-04-21 13:01:18	\N
20	Elegoo Mars 5 Ultra - Ideal para imprimir miniaturas - unboxing y prueba	En el video de hoy ponemos a prueba la elegoo mars 5 ultra, impresora de resina con camara IA para miniaturas y figuras sin lineas de impresion.­ƒæçEnlaces de ...	Wh-M6XNVmuE	Print and Paint Studio	\N	\N	\N	\N	2025-04-21 13:00:32	\N
22	Como pintar a Deadpool impreso en resina 3D - STL Gratis	En el video de hoy te ense├▒o a pintar un busto de deadpool impreso en resina 3D y que puedes descargar el STL gratis.­ƒæçEnlaces de compra y descarga mas abajo...	8lRCg16ICaY	Print and Paint Studio	\N	\N	\N	\N	2025-04-21 13:00:36	\N
23	Pintura rapida y facil Goku Kid  impresa en resina	En el video de hoy te ense├▒o acomo pintar rapido y facil este Goku kid impreso en resina 3D, Ideal para iniciarse.­ƒæçEnlaces de compra y descarga mas abajo ­ƒæç...	C7PvQjhzJdQ	Print and Paint Studio	\N	\N	\N	\N	2025-04-21 13:00:38	\N
24	Ya tengo la GK 3  Ultra !! - Uniformation GK 3 ultra review	En el video de hoy veremos como es la nueva impresora de resina de gran formato Uniformation GK3 Ultra y todo lo que es capaz de hacer.­ƒæçEnlaces de compra y ...	GaENeBmHQUc	Print and Paint Studio	\N	\N	\N	\N	2025-04-21 13:00:39	\N
25	Studio Pro aprende a pintar estatuas premium	En el video de hoy te cuento como formarte y aprender el funcionamiento de un estudio de pintura profesional.Enlace directo a patreon   patreon.com/printandp...	P1OTTPIK5lU	Print and Paint Studio	\N	\N	\N	\N	2025-04-21 13:00:41	\N
27	Ojos profesionales en tus figuras Facil y rapido!/ Impresion 3D	En el video de hoy te ense├▒o a Como poner sticker en los ojos de tus figuras de manera facil y rapida en tus figuras impresas en 3D­ƒæçEnlaces de compra y desc...	zJOFSe1KCLQ	Print and Paint Studio	\N	\N	\N	\N	2025-04-21 13:00:45	\N
28	Como conseguir STL gratis y de pago en 2024 para imprimir en 3D. Descarga los mejores STL 2024	En el video de hoy te digo varias webs y patreons donde conseguir los mejores stl de 2024 gratis y de pago.­ƒæçEnlaces de compra y descarga mas abajo ­ƒæçMi tien...	2wi6ROJo-gI	Print and Paint Studio	\N	\N	\N	\N	2025-04-21 13:00:46	\N
29	Como pintar fuego con efecto OSL/Ghost rider impresion 3/DHow to paint fire with OSL/Ghost Rider	En el video de hoy te ense├▒o a como pintar fuego con efecto osl en un ghost rider impreso en resina 3d de una manera r├ípida y sencilla.­ƒæçEnlaces de compra y ...	iamJMus2N3g	Print and Paint Studio	\N	\N	\N	\N	2025-04-21 13:00:48	\N
30	Sacamos Nuestra nueva estatua de la serie dinosaurios. Prefieres en Kit o terminada?	En el video de hoy ense├▒amos nuestro nuevo proyecto, una figura basada en la seri de Dinosaurios de los a├▒os 90.Correo para informacion comercialprintpaintst...	3-R904Zgu_c	Print and Paint Studio	\N	\N	\N	\N	2025-04-21 13:00:50	\N
31	Como pintar al Correcaminos impreso en resina 3d/How to paint the Road Runner printed in 3D resin.	En el video de hoy aprenderemos a como pintar al correcaminos de los looney tunes impreso en resina 3D con pinturas acrilicas.­ƒæçEnlaces de compra y descarga ...	n_g4FetyXzc	Print and Paint Studio	\N	\N	\N	\N	2025-04-21 13:00:51	\N
19	Personalice mi aer├│grafo con el Xtool F1	En el video de hoy te ense├▒o como funciona el grabador lasr Xtool F1 y como personalice mi aerografo y mas cosas.­ƒæçEnlaces de compra y descarga mas abajo ­ƒæçL...	fBk8FUxvQSI	Print and Paint Studio	Otros	27	402	beginner	2025-04-21 13:00:30	\N
21	La mejor resoluci├│n en impresi├│n 3D - Uniformation GK3 Ultra	En el video de hoy veremos como imprime la nueva impresora de resina de gran formato Uniformation GK3 Ultra y todo lo que es capaz de hacer. impresiones 3d a...	GQesJdIuG1A	Print and Paint Studio	Otros	27	200	beginner	2025-04-21 13:00:34	\N
32	Como pintar a Piccolo impresi├│n en resina 3D/ Lucas Perez patreon	En el video de hoy aprenderemos a como pintar una figura impresa en resina 3d de piccolo esculpida por el patreon de Lucas Perez. Dragon Ball­ƒæçEnlaces de com...	RP4T5-IN95A	Print and Paint Studio	\N	\N	\N	\N	2025-04-21 13:00:53	\N
33	Pintando resina oficial de Crisanta del videojuego blasphemous/gu├¡a Aerograf├¡a en estatuas	En el video de hoy pintamos esta figura oficial en resina del personaje Crisanta del videojuego Blaphemous.­ƒæçEnlaces de compra y descarga mas abajo ­ƒæçCompra ...	5zY-Y8yGCWY	Print and Paint Studio	\N	\N	\N	\N	2025-04-21 13:00:55	\N
34	Como pintar baby yoda realista impreso en resina 3d con pintura acrilica	En el video de hoy aprenderemos a pintar con estilo realista este baby yoda impreso en resina 3d y que pintamos con pinturas acrilicas usando pincel y aerogr...	CSfifryg6HA	Print and Paint Studio	\N	\N	\N	\N	2025-04-21 13:00:56	\N
35	Como pintar Goku namek facil y rapido impreso en resina 3D con acrilicos/impresion 3D	En el video de hoy te ense├▒o de una manera facil y rapida como pintar este Goku namek impreso en resina 3d con acrilicos.­ƒæçEnlaces de compra y descarga mas a...	z8PEz4jI93s	Print and Paint Studio	\N	\N	\N	\N	2025-04-21 13:00:58	\N
36	Como pintar estilo cartoon nivel f├ícil y r├ípido en impresiones 3d /Pato lucas looney tunes.	En el video de hoy aprenderemos a pintar estilo cartoon a nivel de principiante, facil y rapido sobre este pato lucas impreso en resina 3d.­ƒæçEnlaces de compr...	pDoxeo5DrxE	Print and Paint Studio	\N	\N	\N	\N	2025-04-21 13:01:00	\N
37	Aerografos Gaahleri Ace GHAD-98D y Advanced GHAD-68. Buena calidad precio?	En el video de hoy veremos los aerografos Gaahleri Ace GHAD-98D y Advanced GHAD-68,  buena calidad precio y aptos para iniciaci├│n.­ƒæçEnlaces de compra y desca...	TdUlOdM7Zk4	Print and Paint Studio	\N	\N	\N	\N	2025-04-21 13:01:02	\N
38	Como pintar lampara aladdin impresa en 3d facil/How to paint Aladdin lamp printed in 3D easy	En el video de hoy aprenderemos a pintar la lampara y el genio de la pel├¡cula aladdin a tama├▒o real impresa en resina 3d de manera f├ícil y sencilla­ƒæçEnlaces ...	sHSTquuTHFo	Print and Paint Studio	\N	\N	\N	\N	2025-04-21 13:01:03	\N
39	Como pintar c3po impreso en 3d Facil y rapido/How to paint c3po printed in 3d Easy and fast/3d print	En el video de hoy te ense├▒o a pintar con aer├│grafo esta figura de c3po de star wars impresa en resina con pinturas acrilicas.   ­ƒæçEnlaces de compra y descar...	aOQ7TIM34do	Print and Paint Studio	\N	\N	\N	\N	2025-04-21 13:01:05	\N
40	Como pintar cell Dragon ball impreso en resina 3d/Paint cell printed in 3d resin	En el video de hoy te ense├▒o  a pintar este busto de cell de dragon ball impreso en resina de una manera simple y rapida.­ƒæçEnlaces de compra y descarga mas a...	s--u3qiNolg	Print and Paint Studio	\N	\N	\N	\N	2025-04-21 13:01:07	\N
41	Easythreed k7 Impresora econ├│mica para principiantes. Todo lo que necesitas saber antes de comprarla	EN el video de hoy prbamos la Easythreed k7, impresora economica y que se indica para principiantes. Merece la pena? Regalos para navidad y a├▒o nuevo.­ƒæçEnlac...	32_abjrxQqo	Print and Paint Studio	\N	\N	\N	\N	2025-04-21 13:01:09	\N
42	TwoTrees SP-5 V3 imprimiendo Terminator a tama├▒o real (Busto)	En el video de hoy pondremos a prueba la TwoTrees SP-5 V3 imprimiendo u busto de terminator a escala real.Compra SP-5V3 on the online shop:https://bit.ly/40Z...	SGsg7Jf2RFc	Print and Paint Studio	\N	\N	\N	\N	2025-04-21 13:01:11	\N
43	Como pintar  Kame Hame Ha y efectos de energ├¡a en figuras impresas en resina 3D transparente.	En el video de hoy te ense├▒o a pintar con aer├│grafo efectos Kame Hame Ha y de energia para figuras de dragon ball impresas en resina 3d Discord ­ƒæçEnlaces de ...	t4Qn7pKmNEo	Print and Paint Studio	\N	\N	\N	\N	2025-04-21 13:01:12	\N
44	Pinta armas realistas a escala impresas en resina /Paint realistic scale weapons printed in 3d resin	En el video de hoy aprenderemos a pintar armas a escala para nuestras figuras e impresas en 3d.­ƒæçEnlaces de compra y descarga mas abajo ­ƒæçDiscord https://dis...	g2Y3sAzVj4Y	Print and Paint Studio	\N	\N	\N	\N	2025-04-21 13:01:14	\N
45	uniformation GK2 Impresi├│n de resina en 8K. Realmente imprime tan bien? Opini├│n sincera.	En el video de hoy pondremos a prueba UniFormation GKtwo , sacaremos diferentes impresiones con configuraciones diferentes, unas a m├íxima calidad y otras a m...	SZYWeO0rKhA	Print and Paint Studio	\N	\N	\N	\N	2025-04-21 13:01:16	\N
46	Experiencia como colaboradores en Freak wars 2023. Resumen del evento y nuestro stand.	En el video de hoy hacemos un resumen de lo que vivimos en el evento freak wars 2023­ƒæçEnlaces de compra y descarga mas abajo ­ƒæçDiscord https://discord.gg/Ju2...	w83a04XcO3M	Print and Paint Studio	\N	\N	\N	\N	2025-04-21 13:01:18	\N
\.


--
-- Name: favorites_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.favorites_id_seq', 10, true);


--
-- Name: techniques_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.techniques_id_seq', 22, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 5, true);


--
-- Name: videos_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.videos_id_seq', 96, true);


--
-- Name: favorites favorites_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.favorites
    ADD CONSTRAINT favorites_pkey PRIMARY KEY (id);


--
-- Name: favorites favorites_user_id_video_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.favorites
    ADD CONSTRAINT favorites_user_id_video_id_key UNIQUE (user_id, video_id);


--
-- Name: techniques techniques_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.techniques
    ADD CONSTRAINT techniques_pkey PRIMARY KEY (id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: videos video_level_uc; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.videos
    ADD CONSTRAINT video_level_uc UNIQUE (video_id, difficulty_level);


--
-- Name: videos videos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.videos
    ADD CONSTRAINT videos_pkey PRIMARY KEY (id);


--
-- Name: favorites favorites_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.favorites
    ADD CONSTRAINT favorites_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: favorites favorites_video_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.favorites
    ADD CONSTRAINT favorites_video_id_fkey FOREIGN KEY (video_id) REFERENCES public.videos(id) ON DELETE CASCADE;


--
-- Name: techniques techniques_video_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.techniques
    ADD CONSTRAINT techniques_video_id_fkey FOREIGN KEY (video_id) REFERENCES public.videos(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

