DROP TABLE IF EXISTS urls CASCADE;
CREATE TABLE urls (
    id serial PRIMARY KEY,
    name varchar(255) UNIQUE NOT NULL,
    created_at DATE DEFAULT NOW() NOT NULL
);
