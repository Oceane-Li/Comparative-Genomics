-----------------------------------------------------------------------

Comment lancer l'application Pkdotapp ?

-----------------------------------------------------------------------

Pkdotapp est une application conçue pour générer des dotplots à partir 
de protéomes bactériens stockés dans une base de données PostgreSQL. 
Cette application présente une interface graphique développée avec 
Tkinter et implémentée en Python 3. Elle permet aux utilisateurs 
d'explorer la synténie entre les gènes homologues de différentes 
souches bactériennes.



-----------------------------------------------------------------------

I - Pré-requis

-----------------------------------------------------------------------

Vous aurez besoin de lancer des commandes PostgreSQL. Pour cela, vous devez
vous connecter au serveur obiwan de la façon suivante :

- Ouvrer votre terminal Linux.

- Taper la commande suivante : ssh -X prenom@134.157.183.99 (remplacer 'prenom'
  par votre propre prenom).
  Ne pas oublier le -X !

- S'il s'agit de votre première connexion à obiwan, vous devez définir un mot
  de passe.

- Une fois connecté à obiwan, vous pourrez lancer les commandes PSQL demandés.



Le serveur obiwan possède la fonction qui permet d'effectuer le blastp. Si jamais
vous travaillez sur ordinateur local, vous pouvez également faire le choix de 
télécharger la fonction blastp avec la commande suivante :

COMMANDE A TAPER DANS LINUX : sudo apt -get install blastp

(Il est vivement conseillé de lancer les scripts dans obiwan !)



Nous utiliserons plusieurs librairies de python 3 dans nos scripts. Si votre système
Linux vous indique qu'il manque des modules, vous pourrez les installer avec la commande
suivante :

COMMANDE A TAPER DANS LE TERMINAL : pip install nom_du_module



-----------------------------------------------------------------------

II - La base de données 'Projet748'

-----------------------------------------------------------------------

Importer tous les scripts et fichiers dans votre serveur obiwan, dans un même répertoire :
- Pkdotapp.py
- database.sql
- BDD.py
- prokaryotes_complete-genomes.csv 


Une fois que vous êtes connectés à obiwan, vous pouvez accéder à la base 
de données que j'ai pré-fait sur mon serveur obiwan (si vous avez les droits
d'accès). Dans le cas contraire, vous pouvez construire une nouvelle base
de données 'Projet748', en tapant la commande suivante dans le serveur obiwan :

COMMANDE : createdb Projet748
(cette commande va créer une database vide)

Ensuite, si vous avez choisi de créer vous-même la database, vous pourrez créer
les tables nécessaires dans la base de données, en lançant le fichier 'BDD.py'
(Veuillez assurez que les scripts BBD.py et database.sql soient au même endroit)
(/!\ Le script BDD.py est à lancer une seule fois !)

Après cette étape, 3 tables (fasta, blastp et cdsearch) seront construites dans
la base de données 'Projet748'. Vous pouvez vérifier cela en tapant les 3 commandes 
suivantes :

COMMANDE 1 : SELECT * FROM fasta;
COMMANDE 2 : SELECT * FROM blastp;
COMMANDE 3 : SELECT * FROM cdsearch;

Si jamais il y a un problème avec votre serveur ou avec le script et que vous
n'arrivez pas à créer correctement les tables, il vous reste toujours une dernière
option : ouvrez le script database.sql, et copier-coller l'un après l'autre les 
commandes psql dans le serveur obiwan pour créer la table correspondante.
Par exemple, si vous voulez créer la table 'fasta' manuellement, vous pouvez copier-
coller la commande suivante dans le terminal :

CREATE TABLE fasta(
    nom_fichier     TEXT PRIMARY KEY,
    nom_organisme   TEXT,
    abreviation     TEXT,
    ftplink         TEXT,
    repertoire      TEXT
);
(ne pas oublier le ';' !)



-----------------------------------------------------------------------

III - Répertoire et dossiers

-----------------------------------------------------------------------

Après avoir terminé avec la database, il faut maintenant définir les répertoires
où vous allez stocker vos fichiers fasta, blastp et cdsearch télchargés,
pour éviter des redondances de téléchargement qui sont très coûteuse en terme
de temps.


Créer un dossier 'PKDOT' avec la commande suivante à taper dans obiwan :

COMMANDE : mkdir PKDOT


Mettre tous les scripts et fichiers importés dans obiwan dans ce dossier
'PKDOT'.

Entrer dans le répertoire du dossier PKDOT :

COMMANDE : cd PKDOT

(si jamais un message d'erreur s'affiche, il se peut que le dossier PKDOT ne
s'est pas créer correctement. Pour vérifier cela, vous pouvez taper la commande 'ls'
pour checker si 'PKDOT' apparaît dans les affichages. S'il n'y est pas, cela 
signifie que le dossier PKDOT n'a pas été créé).


Une fois dans le dossier PKDOT, créer 3 dossiers supplémentaires :

COMMANDE : mkdir FASTAFILE
COMMANDE : mkdir BLASTPFILE
COMMANDE : mkdir CDSFILE

Ces 3 dossiers seront utiles et nécessaire au bon fonctionnement de notre interface.

Une fois que les 3 dossiers seront créés, vous pourrez importer les fichiers fasta, blastp et cd search
que j'ai déjà réalisé avec mon application pour pouvoir faire un test rapide par la suite.
(voir le fichier PROTEOMES.txt)



Voici la structure des dossiers:

-----PKDOT
        |
        Pkdotapp.py
        |
        database.sql
        |
        BDD.py
        |
        -----FASTAFILE (ex de fichier fasta)
                  |
                  GCA_000005845.2_ASM584v2_translated_cds.faa 
                  |
                  GCA_000008685.2_ASM868v2_translated_cds.faa
                  |
                  ...
        |
        -----BLASTPFILE (ex de fichier blastp)
                  |
                  blastp_BorreHLJ01_Borrei_B31.out 
                  |
                  blastp_BorreHLJ01_Borrei_B31.out
                  |
                  ...
        |
        -----CDSFILE (ex de fichier cdsearch)
                  |
                  CDS_Esche_IAI1.out
                  |
                  CDS_EscheG1655.out
                  |
                  ...

VEUILLEZ NE PAS MODIFIER CETTE STRUCTURE DE DOSSIER (sinon, faudrait que vous modifiez les chemins
de redirection des fichiers dans le script Pkdotapp.py selon votre path).


Maintenant que vous avez la base de données, les tables requises, et les dossiers pour
stocker les fichiers,  on peut passer au script Pkdotapp.py 



-----------------------------------------------------------------------

IV - L'interface graphique Pkdotapp

-----------------------------------------------------------------------

Lancer le script python Pkdotapp.py dans le serveur obiwan :

COMMANDE : python3 Pkdotapp.py 

Quelques secondes après, une fenetre d'interface apparaît, avec :

- à gauche, le panel de commande où vous pourrez manipuler selon vos besoins.

- à droite, un graphe vide pour l'instant qui sera le lieu d'affichage du dotplot
  plus tard si vous lancer un blastp ou un cdsearch.

- en haut à gauche, vous avez un petit onglet 'Menu' où vous pouvez choisir
d'enregistrer les dotplots ou de quitter l'application.



Voyons le panel de commande (à gauche, sur fond bleu clair) plus en détail :

- Que ce soit pour faire un blastp ou un cdsearch, vous devez commencer par 
  sélectionner les organismes procaryotes dont vous voulez comparer les protéomes.

- 2 exemples de procakyotes sont mis par défaut à l'ouverture de l'interface,
  mais vous pouvez bien sûr les modifier selon vos besoins. Pour cela, effacer
  d'abord ce qu'il y a dans ces barres de recherche (un simple sélect all + 
  la touche de suppression suffit). Après, vous pouvez taper le nom de l'organisme
  qui vous intéresse, et des propositions vous seront faites par autocomplétion 
  selon le texte que vous aurez tapé. Si vous ne savez pas quel organisme choisir,
  vous pouvez également appuyer sur la petite flèche à droite de la barre pour voir
  le menu déroulant des organismes procaryotes disponibles, qui sont rangés dans 
  l'ordre alphabétique.

- le premier organisme sélectionné servira de query dans le blastp, et le 2nd organisme
  servira de subject. 
  
- Avant de cliquer sur 'Lancer BLASTP', vous avez une barre d'entrée un peu plus bas 
  qui correspond à la e-value de sélection dans le fichier blastp pour ploter le dotplot.
  La e-value est initialisée à 1e-6 par défaut, mais vous pouvez l'augmenter ou la
  diminuer selon vos besoins. Attention à bien remplir la bonne case de e-value pour le blastp
  (car il y en a une aussi mais pour le cdsearch).
  
- Une fois que vous aurez sélectionné les 2 procaryotes, ainsi que le seuil de e-value
  souhaité, vous pouvez appuyer sur la touche Lancer BLASTP qui est juste en dessous 
  des 2 barres de recherche.

- le temps de lancement du BLASTP dépendra de la taille des fichiers fasta des 2 organismes
  sélectionnés, cela prend en moyenne 2min à 2min 30. Si le blastp entre ces 2 organismes a 
  déjà été fait, la procédure sera assez rapide.

- Vous avez le choix de 'filtrer le dotplot' ou pas : si cette case à droite du blastp
  est cochée, alors le dotplot du blastp n'affichera que les points qui sont au moins 
  sur une diagonale de 3 (en d'autres termes, le filtrage permet d'éliminer le bruit et 
  les points trop dispersés, pour avoir un résultat plus pertinent).
  Le filtrage du dotplot prend une trentaine de seconde à s'exécuter en moyenne (mais 
  ce temps peut s'allonger si les protéomes sont très grands).
  Vous pouvez bien sûr comparer l'effet d'avant et après le filtrage pour garder le dotplot
  qui vous plaît le plus (si vous préférez le dotplot avant le filtrage, décocher la case et 
  re-cliquer sur 'Lancer BLASTP').

- Une fois le blastp terminé, le dotplot correspondant s'affiche à droite dans le canevas.

- Si vous voulez enregistrer le dotplot, vous pouvez soit cliquer sur le bouton 'Enregistrer'
  en gras en bas des e-value, soit sur l'onglet 'Menu' qui contient cette fonctionnalité aussi.
  Une petite fenetre apparaîtra alors, et vous pourrez choisir dans quel répertoire vous voulez
  l'enregistrer, et sous quel format : 3 formats sont disponibles (pdf, png et jpg).


- La procédure est identique pour le cdsearch, mais faut appuyer sur 'Lancer CDSearch'.
  Vous être bien évidemment libre de déterminer le seuil de e-value souhaité pour cette 
  analyse, faites simplement attention à la remplir dans la bonne case.
  Le CDSearch prend beaucoup de temps à se lancer s'il n'a pas été déjà fait.
  Il est normal d'attendre 5 à 10 min PAR ORGANISME, selon la longueur de leur génome
  (mais une fois que le CDS est fait, le dotplot s'affiche très rapidement).

- La case pour filtrer le dotplot du cdsearch est situé à droite du bouton 'Lancer CDSearch',
  et elle fonctionne de la même façon que pour le blastp, cela permet d'éliminer pas mal de bruit.

- Sur le dotplot du CD Search, les points ne sont pas tous de même couleurs.
  En effet, les points du cdsearch sont plottés en fonction du % de similarité fonctionnelle
  qu'il y a entre les couples de gènes des 2 organismes : plus le point est rouge, plus le couple
  de gènes aura de CDD en commun.

- L'enregistrement des dotplot de cdsearch se passe de la même façon que pour le blastp.


Si jamais vous trouvez que les points du dotplot sont trop petits à voir, vous pouvez zoomer
sur le dotplot :

- cliquer d'abord avec la souris sur la zone dont vous souhaiter zoomer dessus.
- ensuite, cliquer sur zoom pour agrandir là où votre souris a cliqué.
- si vous voulez revenir un pas en arrière, cliquer sur 'Dézoomer'.
- si vous voulez revenir au dotplot initial, cliquer sur 'Dézoome total'.


Lorsque vous souhaitez quitter l'application, vous pouvez :
- soit cliquer sur le bouton 'Quitter' du panel de commande.
- soit cliquer sur la croix de la fenetre en haut à droite.
- soit passer par l'onglet Menu -> Quitter.

Dans les 3 cas, une fenetre de confirmation apparaîtra, et si vous voulez réellement fermer
l'application, cliquer sur 'Oui'. Si vous cliquez sur 'Non', vous reviendrez sur la fenetre de
l'application.



-----------------------------------------------------------------------

Fin

-----------------------------------------------------------------------

Application crée par Océane Li.
