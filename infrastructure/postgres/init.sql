CREATE TABLE IF NOT EXISTS "user" (
    id SERIAL PRIMARY KEY,
    created_on DATE,
    first_name VARCHAR,
    last_name VARCHAR,
    birth_date DATE,
    personal_code VARCHAR
);

CREATE TABLE IF NOT EXISTS loan (
    id SERIAL PRIMARY KEY,
    client_id INTEGER,
    amount DOUBLE PRECISION,
    created_on DATE,
    duration BIGINT,
    matured_on DATE,
    status VARCHAR,
    updated_on DATE
);

CREATE TABLE IF NOT EXISTS payment (
    id SERIAL PRIMARY KEY,
    loan_id BIGINT,
    amount DOUBLE PRECISION,
    principle DOUBLE PRECISION,
    interest DOUBLE PRECISION,
    status VARCHAR,
    created_on DATE
);
