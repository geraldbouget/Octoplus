
-- creation table erreur gestion de certaines
-- erreur d'insertion et d'update
CREATE TABLE erreur (
id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
defErreur VARCHAR(255) UNIQUE
);
-- insert valeur d'erreur à faire apparaitre quand l'insertion
-- ou update pose problème
INSERT INTO erreur(defErreur)
VALUES
('Ce numéro de département n\'existe pas dans la table "departement"'),
('Le numéro d\'index ne peut pas être supérieur à 107'),
('la ligne libelle "index non utilisé" ne peut contenir des valeurs > 0 ');

-- trigger pour cas ou insertion new dep pas dans la table dep
DELIMITER |
CREATE TRIGGER before_insert_numDepService BEFORE INSERT
ON service FOR EACH ROW
BEGIN
IF NEW.numDep NOT IN (SELECT DISTINCT numDep FROM departement)
THEN INSERT INTO erreur(defErreur)
VALUES ('Ce numéro de département n\'existe pas dans la table "departement"');
END IF;
END |
DELIMITER ;

-- trigger pour cas ou insertion new dep pas dans la table dep
DELIMITER |
CREATE TRIGGER before_update_numDepService BEFORE UPDATE
ON service FOR EACH ROW
BEGIN
IF NEW.numDep NOT IN (SELECT DISTINCT numDep FROM departement)
THEN INSERT INTO erreur(defErreur)
VALUES ('Ce numéro de département n\'existe pas dans la table "departement"');
END IF;
END |
DELIMITER ;


-- trigger pour éviter insertion d'un codeindex > à 107 - INSERT
DELIMITER |
CREATE TRIGGER before_insert_codeIndexPointage BEFORE INSERT
ON pointage FOR EACH ROW
BEGIN
IF NEW.codeIndex > 107
THEN INSERT INTO erreur(defErreur)
VALUES ('Le numéro d\'index ne peut pas être supérieur à 107');
END IF;
END |
DELIMITER ;

-- trigger pour éviter insertion d'un codeindex > à 107 UPDATE
DELIMITER |
CREATE TRIGGER before_update_codeIndexPointage BEFORE UPDATE
ON pointage FOR EACH ROW
BEGIN
IF NEW.codeIndex > 107
THEN INSERT INTO erreur(defErreur)
VALUES ('Le numéro d\'index ne peut pas être supérieur à 107');
END IF;
END |
DELIMITER ;

-- trigger pour éviter que dans ligne 'index non utilisé' soit
-- insérée valeurs différents de 0 ou null - INSERT
DELIMITER |
CREATE TRIGGER before_insert_nbreInfractions BEFORE INSERT
ON pointage FOR EACH ROW
BEGIN
IF NEW.codeIndex IN (SELECT codeIndex FROM infraction
WHERE libelle = 'Index non utilisé') AND NEW.NbreInfractions > 0
THEN INSERT INTO erreur(defErreur)
VALUES ('la ligne libelle "index non utilisé" ne peut contenir des valeurs > 0 ');
END IF;
END |
DELIMITER ;


-- trigger pour éviter que dans ligne 'index non utilisé' soit
-- insérée valeurs différents de 0 ou null - UPDATE
DELIMITER |
CREATE TRIGGER before_update_nbreInfractions BEFORE UPDATE
ON pointage FOR EACH ROW
BEGIN
IF NEW.codeIndex IN (SELECT codeIndex FROM infraction
WHERE libelle = 'Index non utilisé') AND NEW.NbreInfractions > 0
THEN INSERT INTO erreur(defErreur)
VALUES ('la ligne libelle "index non utilisé" ne peut contenir des valeurs > 0 ');
END IF;
END |
DELIMITER ;

-- ESSAIS TRIGGERS A FAIRE SUR DB FICITF !!!--
--INSERT INTO service(nomService, numDep, idDirection, idAdm)
--VALUES ('ServiceFicitf', '456', 2, 1);
