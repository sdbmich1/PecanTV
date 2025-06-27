--
-- PostgreSQL database dump
--

-- Dumped from database version 14.18 (Debian 14.18-1.pgdg120+1)
-- Dumped by pg_dump version 14.18 (Debian 14.18-1.pgdg120+1)

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
-- Name: content_type; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.content_type AS ENUM (
    'FILM',
    'SERIES'
);


ALTER TYPE public.content_type OWNER TO postgres;

--
-- Name: update_updated_at_column(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.update_updated_at_column() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_updated_at_column() OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: content; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.content (
    id integer NOT NULL,
    title character varying(255) NOT NULL,
    poster_url text NOT NULL,
    trailer_url text NOT NULL,
    content_url text NOT NULL,
    description text,
    type public.content_type NOT NULL,
    runtime integer NOT NULL,
    genre_id integer,
    rating_id integer,
    release_date date,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.content OWNER TO postgres;

--
-- Name: content_genres; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.content_genres (
    id integer NOT NULL,
    content_id integer,
    genre_id integer,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.content_genres OWNER TO postgres;

--
-- Name: content_genres_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.content_genres_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.content_genres_id_seq OWNER TO postgres;

--
-- Name: content_genres_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.content_genres_id_seq OWNED BY public.content_genres.id;


--
-- Name: content_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.content_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.content_id_seq OWNER TO postgres;

--
-- Name: content_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.content_id_seq OWNED BY public.content.id;


--
-- Name: episodes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.episodes (
    id integer NOT NULL,
    series_id integer NOT NULL,
    season_number integer NOT NULL,
    episode_number integer NOT NULL,
    title character varying(255) NOT NULL,
    description text,
    content_url text NOT NULL,
    thumbnail_url text,
    runtime integer,
    air_date date,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.episodes OWNER TO postgres;

--
-- Name: episodes_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.episodes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.episodes_id_seq OWNER TO postgres;

--
-- Name: episodes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.episodes_id_seq OWNED BY public.episodes.id;


--
-- Name: favorites; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.favorites (
    id integer NOT NULL,
    user_id integer NOT NULL,
    content_id integer NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
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
-- Name: genres; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.genres (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    description text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.genres OWNER TO postgres;

--
-- Name: genres_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.genres_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.genres_id_seq OWNER TO postgres;

--
-- Name: genres_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.genres_id_seq OWNED BY public.genres.id;


--
-- Name: ratings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.ratings (
    id integer NOT NULL,
    code character varying(10) NOT NULL,
    description text,
    min_age integer,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.ratings OWNER TO postgres;

--
-- Name: ratings_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.ratings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ratings_id_seq OWNER TO postgres;

--
-- Name: ratings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.ratings_id_seq OWNED BY public.ratings.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    email character varying(255) NOT NULL,
    first_name character varying(100) NOT NULL,
    last_name character varying(100) NOT NULL,
    password_hash character varying(255) NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
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
-- Name: content id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.content ALTER COLUMN id SET DEFAULT nextval('public.content_id_seq'::regclass);


--
-- Name: content_genres id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.content_genres ALTER COLUMN id SET DEFAULT nextval('public.content_genres_id_seq'::regclass);


--
-- Name: episodes id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.episodes ALTER COLUMN id SET DEFAULT nextval('public.episodes_id_seq'::regclass);


--
-- Name: favorites id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.favorites ALTER COLUMN id SET DEFAULT nextval('public.favorites_id_seq'::regclass);


--
-- Name: genres id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.genres ALTER COLUMN id SET DEFAULT nextval('public.genres_id_seq'::regclass);


--
-- Name: ratings id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ratings ALTER COLUMN id SET DEFAULT nextval('public.ratings_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: content; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.content (id, title, poster_url, trailer_url, content_url, description, type, runtime, genre_id, rating_id, release_date, created_at, updated_at) FROM stdin;
1	Carnival of Souls	https://storage.googleapis.com/pecantv_title_images/Carnival-of-souls_Title-Img.png	https://storage.googleapis.com/pecantv_trailers/carnival-of-souls_trailer-59s.mp4	https://storage.googleapis.com/pecantv_features/carnival-of-souls_2p-1080-wCreditsFinal.mp4	A classic horror film about a woman who is haunted by strange visions after a car accident.	FILM	78	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
3	Get Christie Love	https://storage.googleapis.com/pecantv_title_images/GetChristieLove-Feature-Img-16x9.png	https://storage.googleapis.com/pecantv_trailers/GetChristieLove_Trailer-final-60s.mp4	https://storage.googleapis.com/pecantv_features/Get-Christie-Love_2P-720p-fullCredits.mp4	A tough undercover cop takes on the criminal underworld in this action-packed drama.	FILM	60	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
4	Night of the Living Dead	https://storage.googleapis.com/pecantv_title_images/NLD_title-Img-color.png	https://storage.googleapis.com/pecantv_trailers/NLD-color_1080-trailer-40s.mp4	https://storage.googleapis.com/pecantv_features/NLD-color_2p-1080-with-credits.mp4	A group of people trapped in a farmhouse must fight off a horde of flesh-eating zombies.	FILM	96	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
7	Black Brigade	https://storage.googleapis.com/pecantv_title_images/Black-Brigade-Feature-Img.png	https://storage.googleapis.com/pecantv_trailers/BlackBrigade_Trailer_35sFinal.mp4	https://storage.googleapis.com/pecantv_features/Black-Brigade_2P-720p-fullCredits.mp4	A racist officer is put in charge of a squad of black troops charged with taking an important bridge from the Germans.	FILM	70	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
8	Dementia-13	https://storage.googleapis.com/pecantv_title_images/dementia-13_Title-Img.png	https://storage.googleapis.com/pecantv_trailers/dementia-13_trailer-60s.mp4	https://storage.googleapis.com/pecantv_features/dementia-13_2p-1080-24fps-wCredits.mp4	A scheming widow hatches a bold plan to acquire her late husband's inheritance, unaware that she is being targeted by an ax murderer who lurks in the family's estate.	FILM	74	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
9	Little Shop of Horrors	https://storage.googleapis.com/pecantv_title_images/Little-Shop-of-Horrors_Title-Img-colorbk.png	https://storage.googleapis.com/pecantv_trailers/Little-Shop-of-Horrors_trailer-56s.mp4		A farce about a florist's assistant who cultivates a plant that feeds on human blood. 	FILM	60	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
10	The Last Time I Saw Paris	https://storage.googleapis.com/pecantv_title_images/Last-Time-I-Saw-Paris_Title_Img-1920x1080.jpg		https://storage.googleapis.com/pecantv_features/Last-Time-I-Saw-Paris_2p-1080-withCredits2.mp4	An American journalist returns to Paris - a city that gave him true love and deep grief.	FILM	112	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
12	Jesse Owens II			https://storage.googleapis.com/pecantv_features/Jesse-Owens-Part-II_2P-720p-fullCredits.mp4		FILM	0	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
14	Man with the Golden Arm	https://storage.googleapis.com/pecantv_title_images/Man-with-the-Golden-Arm-Title-Img.png		https://storage.googleapis.com/pecantv_features/The_Man_with_the_Golden_Arm_2p_1080_full_credits.mp4	A junkie must face his true self to kick his drug addiction.	FILM	119	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
58	Hercules in the Haunted World	https://storage.googleapis.com/pecantv_title_images/Hercules-in-the-Haunted-World_Title-Img.png	https://storage.googleapis.com/pecantv_trailers/Hercules-in-the-Haunted-World_trailer-60s.mp4	https://storage.googleapis.com/pecantv_features/Hercules-in-the-Haunted-World_1080-24fps-wCredits.mp4	Hercules must journey into Hades itself to retrieve the magic stone that will free his love from the powers of darkness.	FILM	80	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
59	Hercules Against the Moon Men	https://storage.googleapis.com/pecantv_title_images/Hercules-against-the-Moon-Men_Title-Img.png	https://storage.googleapis.com/pecantv_trailers/Hercules-Against-the-Moon-Men_trailer-58s.mp4		Hercules is summoned to oppose the evil Queen Samara, who has allied herself with aliens and is sacrificing her own people in a bid to awaken a moon goddess.	FILM	86	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
16	Mr. Mean	https://storage.googleapis.com/pecantv_title_images/MrMean_feature-Img.jpg		https://storage.googleapis.com/pecantv_features/MrMean_2P-1080p-fullCredits.mp4	Sent to kill a crime boss in Rome, a hit man becomes a target himself.	FILM	79	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
17	Murder in Harlem	https://storage.googleapis.com/pecantv_title_images/Murder-in-Harlem-Feature-Img.png			A black night watchman at a chemical factory finds the body of a murdered white woman. After he reports it, he finds himself accused of the murder.	FILM	102	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
18	Mutiny	https://storage.googleapis.com/pecantv_title_images/Mutiny_title-img.png		https://storage.googleapis.com/pecantv_features/Mutiny_1080-wCredits.mp4		FILM	0	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
23	Red House	https://storage.googleapis.com/pecantv_title_images/Red-House_title-img.png		https://storage.googleapis.com/pecantv_features/Red-House_2p-1080-wCredits.mp4	An old man and his sister are concealing a terrible secret from their adopted teen daughter, concerning a hidden abandoned farmhouse, located deep in the woods.	FILM	100	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
25	Scrooge	https://storage.googleapis.com/pecantv_title_images/Scrooge_title-img.png		https://storage.googleapis.com/pecantv_features/Scrooge_2p-1080-12fps-wCredits.mp4	A musical retelling of Charles Dickens' classic novel about an old bitter miser taken on a journey of self-redemption, courtesy of several mysterious Christmas apparitions.	FILM	110	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
27	SH-Dressed to Kill			https://storage.googleapis.com/pecantv_features/SH-Dressed-to-Kill_1P-1080-full-credits.mp4		FILM	0	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
61	Hell in Normandy	https://storage.googleapis.com/pecantv_title_images/Hell-in-Normandy_title-Img-1920x1080.png		https://storage.googleapis.com/pecantv_features/Hell-in-Normandy_2p-1080-with-credits.mp4	a well-meaning war film with a good premise and enough good acting, suspense and violent action to keep it entertaining.	FILM	88	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
62	Ghost Squad	https://storage.googleapis.com/pecantv_title_images/Ghost-Squad_title-img.png			The adventures of the agents of Scotland Yard's secret undercover crime unit, dubbed "The Ghost Squad".	SERIES	50	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
66	Duel in the Sun	https://storage.googleapis.com/pecantv_title_images/Duel-in-the-Sun_title-img.png		https://storage.googleapis.com/pecantv_features/Duel-in-the-Sun_2p-1080-wCredits.mp4	Beautiful, biracial Pearl Chavez becomes the ward of her dead father's first love and finds herself torn between two brothers, one good and the other bad.	FILM	120	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
67	Dragon Young Master	https://storage.googleapis.com/pecantv_title_images/Dragon-Young-Master_title-img1.png		https://storage.googleapis.com/pecantv_features/Dragon-the-Young-Master_2p-1080-with-credits.mp4	A fighter teams up with the daughter of the man who killed his father in 1920s Manchuria.	FILM	118	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
69	Dick Tracy 	https://storage.googleapis.com/pecantv_title_images/Dick-Tracy_Title-Img.jpg	https://storage.googleapis.com/pecantv_trailers/Dick-Tracy_Trailer-1min.mp4	https://storage.googleapis.com/pecantv_features/Dick-Tracy_2p-1080-credit-role.mp4	Police detective Dick Tracy must identify and apprehend a serial killer known as Splitface.	FILM	61	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
70	Curse of the Aztec Mummy	https://storage.googleapis.com/pecantv_title_images/Curse-of-the-Aztec-Mummy_title-img.jpg		https://storage.googleapis.com/pecantv_features/The-Curse-of-the-Aztec-Mummy_2p-1080-credit-role.mp4	The evil Dr. Krupp, once again trying to get possession of the Aztec princess Xochitl's jewels, hypnotizes her current reincarnation, Flor, to get her to reveal the jewels' location - Xochitl's tomb.	FILM	61	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
71	Creature	https://storage.googleapis.com/pecantv_title_images/Creature_title-img.png	https://storage.googleapis.com/pecantv_trailers/Creature_trailer-59s.mp4		Married woman miscarries after dog attack. Vacation helps her bond with stray dog of same breed.	FILM	98	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
72	Count of Monte Cristo	https://storage.googleapis.com/pecantv_title_images/Count-of-Monte-Cristo-sword-fleur-de-lis_title-img.png			Falsely imprisoned, Edmond Dantes encounters an inmate with knowledge of a hidden treasure. After escaping, he seeks the fortune to avenge his unjust incarceration.	SERIES	28	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
73	Cosmos	https://storage.googleapis.com/pecantv_title_images/Cosmos-fullLogo_blk.png	https://storage.googleapis.com/pecantv_trailers/Cosmos_16sec-Trailer.mov		Captain Alex Hamilton investigates a strange signal on Earth and a UFO above Antarctica, discovering a giant robot enslaving humanoids and observing Earth from an unknown planet.	FILM	86	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
74	Chinese Hercules	https://storage.googleapis.com/pecantv_title_images/Chinese-Hercules_title-img.png		https://storage.googleapis.com/pecantv_features/Chinese-Hercules_2p-1080-with-credits.mp4	A martial arts fighter, haunted by his past, takes a job as a dock worker in a small village.	FILM	86	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
75	Captain Scarlett	https://storage.googleapis.com/pecantv_title_images/Captain-Scarlett_title-img.png		https://storage.googleapis.com/pecantv_features/Captain-Scarlett_1080-wCredits.mp4	Post-Napoleonic Wars, Scarlett returns to southern France. He rescues a princess from a forced marriage, defends locals from the Duke of Corlais' persecution, and ultimately overthrows the Duke's oppressive rule.	FILM	74	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
34	The Chase	https://storage.googleapis.com/pecantv_title_images/The-Chase_title-img.png		https://storage.googleapis.com/pecantv_features/The-Chase_2p-1080-wCredits.mp4	Chuck Scott gets a job as chauffeur to tough guy Eddie Roman; but Chuck's involvement with Eddie's fearful wife becomes a nightmare.	FILM	84	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
35	The Flame	https://storage.googleapis.com/pecantv_title_images/The-Flame_title-img.png			A woman falls for the victim of an intended blackmail plot.	FILM	96	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
36	The Master	https://storage.googleapis.com/pecantv_title_images/The-Master_title-img.png				FILM	0	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
37	The Scarlet Pimpernel	https://storage.googleapis.com/pecantv_title_images/The-Scarlet-Pimpernel_title-img.jpg			A noblewoman discovers her husband is The Scarlet Pimpernel, a vigilante who rescues aristocrats from the blade of the guillotine.	FILM	96	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
38	The Screaming Skull	https://storage.googleapis.com/pecantv_title_images/The-Screaming-Skull_title-img.png		https://storage.googleapis.com/pecantv_features/The-Screaming-Skull_2p-1080-withCredits.mp4	A newly-wed woman believes the ghost of her husband's deceased first wife is haunting her at an eerie Southern mansion.	FILM	67	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
77	Brother from Another Planet	https://storage.googleapis.com/pecantv_title_images/Brother-from-Another-Planet-Feature-Img.jpg			A mute alien with the appearance of a black human is chased by outer-space bounty hunters through the streets of Harlem.	FILM	144	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
78	Bonanza	https://storage.googleapis.com/pecantv_title_images/Bonanza-Series-Image.jpg			The Wild West adventures of Ben Cartwright and his sons as they run and defend their Nevada ranch while helping the surrounding community.	SERIES	48	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
79	Beyond Christmas	https://storage.googleapis.com/pecantv_title_images/Beyond-Christmas_title-image.png		https://storage.googleapis.com/pecantv_features/Beyond-Christmas_2p-1080-wCredits.mp4	Three benevolent spirits work behind the scenes to ensure that a young couple, who they met at Christmas, will find a way to be together and have a love that will last forever.	FILM	78	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
80	Beat the Devil	https://storage.googleapis.com/pecantv_title_images/Beat-the-Devil_title-img.png		https://storage.googleapis.com/pecantv_features/Beat-the-Devil_2p-1080-wCredits.mp4	On their way to Africa are a group of rogues who hope to get rich there, and a seemingly innocent British couple.	FILM	88	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
81	A Christmas Wish	https://storage.googleapis.com/pecantv_title_images/A-Christmas-Wish_title-image.png		https://storage.googleapis.com/pecantv_features/A-Christmas-Wish_1080-12fps-wCredits.mp4	A charming and wholesome 1950 holiday film about a New York family (led by Durante) who are down on their luck at Christmas time.	FILM	86	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
82	Count Duckula				The misadventures of a vegetarian vampire duck and his servants.	SERIES	22	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
83	Dick Tracy vs Cueball		https://storage.googleapis.com/pecantv_trailers/Dick-Tracy-vs-Cueball_Trailer-30s.mp4	https://storage.googleapis.com/pecantv_features/Dick-Tracy-vs-Cueball_2p-1080-credit-role.mp4		FILM	0	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
84	Inframan		https://storage.googleapis.com/pecantv_trailers/Inframan_24sec-Trailer.mov			FILM	0	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
85	The Stranger			https://storage.googleapis.com/pecantv_features/The-Stranger_2p-1080-wCredits.mp4	Expensive diamonds are stolen but before the thief can fence them he is strangled by ex-con Cueball, who then takes the gems and continues murdering people he believes are trying to swindle him.	FILM	60	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
86	The Adventures of Commando Cody	https://storage.googleapis.com/pecantv_title_images/CommandoCodyTitleImg-061925.jpg			Dangerous climate changes are ravaging Earth and the U.S. government requests an investigation by masked super-scientist Commando Cody. He discovers that the disasters are being caused by space-alien forces from unknown planetary origins	SERIES	22	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
20	Passing	https://storage.googleapis.com/pecantv_title_images/Passing_feature-Img.jpg		https://storage.googleapis.com/pecantv_features/PASSING_2P-1080p-fullCredits.mp4		FILM	0	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
39	The Steel Claw	https://storage.googleapis.com/pecantv_title_images/The-Steel-Claw_Title-Img-1920x1080.png			American soldier leads deadly mission into Phillippines to rescue US General held captive by Japanese during WWII.	FILM	95	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
40	The Unholy Four	https://storage.googleapis.com/pecantv_title_images/The-Unholy-Four_title-img.png		https://storage.googleapis.com/pecantv_features/The-Unholy-Four_1080-wCredits.mp4	A man on a fishing trip with three of his friends receives a blow to the head that makes him lose his memory.	FILM	80	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
41	Too Late for Tears	https://storage.googleapis.com/pecantv_title_images/Too-Late-for-Tears_title-img.png		https://storage.googleapis.com/pecantv_features/Too-Late-for-Tears_2p-1080-wCredits.mp4	Through a fluke circumstance, a ruthless woman stumbles across a suitcase filled with $60,000, and is determined to hold onto it even if it means murder.	FILM	96	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
42	William Tell	https://storage.googleapis.com/pecantv_title_images/William-Tell_Title-Img.png			Depicts the legend of William Tell, who, as the stories say, shot an apple off of his son's head and lead the rebellion to free Switzerland.	SERIES	28	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
43	Woman on the Run	https://storage.googleapis.com/pecantv_title_images/Woman-on-the-Run_title-img.png		https://storage.googleapis.com/pecantv_features/Woman-on-the-Run_2p-1080-wCredits.mp4	Frank Johnson becomes an eyewitness to a murder. He's pursued around San Francisco by his wife, the police, and the killer.	FILM	76	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
44	Marlowe	https://storage.googleapis.com/pecantv_title_images/Marlowe_title-img.png			A crime series, featuring the cases of the fictional detective Philip Marlowe.	SERIES	28	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
45	Mike Hammer	https://storage.googleapis.com/pecantv_title_images/MikeHammer_Title-Img-with-title.png			The adventures of Mickey Spillane's tough-talking, brawling, skirt-chasing private detective Mike Hammer, who's always ready to use his fists on a "mug" or his charm on a "skirt" to get the case solved.	SERIES	28	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
46	Man With a Camera	https://storage.googleapis.com/pecantv_title_images/ManWithACameraSeries_Title-Img-with-title.png			Former combat cameraman Mike Kovac is now freelance photographer in New York City, specializing in dangerous assignments others shy away from.	SERIES	28	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
47	Lying Lips	https://storage.googleapis.com/pecantv_title_images/Lying-Lips-Feature-Img.png			A nightclub singer refuses to "date" customers, so she's framed for the murder of her aunt, convicted of the killing and sent to prison.	FILM	77	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
68	Dragnet	https://storage.googleapis.com/pecantv_title_images/Dragnet_title-img.png			Police Detective Sgt. Joe Friday and his partners investigate crimes in Los Angeles.	SERIES	58	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
2	Charade	https://storage.googleapis.com/pecantv_title_images/CHARADE-titleImg-Logo.jpg		https://storage.googleapis.com/pecantv_features/Charade-the-animated-movie_2p-1080-wCredits.mp4	A romantic comedy mystery involving murder, romance, and Parisian intrigue.	FILM	113	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
5	Lola Colt	https://storage.googleapis.com/pecantv_title_images/Lola-Colt_title-img.png		https://storage.googleapis.com/pecantv_features/Lola-Colt_1080-wCredits.mp4	A mysterious woman gunslinger rides into a troubled western town and changes its fate.	FILM	88	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
11	Jesse Owens	https://storage.googleapis.com/pecantv_title_images/Jesse-Owens-Feature-Img.png		https://storage.googleapis.com/pecantv_features/Jesse-Owens-Part-I_2P-720p-fullCredits.mp4	The full story of Jesse Owens, four-time Olympic gold medallist and star of the 1936 Berlin Olympics, as told through the lens of an investigator into Owen’s life at the behest of a judicial mandate. Here we see Owens forced to battle overt and covert racism throughout his life and his battling through difficulties.	FILM	174	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
13	Love Affair	https://storage.googleapis.com/pecantv_title_images/Love-Affair_title-image.png	https://storage.googleapis.com/pecantv_trailers/Love-Affair_Trailer-2min.mp4	https://storage.googleapis.com/pecantv_features/Love-Affair_2p-1080-12fps-wCredits.mp4	A French playboy and an American former nightclub singer fall in love aboard a ship.	FILM	88	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
24	Scarlett Street	https://storage.googleapis.com/pecantv_title_images/Scarlet-Street_Title-Img2.jpg			A man in mid-life crisis befriends a young woman, though her fiancé persuades her to con him out of the fortune they mistakenly assume he possesses.	FILM	102	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
30	Shockproof	https://storage.googleapis.com/pecantv_title_images/Shockproof_title-img.png			A parole officer falls in love with his client, a ravishing blonde who served time for murder, and he's determined to help her go straight despite her interfering criminal boyfriend.	FILM	79	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
31	Silent Night Bloody Night	https://storage.googleapis.com/pecantv_title_images/Silent-Night-Bloody-Night_title-img-Logo.png	https://storage.googleapis.com/pecantv_trailers/Silent-Night-Bloody-Night_-1080-Trailer.mp4		A man inherits a mansion which once was a mental home. He visits the place and begins to investigate some crimes that happened in old times, scaring the people living in the region.	FILM	86	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
15	Master of the Flying Guillotine	https://storage.googleapis.com/pecantv_title_images/Master-of-the-Flying-Guillotine_title-img.png		https://storage.googleapis.com/pecantv_features/Master-of-the-Flying-Guillotine_2p-1080-with-credits.mp4	A vengeful and blind Kung Fu expert travels to a village where a martial arts contest is being held and vows to behead every one armed man he comes across.	FILM	81	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
19	One Eyed Jacks	https://storage.googleapis.com/pecantv_title_images/One-Eyed-Jacks_title-img.png		https://storage.googleapis.com/pecantv_features/One-Eyed-Jacks_2p-1080-wCredits.mp4	After successfully robbing a bank in Sonora, Mexico, Dad Longworth abandons his surviving partner, Rio, who is caught and imprisoned by the Mexican Federales.	FILM	141	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
21	Petrocelli	https://storage.googleapis.com/pecantv_title_images/Petrocelli_title-img.jpg			A Harvard-educated lawyer from Boston sets up shop in a small Arizona town.	SERIES	44	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
22	Prisoners of the Lost Planet	https://storage.googleapis.com/pecantv_title_images/Prisoners-of-the-Lost-Planet_title-img.jpg		https://storage.googleapis.com/pecantv_features/Prisoners-of-the-Lost-Planet_2p-1080-credit-role.mp4	Three people are transported into a parallel reality, where they find they must use modern technology, but medieval weapons, in order to save the citizenry from a murderous warlord.	FILM	94	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
26	Sherlock Holmes - Terror By Night	https://storage.googleapis.com/pecantv_title_images/Sherlock-Holmes-Series-Img.jpg		https://storage.googleapis.com/pecantv_features/SH-Terror-by-Night_1P-1080-full-credits.mp4	When the fabled Star of Rhodesia diamond is stolen on a London to Edinburgh train and the son of its owner is murdered, Sherlock Holmes must discover which of his suspicious fellow passengers is responsible.	FILM	76	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
55	Joshua Black Rider	https://storage.googleapis.com/pecantv_title_images/Joshua-Black-Rider-Feature-Img.png	https://storage.googleapis.com/pecantv_trailers/Joshua-the-Black-Rider_73sec-Trailer.mov	https://storage.googleapis.com/pecantv_features/Joshua-Black-Rider_2P-720p-fullCredits.mp4	A black soldier returns from fighting for the Union in the Civil War only to find out that his mother has been murdered by a gang of white thugs.	FILM	98	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
56	Jackie Robinson	https://storage.googleapis.com/pecantv_title_images/Jackie-Robinson_image1.jpg		https://storage.googleapis.com/pecantv_features/JRS-animated-film_2P-1080p-fullCredits.mp4	Biography of Jackie Robinson, the first black major league baseball player in the 20th century. Traces his career in the negro leagues and the major leagues.	FILM	76	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
57	House on Haunted Hill	https://storage.googleapis.com/pecantv_title_images/House-on-Haunted-Hill_title-img.png		https://storage.googleapis.com/pecantv_features/House-on-Haunted-Hill_2p-1080-withCredits.mp4	A millionaire offers $10,000 to five people who agree to be locked in a large, spooky, rented house overnight with him and his wife.	FILM	77	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
60	Hercules 	https://storage.googleapis.com/pecantv_title_images/Hercules_title-img.jpg	https://storage.cloud.google.com/pecantv_trailers/Hercules_trailer-33s-1080-12fps.mp4			FILM	0	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
6	Joe Bullett	https://storage.googleapis.com/pecantv_title_images/Joe-Bullett-Feature-Img.png	https://storage.googleapis.com/pecantv_trailers/Joe-Bullett_trailer-1min.mp4	https://storage.googleapis.com/pecantv_features/Joe-Bullett_1P-720p-fullCredits.mp4	Joe Bullett is called in to stop a gangster from sabotaging a soccer match.	FILM	79	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
28	SH-Secret Weapon			https://storage.googleapis.com/pecantv_features/SH-Secret-Weapon_1P-1080-full-credits.mp4		FILM	0	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
29	SH-The Woman in Green			https://storage.googleapis.com/pecantv_features/SH-The-Woman-in-Green_1P-1080-full-credits.mp4		FILM	0	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
32	Snake and Crane Secret	https://storage.googleapis.com/pecantv_title_images/Snake-and-Crane-Secret_title-img.png		https://storage.googleapis.com/pecantv_features/Snake-and-Crane-Secret_2p-1080-with-credits.mp4	A martial arts book, which Hsu Yin-Fung carries, is being highly sought by various clans and gangs, but he is in pursuit of someone himself.	FILM	94	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
33	The Buccaneers	https://storage.googleapis.com/pecantv_title_images/The-Buccaneers_title-img.png				FILM	0	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
48	Lost Boundaries	https://storage.googleapis.com/pecantv_title_images/Lost-Boundaries-Feature-Img2.png		https://storage.googleapis.com/pecantv_features/Lost-Boundaries_2P-720p-fullCredits.mp4	A fair-skinned African American doctor faces discrimination in 1940s America.	FILM	96	9	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
49	Longstreet	https://storage.googleapis.com/pecantv_title_images/Longstreet_title-img.png			The cases of a blind insurance investigator.	SERIES	80	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
50	Long Ranger	https://storage.googleapis.com/pecantv_title_images/LoneRanger_TitleImage.png			The adventures of the masked Texas Ranger and his Native American partner.	SERIES	28	32	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
51	Little Lord Fauntleroy	https://storage.googleapis.com/pecantv_title_images/Little-Lord-Fauntleroy_title-img.jpg			An American boy turns out to be the long-lost heir of a British fortune. He is sent to live with the cold and unsentimental Lord, who oversees the trust.	FILM	100	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
52	Legend of the Eight Samurai	https://storage.googleapis.com/pecantv_title_images/Legend-of-the-Eight-Samurai_title-img.png		https://storage.googleapis.com/pecantv_features/Legend-of-the-Eight-Samurai_2p-1080-with-credits.mp4	Princess Shizu was born under a terrible curse. Only the eight legendary samurai, hailing from across Japan, can protect her from an ancient supernatural clan to fulfill their destinies as foretold by prophecy.	FILM	132	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
53	Lady Frankenstein	https://storage.googleapis.com/pecantv_title_images/Lady-Frankenstein_Title-Img.png	https://storage.googleapis.com/pecantv_trailers/Lady-Frankenstein-trailer-clip-50s.mp4		Baron Frankenstein's daughter and his assistant/her lover continue his experiments in an attempt to rebuild his legacy after he is killed by his psychotic, murderous first monster.	FILM	96	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
54	KC Confidential	https://storage.googleapis.com/pecantv_title_images/KC-Confidential_title-img.png		https://storage.googleapis.com/pecantv_features/KC-Confidential_2p-1080-wCredits.mp4	An ex-con trying to go straight is framed for a million dollar armored car robbery and must go to Mexico in order to unmask the real culprits.	FILM	97	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
63	Get the Sheriff	https://storage.googleapis.com/pecantv_title_images/Get-the-Sheriff-Feature-Img.jpg			A rape case opens racial divisions in a small town. A black sheriff and his white deputy investigate allegations that a white businessman raped a black college student.	FILM	60	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
64	Frederick Douglass	https://storage.googleapis.com/pecantv_title_images/Frederick-Douglass_title-img.png			In 1872 in a church in Ohio, former slave Frederick Douglass shares his breathtaking journey from slavery to life as a statesman.	FILM	60	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
65	Flight to Mars	https://storage.googleapis.com/pecantv_title_images/Flight-to-Mars_title-img.jpg		https://storage.googleapis.com/pecantv_features/FLIGHT-TO-MARS_2p-1080.mp4	Five astronauts successfully fly to Mars where they encounter seemingly friendly and advanced inhabitants who harbor covert plans to use their ship to invade Earth.	FILM	70	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
76	Captain Kidd	https://storage.googleapis.com/pecantv_title_images/Captain-Kidd_title-img.jpg			The unhistorical adventures of pirate Captain Kidd revolve around treasure and treachery.	FILM	88	\N	\N	\N	2025-06-22 01:33:02.402144+00	2025-06-22 22:05:48.47775+00
\.


--
-- Data for Name: content_genres; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.content_genres (id, content_id, genre_id, created_at) FROM stdin;
1	48	9	2025-06-22 01:50:07.321355+00
2	50	32	2025-06-22 01:50:07.321355+00
3	2	31	2025-06-22 01:50:40.112933+00
4	5	7	2025-06-22 01:50:40.112933+00
5	20	9	2025-06-22 01:50:40.112933+00
6	13	24	2025-06-22 01:50:40.112933+00
7	11	29	2025-06-22 01:50:40.112933+00
8	82	6	2025-06-22 01:50:40.112933+00
9	25	6	2025-06-22 01:50:40.112933+00
18	57	18	2025-06-22 04:29:39.579871+00
19	53	18	2025-06-22 04:29:39.579871+00
20	38	18	2025-06-22 04:29:39.579871+00
21	31	18	2025-06-22 04:29:39.579871+00
22	8	18	2025-06-22 04:29:39.579871+00
23	70	18	2025-06-22 04:29:39.579871+00
24	71	18	2025-06-22 04:29:39.579871+00
27	54	7	2025-06-22 04:29:39.579871+00
28	17	7	2025-06-22 04:29:39.579871+00
29	24	7	2025-06-22 04:29:39.579871+00
30	30	7	2025-06-22 04:29:39.579871+00
31	41	7	2025-06-22 04:29:39.579871+00
32	43	7	2025-06-22 04:29:39.579871+00
33	34	31	2025-06-22 04:29:39.579871+00
34	85	31	2025-06-22 04:29:39.579871+00
38	47	9	2025-06-22 04:29:39.579871+00
39	10	9	2025-06-22 04:29:39.579871+00
40	35	9	2025-06-22 04:29:39.579871+00
41	40	9	2025-06-22 04:29:39.579871+00
42	64	8	2025-06-22 04:29:39.579871+00
43	56	29	2025-06-22 04:29:39.579871+00
46	9	6	2025-06-22 04:29:39.579871+00
47	51	6	2025-06-22 04:29:39.579871+00
48	59	2	2025-06-22 04:29:39.579871+00
49	58	2	2025-06-22 04:29:39.579871+00
50	74	1	2025-06-22 04:29:39.579871+00
51	67	1	2025-06-22 04:29:39.579871+00
52	15	1	2025-06-22 04:29:39.579871+00
53	32	1	2025-06-22 04:29:39.579871+00
54	39	1	2025-06-22 04:29:39.579871+00
55	76	2	2025-06-22 04:29:39.579871+00
56	75	2	2025-06-22 04:29:39.579871+00
57	37	2	2025-06-22 04:29:39.579871+00
58	42	2	2025-06-22 04:29:39.579871+00
59	86	2	2025-06-22 04:29:39.579871+00
61	19	32	2025-06-22 04:29:39.579871+00
62	66	32	2025-06-22 04:29:39.579871+00
63	63	32	2025-06-22 04:29:39.579871+00
64	55	32	2025-06-22 04:29:39.579871+00
65	65	26	2025-06-22 04:29:39.579871+00
66	22	26	2025-06-22 04:29:39.579871+00
67	77	26	2025-06-22 04:29:39.579871+00
68	52	19	2025-06-22 04:29:39.579871+00
69	16	19	2025-06-22 04:29:39.579871+00
70	26	20	2025-06-22 04:29:39.579871+00
71	78	32	2025-06-22 04:29:39.579871+00
72	68	7	2025-06-22 04:29:39.579871+00
73	62	7	2025-06-22 04:29:39.579871+00
74	49	9	2025-06-22 04:29:39.579871+00
75	46	9	2025-06-22 04:29:39.579871+00
76	44	7	2025-06-22 04:29:39.579871+00
77	45	7	2025-06-22 04:29:39.579871+00
78	21	7	2025-06-22 04:29:39.579871+00
79	72	2	2025-06-22 04:29:39.579871+00
86	80	9	2025-06-22 04:29:39.579871+00
87	73	8	2025-06-22 04:29:39.579871+00
88	6	7	2025-06-22 04:29:39.579871+00
89	86	1	2025-06-22 04:34:59.120979+00
90	2	9	2025-06-22 04:34:59.120981+00
91	42	1	2025-06-22 04:34:59.120982+00
92	5	9	2025-06-22 04:53:35.98497+00
93	34	9	2025-06-22 04:53:35.984984+00
94	77	2	2025-06-22 04:53:35.984984+00
95	55	1	2025-06-22 04:53:35.984984+00
96	85	9	2025-06-22 04:53:35.984985+00
97	52	1	2025-06-22 04:53:35.984985+00
98	26	31	2025-06-22 04:53:35.984985+00
99	54	9	2025-06-22 04:53:35.984987+00
100	57	31	2025-06-22 04:53:35.984988+00
101	17	9	2025-06-22 04:53:35.984988+00
102	16	1	2025-06-22 04:53:35.984988+00
103	61	9	2025-06-22 04:53:35.984988+00
104	53	31	2025-06-22 04:53:35.984989+00
105	24	9	2025-06-22 04:53:35.984989+00
106	15	19	2025-06-22 04:53:35.984989+00
107	58	1	2025-06-22 04:53:35.98499+00
108	7	9	2025-06-22 04:53:35.98499+00
109	38	31	2025-06-22 04:53:35.98499+00
110	30	9	2025-06-22 04:53:35.98499+00
111	32	19	2025-06-22 04:53:35.984991+00
112	76	1	2025-06-22 04:53:35.984991+00
113	31	31	2025-06-22 04:53:35.984991+00
114	59	1	2025-06-22 04:53:35.984991+00
115	41	9	2025-06-22 04:53:35.984992+00
116	67	19	2025-06-22 04:53:35.984992+00
117	75	1	2025-06-22 04:53:35.984992+00
118	8	31	2025-06-22 04:53:35.984993+00
119	43	9	2025-06-22 04:53:35.984993+00
120	74	19	2025-06-22 04:53:35.984993+00
121	37	1	2025-06-22 04:53:35.984993+00
122	19	1	2025-06-22 04:53:35.984994+00
123	81	6	2025-06-22 04:53:35.984994+00
124	6	9	2025-06-22 04:53:35.984994+00
125	65	2	2025-06-22 04:53:35.984994+00
126	79	6	2025-06-22 04:53:35.984995+00
127	66	1	2025-06-22 04:53:35.984995+00
128	22	2	2025-06-22 04:53:35.984995+00
129	63	1	2025-06-22 04:53:35.984995+00
130	1	18	2025-06-22 22:19:01.187396+00
131	69	7	2025-06-22 22:19:01.225497+00
132	83	9	2025-06-22 22:19:01.226901+00
133	3	7	2025-06-22 22:19:01.228201+00
134	60	9	2025-06-22 22:19:01.229461+00
135	84	9	2025-06-22 22:19:01.231702+00
136	12	9	2025-06-22 22:19:01.236093+00
137	14	9	2025-06-22 22:19:01.239918+00
138	18	9	2025-06-22 22:19:01.241314+00
139	4	9	2025-06-22 22:19:01.242378+00
140	23	9	2025-06-22 22:19:01.243461+00
141	27	9	2025-06-22 22:19:01.244992+00
142	28	9	2025-06-22 22:19:01.246633+00
143	29	9	2025-06-22 22:19:01.247824+00
144	33	9	2025-06-22 22:19:01.248689+00
145	36	9	2025-06-22 22:19:01.249585+00
\.


--
-- Data for Name: episodes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.episodes (id, series_id, season_number, episode_number, title, description, content_url, thumbnail_url, runtime, air_date, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: favorites; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.favorites (id, user_id, content_id, created_at) FROM stdin;
1	1	1	2025-06-22 05:34:02.913835+00
\.


--
-- Data for Name: genres; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.genres (id, name, description, created_at, updated_at) FROM stdin;
1	Action		2025-06-22 01:03:17.022079+00	2025-06-22 22:05:48.449729+00
2	Adventure		2025-06-22 01:03:17.022079+00	2025-06-22 22:05:48.449729+00
3	Animals		2025-06-22 01:03:17.022079+00	2025-06-22 22:05:48.449729+00
4	Anime		2025-06-22 01:03:17.022079+00	2025-06-22 22:05:48.449729+00
5	Children		2025-06-22 01:03:17.022079+00	2025-06-22 22:05:48.449729+00
6	Comedy		2025-06-22 01:03:17.022079+00	2025-06-22 22:05:48.449729+00
7	Crime		2025-06-22 01:03:17.022079+00	2025-06-22 22:05:48.449729+00
8	Documentary		2025-06-22 01:03:17.022079+00	2025-06-22 22:05:48.449729+00
9	Drama		2025-06-22 01:03:17.022079+00	2025-06-22 22:05:48.449729+00
10	Educational		2025-06-22 01:03:17.022079+00	2025-06-22 22:05:48.449729+00
11	Faith		2025-06-22 01:03:17.022079+00	2025-06-22 22:05:48.449729+00
12	Fantasy		2025-06-22 01:03:17.022079+00	2025-06-22 22:05:48.449729+00
13	Fashion		2025-06-22 01:03:17.022079+00	2025-06-22 22:05:48.449729+00
14	Food		2025-06-22 01:03:17.022079+00	2025-06-22 22:05:48.449729+00
15	Gaming		2025-06-22 01:03:17.022079+00	2025-06-22 22:05:48.449729+00
16	Health		2025-06-22 01:03:17.022079+00	2025-06-22 22:05:48.449729+00
17	History		2025-06-22 01:03:17.022079+00	2025-06-22 22:05:48.449729+00
18	Horror		2025-06-22 01:03:17.022079+00	2025-06-22 22:05:48.449729+00
19	Martial Arts		2025-06-22 01:03:17.022079+00	2025-06-22 22:05:48.449729+00
20	Mystery		2025-06-22 01:03:17.022079+00	2025-06-22 22:05:48.449729+00
21	Nature		2025-06-22 01:03:17.022079+00	2025-06-22 22:05:48.449729+00
22	News		2025-06-22 01:03:17.022079+00	2025-06-22 22:05:48.449729+00
23	Reality		2025-06-22 01:03:17.022079+00	2025-06-22 22:05:48.449729+00
24	Romance		2025-06-22 01:03:17.022079+00	2025-06-22 22:05:48.449729+00
25	Science		2025-06-22 01:03:17.022079+00	2025-06-22 22:05:48.449729+00
26	Science Fiction		2025-06-22 01:03:17.022079+00	2025-06-22 22:05:48.449729+00
27	Sitcom		2025-06-22 01:03:17.022079+00	2025-06-22 22:05:48.449729+00
28	Special		2025-06-22 01:03:17.022079+00	2025-06-22 22:05:48.449729+00
29	Sports		2025-06-22 01:03:17.022079+00	2025-06-22 22:05:48.449729+00
30	Technology		2025-06-22 01:03:17.022079+00	2025-06-22 22:05:48.449729+00
31	Thriller		2025-06-22 01:03:17.022079+00	2025-06-22 22:05:48.449729+00
32	Western		2025-06-22 01:03:17.022079+00	2025-06-22 22:05:48.449729+00
\.


--
-- Data for Name: ratings; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.ratings (id, code, description, min_age, created_at, updated_at) FROM stdin;
1	TVY		\N	2025-06-22 01:03:17.026924+00	2025-06-22 22:05:48.475458+00
2	TVY7		\N	2025-06-22 01:03:17.026924+00	2025-06-22 22:05:48.475458+00
3	TVG		\N	2025-06-22 01:03:17.026924+00	2025-06-22 22:05:48.475458+00
4	TVPG		\N	2025-06-22 01:03:17.026924+00	2025-06-22 22:05:48.475458+00
5	TV14		\N	2025-06-22 01:03:17.026924+00	2025-06-22 22:05:48.475458+00
6	TVMA		\N	2025-06-22 01:03:17.026924+00	2025-06-22 22:05:48.475458+00
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, email, first_name, last_name, password_hash, created_at, updated_at) FROM stdin;
2	newuser@example.com	New	User	ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f	2025-06-22 20:52:37.602553+00	2025-06-22 20:52:37.602566+00
1	test@example.com	Test	User	5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8	2025-06-22 01:03:21.426712+00	2025-06-22 20:59:51.687867+00
\.


--
-- Name: content_genres_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.content_genres_id_seq', 145, true);


--
-- Name: content_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.content_id_seq', 430, true);


--
-- Name: episodes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.episodes_id_seq', 1, false);


--
-- Name: favorites_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.favorites_id_seq', 1, true);


--
-- Name: genres_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.genres_id_seq', 256, true);


--
-- Name: ratings_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.ratings_id_seq', 48, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 2, true);


--
-- Name: content_genres content_genres_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.content_genres
    ADD CONSTRAINT content_genres_pkey PRIMARY KEY (id);


--
-- Name: content content_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.content
    ADD CONSTRAINT content_pkey PRIMARY KEY (id);


--
-- Name: content content_title_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.content
    ADD CONSTRAINT content_title_key UNIQUE (title);


--
-- Name: episodes episodes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.episodes
    ADD CONSTRAINT episodes_pkey PRIMARY KEY (id);


--
-- Name: episodes episodes_series_id_season_number_episode_number_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.episodes
    ADD CONSTRAINT episodes_series_id_season_number_episode_number_key UNIQUE (series_id, season_number, episode_number);


--
-- Name: favorites favorites_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.favorites
    ADD CONSTRAINT favorites_pkey PRIMARY KEY (id);


--
-- Name: favorites favorites_user_id_content_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.favorites
    ADD CONSTRAINT favorites_user_id_content_id_key UNIQUE (user_id, content_id);


--
-- Name: genres genres_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.genres
    ADD CONSTRAINT genres_name_key UNIQUE (name);


--
-- Name: genres genres_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.genres
    ADD CONSTRAINT genres_pkey PRIMARY KEY (id);


--
-- Name: ratings ratings_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ratings
    ADD CONSTRAINT ratings_code_key UNIQUE (code);


--
-- Name: ratings ratings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ratings
    ADD CONSTRAINT ratings_pkey PRIMARY KEY (id);


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
-- Name: idx_content_genre; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_content_genre ON public.content USING btree (genre_id);


--
-- Name: idx_content_genres_content; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_content_genres_content ON public.content_genres USING btree (content_id);


--
-- Name: idx_content_genres_genre; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_content_genres_genre ON public.content_genres USING btree (genre_id);


--
-- Name: idx_content_rating; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_content_rating ON public.content USING btree (rating_id);


--
-- Name: idx_content_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_content_type ON public.content USING btree (type);


--
-- Name: idx_episodes_series; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_episodes_series ON public.episodes USING btree (series_id);


--
-- Name: idx_episodes_series_season; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_episodes_series_season ON public.episodes USING btree (series_id, season_number);


--
-- Name: idx_favorites_content; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_favorites_content ON public.favorites USING btree (content_id);


--
-- Name: idx_favorites_user; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_favorites_user ON public.favorites USING btree (user_id);


--
-- Name: idx_users_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_users_email ON public.users USING btree (email);


--
-- Name: content update_content_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_content_updated_at BEFORE UPDATE ON public.content FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: episodes update_episodes_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_episodes_updated_at BEFORE UPDATE ON public.episodes FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: genres update_genres_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_genres_updated_at BEFORE UPDATE ON public.genres FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: ratings update_ratings_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_ratings_updated_at BEFORE UPDATE ON public.ratings FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: users update_users_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON public.users FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: content content_genre_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.content
    ADD CONSTRAINT content_genre_id_fkey FOREIGN KEY (genre_id) REFERENCES public.genres(id);


--
-- Name: content_genres content_genres_content_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.content_genres
    ADD CONSTRAINT content_genres_content_id_fkey FOREIGN KEY (content_id) REFERENCES public.content(id) ON DELETE CASCADE;


--
-- Name: content_genres content_genres_genre_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.content_genres
    ADD CONSTRAINT content_genres_genre_id_fkey FOREIGN KEY (genre_id) REFERENCES public.genres(id) ON DELETE CASCADE;


--
-- Name: content content_rating_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.content
    ADD CONSTRAINT content_rating_id_fkey FOREIGN KEY (rating_id) REFERENCES public.ratings(id);


--
-- Name: episodes episodes_series_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.episodes
    ADD CONSTRAINT episodes_series_id_fkey FOREIGN KEY (series_id) REFERENCES public.content(id) ON DELETE CASCADE;


--
-- Name: favorites favorites_content_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.favorites
    ADD CONSTRAINT favorites_content_id_fkey FOREIGN KEY (content_id) REFERENCES public.content(id) ON DELETE CASCADE;


--
-- Name: favorites favorites_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.favorites
    ADD CONSTRAINT favorites_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

