# Octoplus Project

These are the main scripts I wrote for my studies final project at Simplon's School.  
They are based on the following dataset:  
https://www.data.gouv.fr/fr/datasets/crimes-et-delits-enregistres-par-les-services-de-gendarmerie-et-de-police-depuis-2012/

This dataset shows all the crimes and misdemeanours recorded by the french security services ('police' and 'gendarmerie') in France since 2012.  
There is one multi-indexed Excel sheet for each year and for each kind of security service. The table sructure is both multi-indexed at the index and variable levels and the police table structure is different from gendramerie's one.

Each folder contains scripts for one specific part of the project:
- **ProjectPresentation** : long and short version of the project presentation (in french) 
- **mysql** : shows the database model and the main scripts to create tables, constraints, loading data and optimize the database.    
- **data_processing** : shows the python scripts on jupyter notebooks used to check integrity of the datas, clean the datas, prepare tables  in CSV for the database.   
- **database_update_automating** : python application which autmates the process of checking for dataset updates, of processing data and updateing the database
- **dashboard_Dash** : dash/python application to visualize data analysis from the database. The database was deployed on AWS/Redis and the Dash application deployed on
Heroku.


The purpose of publishing these scripts is to show examples of the skills acquired during my training.

The online version of the dashboard : http://octoplus-dash.herokuapp.com/ 
