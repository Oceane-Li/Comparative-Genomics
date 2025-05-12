# Gestion de la base de données 'Projet748'
import os
import psycopg2 as pg


# os.system('createdb Projet748')


# On se connecte à notre BdD Projet748
conn = pg.connect("dbname=Projet748")
cur = conn.cursor()

# Chemin vers votre fichier SQL contenant les instructions de création de tables
sql_file_path = "database.sql"

# Lecture du contenu du fichier SQL
with open(sql_file_path, "r") as sql_file:
    sql_script = sql_file.read()

# Exécution du script SQL
cur.execute(sql_script)
