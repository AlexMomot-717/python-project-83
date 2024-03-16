CREATE TABLE urls (
    id serial PRIMARY KEY,
    name varchar(255) UNIQUE NOT NULL,
    created_at DATE DEFAULT NOW() NOT NULL
);

CREATE TABLE checks (
    id serial PRIMARY KEY,
    url_id bigint REFERENCES urls (id),
    status_code integer,
    h1 text,
    title text,
    description text,
    created_at DATE DEFAULT NOW() NOT NULL
);
