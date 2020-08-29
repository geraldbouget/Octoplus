-- PROCEDURE STOCKEE POUR VERIFIER NBRE INFRACTION EN FONCTION INDEX DEP ET SERVICE ET INSTIUTION --
--(sert aussi de verif d'int"grité des données)--

DELIMITER |
CREATE PROCEDURE `information_generale`(p_annee YEAR(4), p_nomAdm VARCHAR(30),
p_codeIndex SMALLINT(5), p_numDep VARCHAR(3), p_nomService VARCHAR(100))
BEGIN
SELECT p.annee, nomAdm, p.codeIndex, libelle, numDep, nomService, sum(nbreInfractions)
FROM pointage as p
JOIN service AS s ON s.idService=p.idService
JOIN administration as ad ON s.idAdm=ad.idAdm
JOIN infraction as i ON i.codeIndex=p.codeIndex
GROUP BY annee,nomAdm, p.codeIndex, libelle, s.numDep, nomService
HAVING p.annee=p_annee
AND nomAdm=p_nomAdm
AND p.codeIndex=p_codeIndex
AND numDep=p_numDep
AND nomService=p_nomService;
END |


-- PROCEDURE STOCKEE POUR VERIFIER NBRE INFRACTION PAR DEP ET PAR ANNEE
DELIMITER |
CREATE PROCEDURE `nombre_infraction_index`(
  p_annee YEAR(4),
  p_codeIndex SMALLINT(5),
  p_numDep VARCHAR(3))
BEGIN
SELECT p.annee, p.codeIndex, libelle, s.numDep, sum(nbreInfractions) as NombreInfractions
FROM pointage as p
JOIN service AS s ON s.idService=p.idService
JOIN infraction as i ON i.codeIndex=p.codeIndex
GROUP BY annee,p.codeIndex, s.numDep, libelle
HAVING p.annee=p_annee
AND numDep=p_numDep
AND p.codeIndex=p_codeIndex; END |

-- vue matérialisée pour query à partir de dash
CREATE TABLE query_dash_main
ENGINE = InnoDB
SELECT dp.numDep, dp.nomDep,ic.nomIndicLight, i.libelle, annee, sum(p.nbreInfractions) AS cumulInfraction,
d.nbrePopulation,d.densite, SUM((nbreInfractions/nbrePopulation)*1000) AS InfPour1000
FROM pointage AS p
JOIN service AS s ON p.idService=s.idService
JOIN infraction as i ON i.codeIndex=p.codeIndex
JOIN indicateur as ic ON ic.idIndic=i.idIndic
JOIN departement AS dp ON s.numDep=dp.numDep
JOIN demographie AS d ON dp.numDep=d.numDep
GROUP BY dp.numDep, dp.nomDep, ic.nomIndicLight, i.libelle, annee, d.nbrePopulation, d.densite;

-- maj query_dash_main à lancer à partir script autmatisation --
DELIMITER |
CREATE PROCEDURE maj_query_dash_main()
BEGIN
    TRUNCATE query_dash_main;

    INSERT INTO query_dash_main
    SELECT dp.numDep, dp.nomDep,ic.nomIndicLight, i.libelle, annee, sum(p.nbreInfractions) AS cumulInfraction,
	d.nbrePopulation,d.densite, SUM((nbreInfractions/nbrePopulation)*1000) AS InfPour1000
	FROM pointage AS p
	JOIN service AS s ON p.idService=s.idService
	JOIN infraction as i ON i.codeIndex=p.codeIndex
	JOIN indicateur as ic ON ic.idIndic=i.idIndic
	JOIN departement AS dp ON s.numDep=dp.numDep
	JOIN demographie AS d ON dp.numDep=d.numDep
	GROUP BY dp.numDep, dp.nomDep, ic.nomIndicLight, i.libelle, annee, d.nbrePopulation, d.densite;

END |
DELIMITER ;

-- vue matérialisée pour query à partir de dash sur infos demographique POUR
-- avoir nom dep en plus--
-- FIRST : récupérer noms de colonnes séparés par virgule pour PAS tout retaper--
SELECT group_concat(COLUMN_NAME)
FROM information_schema.columns WHERE TABLE_SCHEMA = 'octoplus' AND TABLE_NAME = 'demographie';

CREATE TABLE query_dash_demographie
ENGINE = InnoDB
SELECT  age_15,age_15_29,age_20,age_30_44,age_45_59,age_60_74,age_75,anneeRecensement,
densite,nbreCommunes,nbrePopulation,d.numDep,nomDep,partCom_10000_plus,partCom_200_9999,
partCom_moins_200,partPop_10000_plus,partPop_200_9999,partPop_moins_200
FROM demographie AS dem
JOIN departement AS d
ON d.numDep=dem.numDep;


--
CREATE TABLE query_dash_paris
ENGINE = InnoDB
SELECT dp.numDep, dir.nomDirection,s.nomService,dp.nomDep,ic.nomIndicLight, i.libelle, annee, sum(p.nbreInfractions) AS cumulInfraction,
d.nbrePopulation,d.densite, SUM((nbreInfractions/nbrePopulation)*1000) AS InfPour1000
FROM pointage AS p
JOIN service AS s ON p.idService=s.idService
JOIN direction as dir on dir.idDirection=s.idDirection
JOIN infraction as i ON i.codeIndex=p.codeIndex
JOIN indicateur as ic ON ic.idIndic=i.idIndic
JOIN departement AS dp ON s.numDep=dp.numDep
JOIN demographie AS d ON dp.numDep=d.numDep
where s.numDep='75' and s.idAdm=1
GROUP BY dp.numDep, dp.nomDep,dir.nomDirection, s.nomService,ic.nomIndicLight, i.libelle, annee, d.nbrePopulation, d.densite;

CREATE TABLE query_dash_main_dom
ENGINE = InnoDB
SELECT dp.idRegion, r.nomRegion, ic.nomIndicLight, i.libelle, annee, sum(p.nbreInfractions) AS cumulInfraction,
d.nbrePopulation,d.densite, SUM((nbreInfractions/nbrePopulation)*1000) AS InfPour1000
FROM pointage AS p
JOIN service AS s ON p.idService=s.idService
JOIN infraction as i ON i.codeIndex=p.codeIndex
JOIN indicateur as ic ON ic.idIndic=i.idIndic
JOIN departement AS dp ON s.numDep=dp.numDep
JOIN region as r ON r.idRegion=dp.idRegion
JOIN demographie AS d ON dp.numDep=d.numDep
where dp.numDep = '971' OR dp.numDep = '972' OR dp.numDep = '973' OR dp.numDep = '974'
GROUP BY dp.idRegion, r.nomRegion, ic.nomIndicLight, i.libelle, annee, d.nbrePopulation, d.densite;

CREATE TABLE query_dash_main_region
ENGINE = InnoDB
SELECT dp.idRegion, r.nomRegion, ic.nomIndicLight, i.libelle, annee, sum(p.nbreInfractions) AS cumulInfraction,
d.nbrePopulation,d.densite, SUM((nbreInfractions/nbrePopulation)*1000) AS InfPour1000
FROM pointage AS p
JOIN service AS s ON p.idService=s.idService
JOIN infraction as i ON i.codeIndex=p.codeIndex
JOIN indicateur as ic ON ic.idIndic=i.idIndic
JOIN departement AS dp ON s.numDep=dp.numDep
JOIN region as r ON r.idRegion=dp.idRegion
JOIN demographie AS d ON dp.numDep=d.numDep
GROUP BY dp.idRegion, r.nomRegion, ic.nomIndicLight, i.libelle, annee, d.nbrePopulation, d.densite;
