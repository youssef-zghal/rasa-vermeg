import pyodbc

import warnings

def main():

    def se_connecter_a_ssms1():
        try:
            # Remplacez les valeurs ci-dessous par vos propres informations de connexion
            server = 'DESKTOP-8MJF8PH\MSSQLSERVER1'
            database = 'STAGE_VERMEG'
            # Vous n'avez pas besoin de fournir un nom d'utilisateur et un mot de passe pour l'authentification Windows

            # Créer une chaîne de connexion
            connection_string = f'DRIVER=ODBC Driver 17 for SQL Server;SERVER={server};DATABASE={database};Trusted_Connection=yes;'

            # Se connecter à la base de données
            conn = pyodbc.connect(connection_string)

            # Retourner la connexion
            return conn

        except Exception as e:
            print(f"Erreur lors de la connexion à la base de données : {str(e)}")
            return None

    def executer_requete(conn, sql_query):
        try:
            # Créer un curseur pour exécuter la requête
            cursor = conn.cursor()

            # Exécuter la requête SQL
            cursor.execute(sql_query)

            # Récupérer les résultats de la requête
            results = cursor.fetchall()

            # Fermer le curseur
            cursor.close()

            # Retourner les résultats
            return results

        except Exception as e:
            print(f"Erreur lors de l'exécution de la requête : {str(e)}")
            return None

    def obtenir_types(conn):
        types = []
        sql_query = "SELECT DISTINCT Type FROM dbo.[Dimension Fournisseur]"
        results = executer_requete(conn, sql_query)
        if results:
            for row in results:
                types.append(row.Type)
        return types

    def obtenir_etats(conn):
        etats = []
        sql_query = "SELECT DISTINCT Etat FROM dbo.[Dimensions Facture]"
        results = executer_requete(conn, sql_query)
        if results:
            for row in results:
                etats.append(row.Etat)
        return etats
    
    def obtenir_Fournisseur(conn):
        Fournisseur = []
        sql_query = "SELECT DISTINCT Fournisseur FROM dbo.[Dimension Fournisseur]"
        results = executer_requete(conn, sql_query)
        if results:
            for row in results:
                Fournisseur.append(row.Fournisseur)
        return Fournisseur

    def obtenir_Facture(conn):
        Facture = []
        sql_query = "SELECT DISTINCT Facture FROM dbo.[Dimensions Facture]"
        results = executer_requete(conn, sql_query)
        if results:
            for row in results:
                Facture.append(row.Facture)
        return Facture
    
    def inserer_dans_dictionnaire(file_name, data):
        with open(file_name, "w", encoding="utf-8") as file:
            file.write("# Nouveaux éléments\n")
            file.write("data = [\n")
            for item in data:
                item = item.strip()  # Enlever les espaces à la fin
                escaped_item = item.replace("'", "\\'")  # Échapper les apostrophes
                file.write(f"    '{escaped_item}',\n")
            file.write("]\n")

    import re

    # Fonction pour extraire les éléments de la liste data du fichier dictionnaire_Etats.py
    def extract_elements(file_path):
        elements = []
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                for line in lines:
                    match = re.match(r"\s*'([^']+)',", line)
                    if match:
                        elements.append(match.group(1))
        except FileNotFoundError:
            print(f"Fichier non trouvé : {file_path}")
        return elements

    # Fonction pour générer le contenu du fichier nlu.yml
    import random

    def generate_nlu_contentType(elements):
        formulations = [
            "montant pour le type [{element}](type) ?",
            "depenses pour le type [{element}](type) ?",
            "montants pour le type [{element}](type) ?",
            "type [{element}](type) ?",
            "[{element}](type)",
            "details sur [{element}](type)",
        ]
    
        
        content = "- intent: demande_montant_type \n  examples: |\n"
        for element in elements:
            formulation = random.choice(formulations)
            content += f"    - {formulation}\n".format(element=element)
        return content

    def generate_nlu_contentFournisseur(elements):
        formulations = [
            "montant pour le fournisseur [{element}](Fournisseur) ?",
            "montant pour [{element}](Fournisseur) ?",
            "Combien [{element}](Fournisseur)",
            "[{element}](Fournisseur)",
            "facture pour le fournisseur [{element}](Fournisseur)",
        ]
        formulations2=[
            "total [{element}](Fournisseur) en [Mars](month) [2022](Annee) ?"   ,
            "Combien on a avec [{element}](Fournisseur) en [Fevrier](month)?",
            "montants pour le fournisseur [{element}](Fournisseur) pour mois [aout](month) [2022](Annee)",
        ]
        
        content = "- intent: demande_montant_fournisseur \n  examples: |\n"
        for element in elements:
            formulation = random.choice(formulations)
            content += f"    - {formulation}\n".format(element=element)
        
    
        content2 = "- intent: demander_montant_total_fournisseur_mois_annee \n  examples: |\n"
        for element2 in elements:
            formulation2 = random.choice(formulations2)
            content2 += f"    - {formulation2}\n".format(element=element2)
        return content,content2



    def generate_nlu_contentFacture(elements):
        formulations = [
            "fournisseur cette facture [{element}](Facture) ?",
            "facture [{element}](Facture) ?",
            "cette facture [{element}](Facture)",
            "[{element}](Facture)",
            "fournisseur pour cette facture [{element}](Facture) ",
            "facture [{element}](Facture)",

        ]
        
        content = "- intent: demande_Facture \n  examples: |\n"
        for element in elements:
            formulation = random.choice(formulations)
            content += f"    - {formulation}\n".format(element=element)
        return content


    # --

    def effacerType():
        # Lecture du contenu du fichier nlu.yml
        with open('data/nlu.yml', 'r') as file:
            lines = file.readlines()

        # Ouverture du fichier en mode écriture pour y écrire les lignes filtrées
        with open('data/nlu.yml', 'w') as file:
            # Variable pour suivre si nous sommes à l'intérieur du bloc à supprimer
            inside_block = False
            for line in lines:
                # Si nous sommes à l'intérieur du bloc et que nous trouvons une ligne vide, le bloc est terminé
                if inside_block and line.strip() == "":
                    inside_block = False
                    continue

                # Si nous ne sommes pas dans le bloc, écrivons la ligne
                if not inside_block:
                    # Vérifions si la ligne correspond au début du bloc à supprimer
                    if line.strip().startswith('- intent: demande_montant_type'):
                        inside_block = True
                    else:
                        file.write(line)
                # Si nous sommes à l'intérieur du bloc, passons à la ligne suivante sans écrire
                else:
                    continue

        # print("Le code a été détecté et effacé avec succès.")
                
    def effacerFournisseur():
        # Lecture du contenu du fichier nlu.yml
        with open('data/nlu.yml', 'r') as file:
            lines = file.readlines()

        # Ouverture du fichier en mode écriture pour y écrire les lignes filtrées
        with open('data/nlu.yml', 'w') as file:
            # Variable pour suivre si nous sommes à l'intérieur du bloc à supprimer
            inside_block = False
            for line in lines:
                # Si nous sommes à l'intérieur du bloc et que nous trouvons une ligne vide, le bloc est terminé
                if inside_block and line.strip() == "":
                    inside_block = False
                    continue

                # Si nous ne sommes pas dans le bloc, écrivons la ligne
                if not inside_block:
                    # Vérifions si la ligne correspond au début du bloc à supprimer
                    if line.strip().startswith('- intent: demande_montant_fournisseur'):
                        inside_block = True
                    else:
                        file.write(line)
                # Si nous sommes à l'intérieur du bloc, passons à la ligne suivante sans écrire
                else:
                    continue

    def effacerFacture():
        # Lecture du contenu du fichier nlu.yml
        with open('data/nlu.yml', 'r') as file:
            lines = file.readlines()

        # Ouverture du fichier en mode écriture pour y écrire les lignes filtrées
        with open('data/nlu.yml', 'w') as file:
            # Variable pour suivre si nous sommes à l'intérieur du bloc à supprimer
            inside_block = False
            for line in lines:
                # Si nous sommes à l'intérieur du bloc et que nous trouvons une ligne vide, le bloc est terminé
                if inside_block and line.strip() == "":
                    inside_block = False
                    continue

                # Si nous ne sommes pas dans le bloc, écrivons la ligne
                if not inside_block:
                    # Vérifions si la ligne correspond au début du bloc à supprimer
                    if line.strip().startswith('- intent: demande_Facture'):
                        inside_block = True
                    else:
                        file.write(line)
                # Si nous sommes à l'intérieur du bloc, passons à la ligne suivante sans écrire
                else:
                    continue

    conn = se_connecter_a_ssms1()
    if conn:
        types = obtenir_types(conn)
        etats = obtenir_etats(conn)
        Facture = obtenir_Facture(conn)
        Fournisseur = obtenir_Fournisseur(conn)
        inserer_dans_dictionnaire("dictionnaire_Types.py", types)
        inserer_dans_dictionnaire("dictionnaire_Etats.py", etats)
        inserer_dans_dictionnaire("dictionnaire_Fournisseur.py", Fournisseur)
        inserer_dans_dictionnaire("dictionnaire_Facture.py", Facture)
        # print("Types et états insérés avec succès dans les fichiers.")
        effacerType()
        effacerFournisseur()
        effacerFacture()

# Chemin vers le fichier dictionnaire_Etats.py
        file_path = "dictionnaire_Types.py"
# Extraction des éléments
        elements = extract_elements(file_path)
# Génération du contenu du fichier nlu.yml
        nlu_content = generate_nlu_contentType(elements)
# Écriture du contenu dans le fichier nlu.yml
        with open("data/nlu.yml", "a", encoding="utf-8") as nlu_file:
            nlu_file.write(nlu_content)
# print("Le fichier nlu.yml a été généré avec succès.")
            
# Chemin vers le fichier dictionnaire_Fournisseur.py
        file_path2 = "dictionnaire_Fournisseur.py"
# Extraction des éléments
        elements2 = extract_elements(file_path2)
# Génération du contenu du fichier nlu.yml
        nlu_content2,nlu_content4 = generate_nlu_contentFournisseur(elements2)
# Écriture du contenu dans le fichier nlu.yml
        with open("data/nlu.yml", "a", encoding="utf-8") as nlu_file2:
            nlu_file2.write(nlu_content2)
            nlu_file2.write(nlu_content4)

# Chemin vers le fichier dictionnaire_Facture.py
        file_path3 = "dictionnaire_Facture.py"
# Extraction des éléments
        elements3 = extract_elements(file_path3)
# Génération du contenu du fichier nlu.yml
        nlu_content3 = generate_nlu_contentFacture(elements3)
# Écriture du contenu dans le fichier nlu.yml
        with open("data/nlu.yml", "a", encoding="utf-8") as nlu_file3:
            nlu_file3.write(nlu_content3)
# print("Le fichier nlu.yml a été généré avec succès.")
        conn.close()

if __name__ == "__main__":
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning)
        main()
