
# Script Python de scraping du site https://books.toscrape.com/

## Description du projet

Il s'agit du premier projet réalisé dans le cadre de ma formation OpenClassrooms.
Il s'agit d'un script très basique. Le but du projet était de me remettre le pied à l'étrier en termes de Python, utilisation des environnements virtuels, ...
Avec le recul, assez intéressant de voir la manière dont j'avais développé ce projet à l'époque : sans POO, avec une fonction monolythique de 80 lignes.
M'a tout de même permis de découvrir le principe du scraping.


## Mise en place et exécution du script

1. Téléchargez le projet depuis Github
Pour cloner le projet en local sur votre machine, copiez l'URL de ce repo et lancez la commande suivante dans git bash :  
```
git clone <URL du repo>
```
2. Créez un environnement virtuel Python en exécutant la commande suivantes dans le Terminal de votre choix :
```
python -m venv <environment name>
```
Puis, toujours dans le terminal, activez votre environnement avec la commande suivante si vous êtes sous Linux :
```
source env/bin/activate
```
Ou bien celle-ci si vous êtes sous Windows
```
env/Scripts/activate.bat
```
3. Téléchargez les packages Python nécessaires à la bonne exécution du script à l'aide de la commande suivante :
```
pip install -r requirements.txt
```
4. Vous pouvez maintenant exécuter le script, soit à l'aide de l'IDE de votre choix, soit directement depuis le Terminal, à l'aide de la commande suivante :
```		
python script.py
```
NB : Les fichiers seront générés dans un dossier results/ date du jour / au sein dossier dans lequel le script est exécuté.


