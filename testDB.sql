-- TESTS PARA LA BASE DE DATOS DE GESTIÓN DE PORTAFOLIOS

-- 1. Insertar datos de prueba en USER
INSERT INTO USER (ObjectID, ID, password, name, riskProfile, createdAt)
VALUES 
('user1', 'usuario1@email.com', 'pass123', 'Juan Pérez', 'moderado', date('now')),
('user2', 'usuario2@email.com', 'pass456', 'Ana García', 'agresivo', date('now')),
('user3', 'usuario3@email.com', 'pass789', 'Carlos López', 'conservador', date('now'));

-- 2. Insertar datos de prueba en ETFs
INSERT INTO ETFs (ObjectID, ID, name, description, category, assets, lastUpdate)
VALUES 
('etf1', 'VTI', 'Vanguard Total Stock Market ETF', 'ETF que sigue el mercado total de EE.UU.', 'Renta Variable', 1250.75, date('now')),
('etf2', 'AGG', 'iShares Core U.S. Aggregate Bond ETF', 'ETF de bonos de EE.UU.', 'Renta Fija', 895.32, date('now')),
('etf3', 'VGT', 'Vanguard Information Technology ETF', 'ETF del sector tecnológico', 'Tecnología', 2100.45, date('now')),
('etf4', 'VWO', 'Vanguard FTSE Emerging Markets ETF', 'ETF de mercados emergentes', 'Internacional', 980.20, date('now'));

-- 3. Insertar datos de prueba en PORTFOLIOS
INSERT INTO PORTFOLIOS (ObjectID, ID, userUK, name, valor, createdAt, lastUpdate)
VALUES 
('port1', 'portfolio1', 'usuario1@email.com', 'Mi portafolio principal', 10000.00, date('now'), date('now')),
('port2', 'portfolio2', 'usuario1@email.com', 'Portafolio alto riesgo', 5000.00, date('now'), date('now')),
('port3', 'portfolio3', 'usuario2@email.com', 'Inversión a largo plazo', 15000.00, date('now'), date('now'));

-- 4. Insertar datos de prueba en PORTFOLIO_ITEMS
INSERT INTO PORTFOLIO_ITEMS (ObjectID, ID, portfolioID, etfID, allocation)
VALUES 
('item1', 'item1', 'portfolio1', 'VTI', 60.0),
('item2', 'item2', 'portfolio1', 'AGG', 40.0),
('item3', 'item3', 'portfolio2', 'VGT', 70.0),
('item4', 'item4', 'portfolio2', 'VWO', 30.0),
('item5', 'item5', 'portfolio3', 'VTI', 50.0),
('item6', 'item6', 'portfolio3', 'AGG', 30.0),
('item7', 'item7', 'portfolio3', 'VWO', 20.0);

-- 5. TEST: Verificar que hay datos en todas las tablas
SELECT 'Usuarios: ' || COUNT(*) FROM USER;
SELECT 'ETFs: ' || COUNT(*) FROM ETFs;
SELECT 'Portafolios: ' || COUNT(*) FROM PORTFOLIOS;
SELECT 'Items de portafolio: ' || COUNT(*) FROM PORTFOLIO_ITEMS;

-- 6. TEST: Verificar las relaciones entre tablas
-- Portafolios por usuario
SELECT u.name AS usuario, COUNT(p.ObjectID) AS num_portafolios
FROM USER u
LEFT JOIN PORTFOLIOS p ON u.ID = p.userUK
GROUP BY u.ID;

-- 7. TEST: Mostrar composición de un portafolio específico
SELECT 
    p.name AS portafolio,
    e.ID AS simbolo_etf,
    e.name AS nombre_etf,
    pi.allocation AS porcentaje_asignacion
FROM PORTFOLIOS p
JOIN PORTFOLIO_ITEMS pi ON p.ID = pi.portfolioID
JOIN ETFs e ON pi.etfID = e.ID
WHERE p.ID = 'portfolio1';

-- 8. TEST: Verificar que la suma de asignaciones sea 100% en cada portafolio
SELECT 
    p.ID AS portafolio_id,
    p.name AS portafolio_nombre,
    SUM(pi.allocation) AS suma_asignaciones
FROM PORTFOLIOS p
JOIN PORTFOLIO_ITEMS pi ON p.ID = pi.portfolioID
GROUP BY p.ID
HAVING SUM(pi.allocation) <> 100.0;

-- 9. TEST: Verificar integridad referencial (debería dar 0 resultados)
SELECT COUNT(*) AS relaciones_huerfanas
FROM PORTFOLIO_ITEMS pi
WHERE NOT EXISTS (SELECT 1 FROM PORTFOLIOS p WHERE p.ID = pi.portfolioID)
   OR NOT EXISTS (SELECT 1 FROM ETFs e WHERE e.ID = pi.etfID);

-- 10. TEST: Buscar ETFs no utilizados en ningún portafolio
SELECT e.ID, e.name
FROM ETFs e
LEFT JOIN PORTFOLIO_ITEMS pi ON e.ID = pi.etfID
WHERE pi.ObjectID IS NULL;
