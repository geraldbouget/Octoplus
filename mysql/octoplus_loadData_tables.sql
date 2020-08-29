-- INSERTION DONNEES --

LOAD DATA INFILE '/Users/geraldbouget/dumps/export_regions.csv'
INTO TABLE Region
FIELDS TERMINATED BY ","
ENCLOSED BY '"'
LINES TERMINATED BY "\n"
IGNORE 1 LINES;

LOAD DATA INFILE '/Users/geraldbouget/dumps/export_departements.csv'
INTO TABLE Departement
FIELDS TERMINATED BY ","
ENCLOSED BY '"'
LINES TERMINATED BY "\n"
IGNORE 1 LINES
(idRegion,numDep, nomDep);

--1ere version demographie
-- LOAD DATA INFILE '/Users/geraldbouget/dumps/export_demographie.csv'
-- INTO TABLE Demographie
-- FIELDS TERMINATED BY ","
-- ENCLOSED BY '"'
-- LINES TERMINATED BY "\n"
-- IGNORE 1 LINES
-- (numDep, @nbrePopulation, @densite, anneeRecensement)
-- SET
-- nbrePopulation = if(@nbrePopulation=0, NULL, @nbrePopulation),
-- densite = if(@densite=0, NULL, @densite);

--verion 2 update1
LOAD DATA INFILE '/Users/geraldbouget/dumps/export_demographieUpdate1.csv'
INTO TABLE Demographie
FIELDS TERMINATED BY ","
ENCLOSED BY '"'
LINES TERMINATED BY "\n"
IGNORE 1 LINES
(numDep, @nbrePopulation, @densite, anneeRecensement,
@age_15, @age_15_29, @age_30_44, @age_45_59, @age_60_74, @age_75,
@age_20, @nbreCommunes, @partCom_moins_200, @partPop_moins_200, @partCom_200_9999, @partPop_200_9999,
@partCom_10000_plus, @partPop_10000_plus)
SET
nbrePopulation = if(@nbrePopulation=0, NULL, @nbrePopulation),
densite = if(@densite=0, NULL, @densite),
nbreCommunes = if(@nbreCommunes=0, NULL, @nbreCommunes),
age_15 = if(@age_15=0, NULL, @age_15),
age_15_29 = if(@age_15_29=0, NULL, @age_15_29),
age_30_44 = if(@age_30_44=0, NULL, @age_30_44),
age_45_59 = if(@age_45_59=0, NULL, @age_45_59),
age_45_59 = if(@age_45_59=0, NULL, @age_45_59),
age_60_74 = if(@age_60_74=0, NULL, @age_60_74),
age_75 = if(@age_75=0, NULL, @age_75),
age_20 = if(@age_20=0, NULL, @age_20),
partCom_moins_200 = if(@partCom_moins_200=0, NULL, @partCom_moins_200),
partPop_moins_200 = if(@partPop_moins_200=0, NULL, @partPop_moins_200),
partCom_200_9999 = if(@partCom_200_9999=0, NULL, @partCom_200_9999),
partPop_200_9999 = if(@partPop_200_9999=0, NULL, @partPop_200_9999),
partCom_10000_plus = if(@partCom_10000_plus=0, NULL, @partCom_10000_plus),
partPop_10000_plus = if(@partPop_10000_plus=0, NULL, @partPop_10000_plus);


LOAD DATA INFILE '/Users/geraldbouget/dumps/export_directions.csv'
INTO TABLE Direction
FIELDS TERMINATED BY ","
ENCLOSED BY '"'
LINES TERMINATED BY "\n"
IGNORE 1 LINES
(nomDirection, nomComplet, idAdm);

LOAD DATA INFILE '/Users/geraldbouget/dumps/export_administration.csv'
INTO TABLE Administration
FIELDS TERMINATED BY ","
ENCLOSED BY '"'
LINES TERMINATED BY "\n"
IGNORE 1 LINES
(nomAdm);

LOAD DATA INFILE '/Users/geraldbouget/dumps/export_services_PG.csv'
INTO TABLE Service
FIELDS TERMINATED BY ","
ENCLOSED BY '"'
LINES TERMINATED BY "\n"
IGNORE 1 LINES
(numDep, nomService, @value, idAdm)
SET
idDirection = if(@value=0, NULL, @value);

LOAD DATA INFILE '/Users/geraldbouget/dumps/export_pointage_PG.csv'
INTO TABLE Pointage
FIELDS TERMINATED BY ","
ENCLOSED BY '"'
LINES TERMINATED BY "\n"
IGNORE 1 LINES
(annee, nbreInfractions, idService, codeIndex);

LOAD DATA INFILE '/Users/geraldbouget/dumps/export_indicateurs.csv'
INTO TABLE Indicateur
FIELDS TERMINATED BY ","
ENCLOSED BY '"'
LINES TERMINATED BY "\n"
IGNORE 1 LINES
(nomIndic, nomIndicLight);

LOAD DATA INFILE '/Users/geraldbouget/dumps/export_UniteCompte.csv'
INTO TABLE uniteCompte
FIELDS TERMINATED BY ","
ENCLOSED BY '"'
LINES TERMINATED BY "\n"
IGNORE 1 LINES
(nomUc);

LOAD DATA INFILE '/Users/geraldbouget/dumps/export_infractions.csv'
INTO TABLE infraction
FIELDS TERMINATED BY ","
ENCLOSED BY '"'
LINES TERMINATED BY "\n"
IGNORE 1 LINES
(codeIndex, libelle, @idIndic, @idUc)
SET
idIndic = if(@idIndic='', NULL, @idIndic),
idUc=if(@idUc='', NULL, @idUc)
;
