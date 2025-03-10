-- Asegurarse de que las claves foráneas están activadas
PRAGMA foreign_keys = ON;

-- Recrear las tablas relevantes con relaciones claras
DROP TABLE IF EXISTS PORTFOLIO_ITEMS;
DROP TABLE IF EXISTS PORTFOLIOS;
DROP TABLE IF EXISTS USER;
DROP TABLE IF EXISTS ETFs;

-- Crear la tabla USER
CREATE TABLE USER (
    ObjectID TEXT PRIMARY KEY,
    ID TEXT UNIQUE,  -- email
    password TEXT,
    name TEXT,
    riskProfile TEXT,
    createdAt DATE
);

-- Crear la tabla ETFs
CREATE TABLE ETFs (
    ObjectID TEXT PRIMARY KEY,
    ID TEXT UNIQUE,  -- symbol
    name TEXT,
    description TEXT,
    category TEXT,
    assets REAL,
    lastUpdate DATE
);

-- Crear la tabla PORTFOLIOS
CREATE TABLE PORTFOLIOS (
    ObjectID TEXT PRIMARY KEY,
    ID TEXT UNIQUE,  -- Asegurando que ID sea UNIQUE para referencia
    userUK TEXT,
    name TEXT,
    valor REAL,
    createdAt DATE,
    lastUpdate DATE,
    FOREIGN KEY (userUK) REFERENCES USER(ID)
);

-- Crear la tabla PORTFOLIO_ITEMS
CREATE TABLE PORTFOLIO_ITEMS (
    ObjectID TEXT PRIMARY KEY,
    ID TEXT,
    portfolioID TEXT,
    etfID TEXT,
    allocation REAL,
    FOREIGN KEY (portfolioID) REFERENCES PORTFOLIOS(ID),
    FOREIGN KEY (etfID) REFERENCES ETFs(ID)
);
