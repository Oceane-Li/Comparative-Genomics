--Code psql pour créer les tables dans la base de données Projet748


-- Table des fichiers fasta (ncbi)
CREATE TABLE fasta(
    nom_fichier     TEXT PRIMARY KEY,
    nom_organisme   TEXT,
    abreviation     TEXT,
    ftplink         TEXT,
    repertoire      TEXT
);


-- Table des fichiers BLASTP.out
CREATE TABLE blastp(
    nom_fichier     TEXT PRIMARY KEY,
    repertoire      TEXT
);


-- Table des fichiers CDSearch.out
CREATE TABLE cdsearch(
    nom_fichier     TEXT PRIMARY KEY,
    repertoire      TEXT
);