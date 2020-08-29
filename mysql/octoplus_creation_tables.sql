CREATE DATABASE IF NOT EXISTS octoplus DEFAULT CHARACTER SET utf8mb4 ;

USE octoplus

-- CREATION TABLES --

CREATE TABLE region(
  idRegion VARCHAR(3) NOT NULL,
  NomRegion VARCHAR(100) NULL,
  PRIMARY KEY(idRegion)
)
ENGINE = InnoDB;

CREATE TABLE departement(
  numDep VARCHAR(3) NOT NULL,
  nomDep VARCHAR(50) NULL,
  idRegion VARCHAR(3) NOT NULL,
  PRIMARY KEY(numDep)
)
ENGINE = InnoDB;

-- 1ere version table demographie
-- CREATE TABLE Demographie(
--   idDemo SMALLINT(3) NOT NULL AUTO_INCREMENT,
--   numDep VARCHAR(3) NOT NULL,
--   nbrePopulation INT NULL,
--   densite FLOAT NULL,
--   anneeRecensement YEAR NOT NULL,
--   PRIMARY KEY(idDemo)
-- )
-- ENGINE = InnoDB;

CREATE TABLE demographie(
  numDep VARCHAR(3) NOT NULL,
  anneeRecensement YEAR NOT NULL,
  nbrePopulation INT NULL,
  densite FLOAT NULL,
  nbreCommunes INT NULL,
  age_15 FLOAT NULL,
  age_15_29 FLOAT NULL,
  age_30_44 FLOAT NULL,
  age_45_59 FLOAT NULL,
  age_60_74 FLOAT NULL,
  age_75 FLOAT NULL,
  age_20 FLOAT NULL,
  partCom_moins_200 FLOAT NULL,
  partPop_moins_200 FLOAT NULL,
  partCom_200_9999 FLOAT NULL,
  partPop_200_9999 FLOAT NULL,
  partCom_10000_plus FLOAT NULL,
  partPop_10000_plus FLOAT NULL,
  PRIMARY KEY(numDep, anneeRecensement)
)
ENGINE = InnoDB;


CREATE TABLE administration(
  idAdm SMALLINT(3) NOT NULL AUTO_INCREMENT,
  nomAdm VARCHAR(30) NULL,
  PRIMARY KEY(idAdm)
)
ENGINE = InnoDB;

CREATE TABLE direction(
  idDirection SMALLINT(3) NOT NULL AUTO_INCREMENT,
  nomDirection VARCHAR(100) NULL,
  idAdm SMALLINT(3) NULL,
  nomComplet VARCHAR(150) NULL,
  PRIMARY KEY(idDirection)
)
ENGINE = InnoDB;


CREATE TABLE service(
  idService SMALLINT(4) NOT NULL AUTO_INCREMENT,
  nomService VARCHAR(100) NOT NULL,
  numDep VARCHAR(3) NOT NULL,
  idDirection SMALLINT(3) NULL,
  idAdm SMALLINT(3) NULL,
  PRIMARY KEY(idService)
)
ENGINE = InnoDB;

CREATE TABLE pointage(
  annee YEAR NOT NULL,
  nbreInfractions INT NULL,
  idService SMALLINT(4) NOT NULL,
  codeIndex SMALLINT(5) NOT NULL

)
ENGINE = InnoDB;

CREATE TABLE indicateur(
  idIndic SMALLINT(3) NOT NULL AUTO_INCREMENT,
  nomIndic VARCHAR(150) NULL,
  nomIndicLight VARCHAR(100) NULL,
  PRIMARY KEY(idIndic)
)
ENGINE = InnoDB;

CREATE TABLE infraction(
  codeIndex SMALLINT(5) NOT NULL,
  libelle VARCHAR(200) NULL,
  idIndic SMALLINT(3)  NULL,
  idUc SMALLINT(3) NULL,
  PRIMARY KEY(codeIndex)
)
ENGINE = InnoDB;


CREATE TABLE uniteCompte(
  idUc SMALLINT(3) NOT NULL AUTO_INCREMENT,
  nomUc VARCHAR(45) NULL,
  PRIMARY KEY(idUc)
)
ENGINE = InnoDB;
