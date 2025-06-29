
  
  -- util une fois le docker compose estlancer on lance ce script pour créer les tables bdd
-- Fichier: sql/init.sql

-- Création de la table pour les films
CREATE TABLE movies (
    movieId INT NOT NULL,
    title VARCHAR(255),
    genres VARCHAR(255),
    PRIMARY KEY (movieId)
);

-- Création de la table pour les notes
CREATE TABLE ratings (
    id INT AUTO_INCREMENT,
    userId INT,
    movieId INT,
    rating FLOAT,
    timestamp VARCHAR(30),
    PRIMARY KEY (id),
    -- Créer des index améliore considérablement la vitesse des recherches sur ces colonnes
    INDEX (userId), 
    INDEX (movieId)
);
