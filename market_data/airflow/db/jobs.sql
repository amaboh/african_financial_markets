 -- Create indices table
CREATE SCHEMA IF NOT EXISTS market_data;

CREATE TABLE IF NOT EXISTS indices (
    id SERIAL PRIMARY KEY,
    current_date TEXT,
    index_abbreviation TEXT,
    index_change NUMERIC,
    index_percentage_change NUMERIC,
    index_value NUMERIC,
    indice_name VARCHAR(255),
    market_summary JSONB,
    time_periods JSONB
);


-- Create companies table
CREATE TABLE IF NOT EXISTS companies (
    id SERIAL PRIMARY KEY,
    company_name VARCHAR(255),
    sector VARCHAR(255),
    price NUMERIC,
    one_day NUMERIC,
    ytd NUMERIC,
    market_cap NUMERIC,
    date TEXT,
    market_name VARCHAR(255)
);

