
from tkinter import EventType
import pyodbc

def executer_autre_fichier():
    try:
        # Chemin vers le fichier Python à exécuter
        chemin_fichier = '/data/Retrieval.py'

        # Exécute le fichier Python
        with open(chemin_fichier, 'r') as fichier:
            code = fichier.read()
            exec(code)

    except FileNotFoundError:
        print("Le fichier spécifié est introuvable.")
executer_autre_fichier()

def se_connecter_a_ssms():
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

# Exemple d'utilisation
conn = se_connecter_a_ssms()
# if conn:
#     print("Connexion réussie à la base de données.")
#     # Exemple de requête SELECT
#     query = "SELECT * FROM dbo.Source"
#     results = executer_requete(conn, query)
#     if results:
#         print("Résultats de la requête :")
#         for row in results:
#             print(row)
#     else:
#         print("Aucun résultat retourné.")

#     # Vous pouvez exécuter d'autres requêtes ici
# else:
#     print("Échec de la connexion à la base de données.")



from typing import Type, Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import pyodbc

class ActionObtenirFournisseurMontant(Action):
    def name(self) -> Text:
        return "action_obtenir_Fournisseur_montant"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        
        # Récupérer l'entité montant du tracker
        ref_entity = tracker.get_slot("Montant")
        if ref_entity:
            ref = int(ref_entity)
            # Se connecter à la base de données
            conn = se_connecter_a_ssms()  # Vous devez implémenter ces fonctions

            if conn:
                # Exécuter la requête SQL pour obtenir le montant de la facture
                query = f"""
                    SELECT f.montant 
                    FROM dbo.fait f
                    JOIN dbo.[Dimension fournisseur] fournisseur ON f.FK_Fournisseur = Pk_fournisseur
                    JOIN dbo.[Dimensions facture] facture ON f.FK_facture = PK_facture
                    WHERE facture.Référence = '{ref}'
                """
                results = executer_requete(conn, query)  # Vous devez implémenter cette fonction

                if results:
                    montant = results[0][0]
                    dispatcher.utter_message(template="utter_montant", montant=montant, Référence=ref)  # Assurez-vous que la valeur du slot montant est fournie
                else:
                    dispatcher.utter_message(text="Désolé, je n'ai pas pu trouver le montant pour cette Reference.")
            else:
                dispatcher.utter_message(text="Désolé, je n'ai pas pu me connecter à la base de données.")
        else:
            dispatcher.utter_message(text="Désolé, je n'ai pas pu extraire le numéro de Reference.")
        
        return []

# -----------------------------------------------------------------------------------------------------------------   
    
from datetime import datetime

class ActionObtenirMontantInf(Action):
    def name(self) -> Text:
        return "action_obtenir_montant_inf"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        
        # Récupérer l'entité montant du tracker
        ref_entity = tracker.get_slot("Montant")
        if ref_entity:
            montant = int(ref_entity)
            # Se connecter à la base de données
            conn = se_connecter_a_ssms()  # Vous devez implémenter ces fonctions

            if conn:
                # Exécuter la requête SQL pour obtenir les détails des factures avec un montant supérieur
                query = f"""
                    SELECT Fournisseur.Fournisseur , Facture.Référence , Facture.Facture , Date.Date , f.Montant , Facture.Etat , Fournisseur.type
                    FROM dbo.fait f 
                    JOIN dbo.[Dimension fournisseur] fournisseur ON f.FK_Fournisseur = fournisseur.Pk_fournisseur
                    JOIN dbo.[Dimensions facture] facture ON f.FK_facture = facture.PK_facture
                    JOIN dbo.[Dimension_dates] date ON f.FK_Date = Date.DateKey
                    WHERE f.Montant < {montant}
                """
                results = executer_requete(conn, query)  # Vous devez implémenter cette fonction

                if results:
                    for result in results:
                        # Récupérer les détails de chaque facture
                        reference, fournisseur, facture, date, montant, etat, type_facture = result
                        date_str = date.strftime("%Y-%m-%d")
                        dispatcher.utter_message(template="utter_inf", 
                                                 reference=reference, 
                                                 fournisseur=fournisseur, 
                                                 facture=facture, 
                                                 date=date_str, 
                                                 montant=montant, 
                                                 etat=etat, 
                                                 type_facture=type_facture)
                else:
                    dispatcher.utter_message(
                        text="Désolé, je n'ai pas pu trouver de factures avec un montant inférieur à celui spécifié."
                    )
            else:
                dispatcher.utter_message(
                    text="Désolé, je n'ai pas pu me connecter à la base de données."
                )
        else:
            dispatcher.utter_message(
                text="Désolé, je n'ai pas pu extraire le montant spécifié."
            )

        return []

 
# ------------------------------------------------------------------------------------------------------------------
from datetime import datetime

class ActionObtenirMontantSup(Action):
    def name(self) -> Text:
        return "action_obtenir_montant_sup"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        
        # Récupérer l'entité montant du tracker
        ref_entity = tracker.get_slot("Montant")
        if ref_entity:
            montant = int(ref_entity)
            # Se connecter à la base de données
            conn = se_connecter_a_ssms()  # Vous devez implémenter ces fonctions

            if conn:
                # Exécuter la requête SQL pour obtenir les détails des factures avec un montant supérieur
                query = f"""
                    SELECT Fournisseur.Fournisseur , Facture.Référence , Facture.Facture , Date.Date , f.Montant , Facture.Etat , Fournisseur.type
                    FROM dbo.fait f 
                    JOIN dbo.[Dimension fournisseur] fournisseur ON f.FK_Fournisseur = fournisseur.Pk_fournisseur
                    JOIN dbo.[Dimensions facture] facture ON f.FK_facture = facture.PK_facture
                    JOIN dbo.[Dimension_dates] date ON f.FK_Date = Date.DateKey
                    WHERE f.Montant > {montant}
                """
                results = executer_requete(conn, query)  # Vous devez implémenter cette fonction

                if results:
                    for result in results:
                        # Récupérer les détails de chaque facture
                        reference, fournisseur, facture, date, montant, etat, type_facture = result
                        date_str = date.strftime("%Y-%m-%d")
                        dispatcher.utter_message(template="utter_sup", 
                                                 reference=reference, 
                                                 fournisseur=fournisseur, 
                                                 facture=facture, 
                                                 date=date_str, 
                                                 montant=montant, 
                                                 etat=etat, 
                                                 type_facture=type_facture)
                else:
                    dispatcher.utter_message(text="Aucune facture trouvée avec un montant supérieur à celui spécifié.")
            else:
                dispatcher.utter_message(text="Désolé, je n'ai pas pu me connecter à la base de données.")
        else:
            dispatcher.utter_message(text="Désolé, je n'ai pas pu extraire le montant spécifié.")
        
        return []

# ------------------------------------------------------------------------------------------------------------------
from datetime import datetime

class ActionObtenirMontantegal(Action):
    def name(self) -> Text:
        return "action_obtenir_montant_egal"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        
        # Récupérer l'entité montant du tracker
        ref_entity = tracker.get_slot("Montant")
        if ref_entity:
            montant = int(ref_entity)
            # Se connecter à la base de données
            conn = se_connecter_a_ssms()  # Vous devez implémenter ces fonctions

            if conn:
                # Exécuter la requête SQL pour obtenir les détails des factures avec un montant supérieur
                query = f"""
                    SELECT Fournisseur.Fournisseur , Facture.Référence , Facture.Facture , Date.Date , f.Montant , Facture.Etat , Fournisseur.type
                    FROM dbo.fait f 
                    JOIN dbo.[Dimension fournisseur] fournisseur ON f.FK_Fournisseur = fournisseur.Pk_fournisseur
                    JOIN dbo.[Dimensions facture] facture ON f.FK_facture = facture.PK_facture
                    JOIN dbo.[Dimension_dates] date ON f.FK_Date = Date.DateKey
                    WHERE f.Montant = {montant}
                """
                results = executer_requete(conn, query)  # Vous devez implémenter cette fonction

                if results:
                    for result in results:
                        # Récupérer les détails de chaque facture
                        reference, fournisseur, facture, date, montant, etat, type_facture = result
                        date_str = date.strftime("%Y-%m-%d")
                        dispatcher.utter_message(template="utter_egal", 
                                                 reference=reference, 
                                                 fournisseur=fournisseur, 
                                                 facture=facture, 
                                                 date=date_str, 
                                                 montant=montant, 
                                                 etat=etat, 
                                                 type_facture=type_facture)
                else:
                    dispatcher.utter_message(text="Aucune facture trouvée avec un montant égal à celui spécifié.")
            else:
                dispatcher.utter_message(text="Désolé, je n'ai pas pu me connecter à la base de données.")
        else:
            dispatcher.utter_message(text="Désolé, je n'ai pas pu extraire le montant spécifié.")
        
        return []
    
# -----------------------------------------------------------------------------------------------------------------

class ActionMontantTotalFournisseurs(Action):
    def name(self) -> Text:
        return "action_montant_total_fournisseurs"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        # Se connecter à la base de données
        conn = se_connecter_a_ssms()  # Assurez-vous d'avoir cette fonction implémentée

        if conn:
            # Exécuter la requête SQL pour obtenir les montants dus par fournisseur
            query = f"""
            SELECT Fournisseur.Fournisseur , SUM(f.Montant) AS MontantTotal 
            FROM dbo.fait f 
            JOIN dbo.[Dimension fournisseur] fournisseur ON f.FK_Fournisseur = fournisseur.Pk_fournisseur
            GROUP BY Fournisseur
            """  
            results = executer_requete(conn, query)  # Assurez-vous d'avoir cette fonction implémentée

            if results:
                for row in results:
                    Fournisseur = row[0]
                    montant_total = row[1]
                    dispatcher.utter_message(
                        text=f"Le fournisseur {Fournisseur} doit un montant total de {montant_total}."
                    )
            else:
                dispatcher.utter_message(text="Désolé, je n'ai pas pu trouver les informations sur les montants dus par fournisseur.")
        else:
            dispatcher.utter_message(text="Désolé, je n'ai pas pu me connecter à la base de données.")

        return []

# -----------------------------------------------------------------------------------------------------------------

class ActionObtenirMontantDate(Action):
    def name(self) -> Text:
        return "action_obtenir_montant_Date"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Obtenir la date de la requête de l'utilisateur
        date = tracker.get_slot('Date')
        
        # Requête SQL pour obtenir tous les montants correspondant à la date
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT f.montant FROM dbo.fait f JOIN dbo.[Dimension_dates] date ON f.FK_Date = Date.DateKey  WHERE date.date = ?", (date,))
        rows = cursor.fetchall()
        
        if rows:
            amounts = [row[0] for row in rows]
            amount_str = ", ".join(str(amount) for amount in amounts)
            dispatcher.utter_message(text=f"Les montants pour la date {date} sont : {amount_str} TND.")
        else:
            dispatcher.utter_message(text=f"Aucun montant trouvé pour la date {date}.")
        
        return []

# -----------------------------------------------------------------------------------------------------------------

import re

class MontantTotalParEtat(Action):
    def name(self) -> Text:
        return "Montant_Total_Par_Etat"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        # Se connecter à la base de données
        conn = se_connecter_a_ssms()  # Assurez-vous d'avoir cette fonction implémentée

        if conn:
            # Exécuter la requête SQL pour obtenir les montants dus par fournisseur
            query = """SELECT facture.Etat, SUM(f.Montant) AS MontantTotal 
            FROM dbo.fait f 
            JOIN dbo.[Dimensions facture] facture ON f.FK_facture = facture.PK_facture
            GROUP BY facture.Etat
            """
            results = executer_requete(conn, query)  # Assurez-vous d'avoir cette fonction implémentée

            if results:
                for row in results:
                    Etat = row[0]
                    montant_total = row[1]
                    dispatcher.utter_message(
                        text=f"L'Etat' {Etat} -> {montant_total}."
                    )
            else:
                dispatcher.utter_message(text="Désolé, je n'ai pas pu trouver les informations sur les montants dus par etat.")
        else:
            dispatcher.utter_message(text="Désolé, je n'ai pas pu me connecter à la base de données.")

        return []


# -----------------------------------------------------------------------------------------------------------------
     
class ActionAfficherMontantsEtatValidees(Action):
    def name(self) -> Text:
        return "action_afficher_montants_etat_validees"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Connexion à la base de données (assurez-vous que "conn" est correctement défini)
        cursor = conn.cursor()
        # Requête SQL pour obtenir tous les montants correspondant à l'état Validé
        query = """SELECT Fournisseur.Fournisseur , Facture.Référence , Facture.Facture , Date.Date , f.Montant , Facture.Etat , Fournisseur.type
                    FROM dbo.fait f 
                    JOIN dbo.[Dimension fournisseur] fournisseur ON f.FK_Fournisseur = fournisseur.Pk_fournisseur
                    JOIN dbo.[Dimensions facture] facture ON f.FK_facture = facture.PK_facture
                    JOIN dbo.[Dimension_dates] date ON f.FK_Date = Date.DateKey WHERE facture.etat = 'Validé'"""
        
        results = executer_requete(conn, query)  # Vous devez implémenter cette fonction

        if results:
            for result in results:
                # Récupérer les détails de chaque facture
                fournisseur,reference, facture, date, montant, etat,type = result
                date_str = date.strftime("%Y-%m-%d")
                dispatcher.utter_message(
                        text=f"le fournisseur {fournisseur} doit un montant total de {montant} avec un état {etat}."
                    )
        else:
            # Aucun montant trouvé pour l'état Validé
            dispatcher.utter_message(text=f"Aucun montant trouvé pour l'état 'Validé'.")

        return []

# -----------------------------------------------------------------------------------------------------------------
         
class ActionAfficherMontantsEtatCree(Action):
    def name(self) -> Text:
        return "action_afficher_montants_etat_crees"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Connexion à la base de données (assurez-vous que "conn" est correctement défini)
        cursor = conn.cursor()
        # Requête SQL pour obtenir tous les montants correspondant à l'état Cree
        query = """SELECT Fournisseur.Fournisseur , Facture.Référence , Facture.Facture , Date.Date , f.Montant , Facture.Etat , Fournisseur.type
                    FROM dbo.fait f 
                    JOIN dbo.[Dimension fournisseur] fournisseur ON f.FK_Fournisseur = fournisseur.Pk_fournisseur
                    JOIN dbo.[Dimensions facture] facture ON f.FK_facture = facture.PK_facture
                    JOIN dbo.[Dimension_dates] date ON f.FK_Date = Date.DateKey WHERE facture.etat = 'Créé'"""
        results = executer_requete(conn, query)  # Vous devez implémenter cette fonction

        if results:
            for result in results:
                # Récupérer les détails de chaque facture
                fournisseur,reference, facture, date, montant, etat,type = result
                date_str = date.strftime("%Y-%m-%d")
                dispatcher.utter_message(
                        text=f"Le fournisseur {fournisseur} doit un montant total de {montant} avec un état {etat}."
                    )
        else:
            # Aucun montant trouvé pour l'état Cree
            dispatcher.utter_message(text=f"Aucun montant trouvé pour l'état 'Créé'.")

        return []
# -----------------------------------------------------------------------------------------------------------------
         
class ActionAfficherMontantsEtatCree(Action):
    def name(self) -> Text:
        return "action_afficher_montants_etat_prets"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Connexion à la base de données (assurez-vous que "conn" est correctement défini)
        cursor = conn.cursor()
        # Requête SQL pour obtenir tous les montants correspondant à l'état Pret
        query = """SELECT Fournisseur.Fournisseur , Facture.Référence , Facture.Facture , Date.Date , f.Montant , Facture.Etat , Fournisseur.type
            FROM dbo.fait f 
            JOIN dbo.[Dimension fournisseur] fournisseur ON f.FK_Fournisseur = fournisseur.Pk_fournisseur
            JOIN dbo.[Dimensions facture] facture ON f.FK_facture = facture.PK_facture
            JOIN dbo.[Dimension_dates] date ON f.FK_Date = Date.DateKey WHERE facture.etat = 'Prét pour paiement'"""

        results = executer_requete(conn, query)  # Vous devez implémenter cette fonction

        if results:
            for result in results:
                # Récupérer les détails de chaque facture
                fournisseur,reference, facture, date, montant, etat,type = result
                date_str = date.strftime("%Y-%m-%d")
                dispatcher.utter_message(
                        text=f"Le fournisseur {fournisseur} doit un montant total de {montant} avec un état {etat}."
                    )
        else:
            # Aucun montant trouvé pour l'état Pret
            dispatcher.utter_message(text=f"Aucun montant trouvé pour l'état 'Pret'.")

        return []



# -----------------------------------------------------------------------------------------------------------------
import re

class ActionGetTypeByAmount(Action):
    def name(self) -> Text:
        return "action_get_type_by_amount"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Obtenir le texte du message de l'utilisateur
        message = tracker.latest_message.get("text")
        
        # Extraire le montant à partir du texte du message en utilisant une expression régulière
        matches = re.findall(r'\d+', message)
        amount = int(matches[0]) if matches else None
        if not amount:
            dispatcher.utter_message("Je n'ai pas compris le montant.")
            return []
        # Connexion à la base de données
        conn = se_connecter_a_ssms() 
        # Interagir avec la base de données pour obtenir le type correspondant au montant
        cursor = conn.cursor()
        cursor.execute("SELECT fournisseur.type FROM dbo.fait f JOIN dbo.[Dimension fournisseur] fournisseur ON f.FK_Fournisseur = fournisseur.Pk_fournisseur WHERE f.Montant = ?", (amount,))
        result = cursor.fetchone()
        conn.close()
        if result:
            type = result[0]
            dispatcher.utter_message(f"Le type pour le montant {amount} est {type}.")
        else:
            dispatcher.utter_message("Je n'ai pas trouvé de type pour ce montant.")

        return []
# -----------------------------------------------------------------------------------------------------------------

import re

class MontantTotalParType(Action):
    def name(self) -> Text:
        return "Montant_Total_Par_Type"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        # Se connecter à la base de données
        conn = se_connecter_a_ssms()  # Assurez-vous d'avoir cette fonction implémentée

        if conn:
            # Exécuter la requête SQL pour obtenir les montants dus par fournisseur
            query = f""" SELECT Fournisseur.type , SUM(f.Montant) AS MontantTotal 
                    FROM dbo.fait f 
                    JOIN dbo.[Dimension fournisseur] fournisseur ON f.FK_Fournisseur = fournisseur.Pk_fournisseur
                    GROUP BY type """  
            results = executer_requete(conn, query)  # Assurez-vous d'avoir cette fonction implémentée

            if results:
                for row in results:
                    type = row[0]
                    montant_total = row[1]
                    dispatcher.utter_message(
                        text=f"Type: {type} -> {montant_total}."
                    )
            else:
                dispatcher.utter_message(text="Désolé, je n'ai pas pu trouver les informations sur les montants dus par type.")
        else:
            dispatcher.utter_message(text="Désolé, je n'ai pas pu me connecter à la base de données.")

        return []

# -----------------------------------------------------------------------------------------------------------------


class MontantParType(Action):
    def name(self) -> Text:
        return "Montant_Par_Type"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Récupérer la valeur du slot 'type' de l'objet tracker
        requested_type = tracker.get_slot("type")
        
        if requested_type is None:
            dispatcher.utter_message(text="Désolé, je n'ai pas compris le type demandé.")
            return []

        # Connexion à la base de données (assurez-vous que "conn" est correctement défini)
        cursor = conn.cursor()
        # Requête SQL pour obtenir tous les montants correspondant à un type donné
        query = """SELECT Fournisseur.Fournisseur, f.Montant, Fournisseur.type
                   FROM dbo.fait f 
                   JOIN dbo.[Dimension fournisseur] fournisseur ON f.FK_Fournisseur = fournisseur.Pk_fournisseur
                   WHERE Fournisseur.type = ?"""

        # Exécuter la requête SQL avec le type en tant que paramètre sécurisé
        cursor.execute(query, (requested_type,))
        results = cursor.fetchall()

        if results:
            for result in results:
                # Récupérer les détails de chaque facture
                fournisseur, montant, type = result
                dispatcher.utter_message(
                    text=f"Le fournisseur {fournisseur} a un montant de {montant} pour le type {type}."
                )
        else:
            # Aucun montant trouvé pour le type demandé
            dispatcher.utter_message(text=f"Aucun montant trouvé pour le type demandé.")

        return []


# -----------------------------------------------------------------------------------------------------------------

class MontantParFournisseur(Action):
    def name(self) -> Text:
        return "Montant_Par_Fournisseur"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Récupérer la valeur du slot 'Fournisseur' de l'objet tracker
        requested_fournisseur = tracker.get_slot("Fournisseur")
        
        if requested_fournisseur is None:
            dispatcher.utter_message(text="Désolé, je n'ai pas compris le fournisseur demandé.")
            return []


            # Connexion à la base de données (assurez-vous que "conn" est correctement défini)
        cursor = conn.cursor()
            
            # Requête SQL pour obtenir les montants correspondant à un fournisseur donné
        query = """SELECT Fournisseur.Fournisseur, f.Montant, facture.etat , facture.Facture
                    FROM dbo.Fait f 
                    JOIN dbo.[Dimensions facture] facture ON f.FK_facture = facture.PK_facture
                    JOIN dbo.[Dimension Fournisseur] Fournisseur ON f.FK_Fournisseur = Fournisseur.Pk_Fournisseur
                    WHERE Fournisseur.Fournisseur = ?"""

            # Exécuter la requête SQL avec le fournisseur en tant que paramètre sécurisé
        cursor.execute(query, (requested_fournisseur,))
        results = cursor.fetchall()

        if results:
            for result in results:
                    # Récupérer les détails de chaque facture
                fournisseur, montant, etat , facture = result
                dispatcher.utter_message(
                    text=f"Le fournisseur {fournisseur} pour la facture {facture} a un montant de {montant} pour l'etat {etat}."
                )
        else:
                # Aucun montant trouvé pour le fournisseur demandé
            dispatcher.utter_message(text=f"Aucun montant trouvé pour le fournisseur demandé.")


        return []

# -----------------------------------------------------------------------------------------------------------------

class ActionCountFournisseur(Action):
    def name(self):
        return "action_count_Fournisseur"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:            
            # Exécutez la requête pour compter les fournisseurs
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM dbo.[Dimension Fournisseur]")
            count = cursor.fetchone()[0]  # Obtenez le nombre de fournisseurs

            # Envoyez la réponse au dispatcher pour la réponse de l'assistant
            dispatcher.utter_message(text=f"Vous avez {count} fournisseurs dans votre base de données.")
        except Exception as e:
            # En cas d'erreur, affichez un message d'erreur
            dispatcher.utter_message(text="Une erreur s'est produite lors de la connexion à la base de données.")

        return []
    

# -----------------------------------------------------------------------------------------------------------------

class ActionCountType(Action):
    def name(self):
        return "action_count_Type"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:            
            # Exécutez la requête pour compter les fournisseurs
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(distinct(Type)) FROM dbo.[Dimension Fournisseur]")
            count = cursor.fetchone()[0]  # Obtenez le nombre de fournisseurs

            # Envoyez la réponse au dispatcher pour la réponse de l'assistant
            dispatcher.utter_message(text=f"Vous avez {count} Types dans votre base de données.")
        except Exception as e:
            # En cas d'erreur, affichez un message d'erreur
            dispatcher.utter_message(text="Une erreur s'est produite lors de la connexion à la base de données.")

        return []
    
# -----------------------------------------------------------------------------------------------------------------

class ActionRecupererMontantParDate(Action):
    def name(self):
        return "action_Recuperer_Montant_Par_Date"

    def run(self, dispatcher, tracker, domain):
        # Extraire les slots de date du tracker
        start_date = tracker.get_slot("start_date")
        end_date = tracker.get_slot("end_date")

        # Se connecter à la base de données
        conn = se_connecter_a_ssms()

        # Exécuter la requête SQL pour récupérer les montants à payer
        cursor = conn.cursor()
        query = f"""SELECT DISTINCT f.montant 
                    FROM dbo.fait f 
                    JOIN dbo.[Dimension_dates] date ON f.FK_Date = Date.DateKey                 
                    WHERE date.date BETWEEN ? AND ?"""
        cursor.execute(query, (start_date, end_date))
        rows = cursor.fetchall()

        # Rassembler les montants récupérés
        montants = [row[0] for row in rows]
        # Envoyer les montants récupérés au dispatcher
        dispatcher.utter_message(f"Les montants à payer sont : {', '.join(map(str, montants))} ")

        return []

    # -------------------------------------------------------------------------------------------
class ActionObtenirFactureMontant(Action):
    def name(self) -> Text:
        return "action_obtenir_Facture_montant"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        
        # Récupérer l'entité montant du tracker
        Facture = tracker.get_slot("Facture")  # Ajout de facture_entity pour utiliser plus tard
        
        # Se connecter à la base de données
        conn = se_connecter_a_ssms()  # Vous devez implémenter cette fonction

        if conn:
            # Exécuter la requête SQL pour obtenir le montant de la facture
                cursor = conn.cursor()
                query = f"""
                    SELECT f.montant,facture.facture,fournisseur.fournisseur,date.date
                    FROM dbo.fait f
                    JOIN dbo.[Dimension_dates] date ON f.FK_Date = Date.DateKey
                    JOIN dbo.[Dimensions facture] facture ON f.FK_facture = facture.PK_facture
                    JOIN dbo.[Dimension Fournisseur] Fournisseur ON f.FK_Fournisseur = Fournisseur.Pk_Fournisseur
                    WHERE facture.facture = ?
                """
                cursor.execute(query, (Facture,)) 
                results = cursor.fetchall()

                if results:
                    for result in results:
                    # Récupérer les détails de chaque facture
                        montant,Facture,Fournisseur,Date = result
                        dispatcher.utter_message(
                        text=f"La facture {Facture} est établie au nom du {Fournisseur}, d'un montant de {montant}, et datée du {Date}."
                )
                else:
                    dispatcher.utter_message(text="Désolé, je n'ai pas pu me connecter à la base de données.")
        
        return []

# -------------------------------------------------------------------------------------------
    
class ActionCountFacture(Action):
    def name(self):
        return "action_count_Facture"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:            
            # Exécutez la requête pour compter les Facture
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(Facture) FROM dbo.[Dimensions facture]")
            count = cursor.fetchone()[0]  # Obtenez le nombre de facture

            # Envoyez la réponse au dispatcher pour la réponse de l'assistant
            dispatcher.utter_message(text=f"Vous avez {count} facture dans votre base de données.")
        except Exception as e:
            # En cas d'erreur, affichez un message d'erreur
            dispatcher.utter_message(text="Une erreur s'est produite lors de la connexion à la base de données.")

        return []


 # -------------------------------------------------------------------------------------------

class TopFournisseurs(Action):
    def name(self) -> Text:
        return "action_top_fournisseurs"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Extraire la valeur du slot "top"
        top_value = tracker.get_slot("top")
        if top_value is None:
            top_value = 5  # Par défaut, si aucun slot n'est fourni, on utilise top 5
        else:
            try:
                top_value = int(top_value)
            except ValueError:
                dispatcher.utter_message(text="La valeur de top n'est pas valide.")
                return []

        # Connexion à la base de données (assurez-vous que "conn" est correctement défini)
        conn = se_connecter_a_ssms()

        # Requête SQL pour obtenir les top fournisseurs par montant
        query = f"""SELECT TOP {top_value} Fournisseur.Fournisseur, SUM(f.Montant) as Total_Montant
                    FROM dbo.Fait f 
                    JOIN dbo.[Dimension Fournisseur] Fournisseur ON f.FK_Fournisseur = Fournisseur.Pk_Fournisseur
                    GROUP BY Fournisseur.Fournisseur
                    ORDER BY Total_Montant DESC"""

        # Exécuter la requête SQL
        results = executer_requete(conn, query)

        if results:
            for idx, result in enumerate(results, start=1):
                fournisseur, total_montant = result
                dispatcher.utter_message(
                    text=f"{idx}. {fournisseur} : {total_montant} "
                )
        else:
            dispatcher.utter_message(text="Aucun résultat trouvé pour les top fournisseurs.")

        return []
    
# -----------------------------------------------------------------------------
    
class TopType(Action):
    def name(self) -> Text:
        return "action_top_Type"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Extraire la valeur du slot "top"
        top_value = tracker.get_slot("top")
        if top_value is None:
            top_value = 5  # Par défaut, si aucun slot n'est fourni, on utilise top 5
        else:
            try:
                top_value = int(top_value)
            except ValueError:
                dispatcher.utter_message(text="La valeur de top n'est pas valide.")
                return []

        # Connexion à la base de données (assurez-vous que "conn" est correctement défini)
        conn = se_connecter_a_ssms()

        # Requête SQL pour obtenir les top fournisseurs par montant
        query = f"""SELECT TOP {top_value} Fournisseur.Type, SUM(f.Montant) as Total_Montant
                    FROM dbo.Fait f 
                    JOIN dbo.[Dimension Fournisseur] Fournisseur ON f.FK_Fournisseur = Fournisseur.Pk_Fournisseur
                    GROUP BY Fournisseur.Type
                    ORDER BY Total_Montant DESC"""

        # Exécuter la requête SQL
        results = executer_requete(conn, query)

        if results:
            for idx, result in enumerate(results, start=1):
                Type, total_montant = result
                dispatcher.utter_message(
                    text=f"{idx}. {Type} : {total_montant} "
                )
        else:
            dispatcher.utter_message(text="Aucun résultat trouvé pour les top Type.")

        return []

# -----------------------------------------------------------------------------
    
class LessFournisseurs(Action):
    def name(self) -> Text:
        return "action_Less_fournisseurs"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Extraire la valeur du slot "top"
        top_value = tracker.get_slot("top")
        if top_value is None:
            top_value = 5  # Par défaut, si aucun slot n'est fourni, on utilise top 5
        else:
            try:
                top_value = int(top_value)
            except ValueError:
                dispatcher.utter_message(text="La valeur de top n'est pas valide.")
                return []

        # Connexion à la base de données (assurez-vous que "conn" est correctement défini)
        conn = se_connecter_a_ssms()

        # Requête SQL pour obtenir les top fournisseurs par montant (en excluant les montants nuls)
        query = f"""SELECT TOP {top_value} Fournisseur.Fournisseur, SUM(f.Montant) as Total_Montant
                    FROM dbo.Fait f 
                    JOIN dbo.[Dimension Fournisseur] Fournisseur ON f.FK_Fournisseur = Fournisseur.Pk_Fournisseur
                    WHERE f.Montant > 0
                    GROUP BY Fournisseur.Fournisseur
                    ORDER BY Total_Montant ASC"""  # Tri ascendant

        # Exécuter la requête SQL
        results = executer_requete(conn, query)

        if results:
            for idx, result in enumerate(results, start=1):
                fournisseur, total_montant = result
                dispatcher.utter_message(
                    text=f"{idx}. {fournisseur} : {total_montant} "
                )
        else:
            dispatcher.utter_message(text="Aucun résultat trouvé pour les top fournisseurs.")

        return []

# -----------------------------------------------------------------------------
 
class ActionFournisseursZero(Action):
    def name(self):
        return "action_fournisseurs_zero"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        try:
            # Connexion à la base de données
            conn = se_connecter_a_ssms()

            # Exécuter la requête SQL pour récupérer les fournisseurs avec un montant de 0
            query = f"""SELECT DISTINCT fournisseur.fournisseur 
                        FROM dbo.Fait f 
                        JOIN dbo.[Dimension Fournisseur] Fournisseur ON f.FK_Fournisseur = Fournisseur.Pk_Fournisseur
                        WHERE montant = 0"""
            results = executer_requete(conn, query)

            # Si des résultats sont trouvés, les envoyer au chatbot
            if results:
                fournisseurs = [row[0] for row in results]
                dispatcher.utter_message("Les fournisseurs qu'on a jamais travailler avec eux sont : {}".format(", ".join(fournisseurs)))
            else:
                dispatcher.utter_message("Aucun fournisseur n'a été trouvé.")

        except Exception as e:
            dispatcher.utter_message("Une erreur s'est produite lors de la récupération des fournisseurs : {}".format(str(e)))

        return []
    
# ------------------------------------------------------------------------------

class ActionMontantTotalFacture(Action):
    def name(self) -> Text:
        return "action_montant_total_facture"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        # Se connecter à la base de données
        conn = se_connecter_a_ssms()  # Assurez-vous d'avoir cette fonction implémentée

        if conn:
            # Exécuter la requête SQL pour obtenir les montants dus par fournisseur
            query = f"""
            SELECT Fournisseur.Fournisseur , facture.Facture , SUM(f.Montant) AS MontantTotal
            FROM dbo.fait f 
            JOIN dbo.[Dimensions facture] facture ON f.FK_facture = facture.PK_facture
            JOIN dbo.[Dimension fournisseur] fournisseur ON f.FK_Fournisseur = fournisseur.Pk_fournisseur
            GROUP BY fournisseur.Fournisseur, facture.Facture
            """  
            results = executer_requete(conn, query)  # Assurez-vous d'avoir cette fonction implémentée

            if results:
                for row in results:
                    fournisseur = row[0]
                    facture = row[1]
                    montant_total = row[2]
                    dispatcher.utter_message(
                        text=f"La facture {facture} pour le fournisseur {fournisseur} doit un montant total de {montant_total}."
                    )
            else:
                dispatcher.utter_message(text="Désolé, je n'ai pas pu trouver les informations sur les montants dus par facture.")
        else:
            dispatcher.utter_message(text="Désolé, je n'ai pas pu me connecter à la base de données.")

        return []
 
#---------------------------------------------------------------------------------------------

    
class ActionCalculerSommeTotal(Action):
    def name(self):
        return "action_calculer_Somme_montant"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        conn = se_connecter_a_ssms()
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(montant) FROM dbo.fait f")
        total = cursor.fetchone()[0]
        dispatcher.utter_message("Le montant total des factures est : " + str(total))
        return []

#---------------------------------------------------------------------------------------------


class ActionCalculerMontantTotalParAnnee(Action):
    def name(self):
        return "action_calculer_montant_total_par_annee"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        year = tracker.get_slot("Année")
        conn = se_connecter_a_ssms()
        cursor = conn.cursor()
        cursor.execute("SELECT YEAR(Date), SUM(f.montant) FROM dbo.fait f JOIN dbo.[Dimension_dates] date ON f.FK_Date = Date.DateKey WHERE YEAR(Date) = ? GROUP BY YEAR(Date)", (year,))
        print("------",year)
        result = cursor.fetchone()
        if result:
            year, total = result
            dispatcher.utter_message(f"Le montant total des factures pour l'année {year} est : {total}")
        else:
            dispatcher.utter_message("Aucune facture trouvée pour cette année.")
        return []
    

#---------------------------------------------------------------------------------------------
  

class ActionGetFactureParMois(Action):
    def name(self) -> Text:
        return "action_get_Facture_mois"

    def preprocess_month(self, month: Text) -> Text:
        """
        Preprocesses the month entity to remove accents and circumflexes.
        """
        month = month.lower()
        month = month.replace('é', 'e').replace('ê', 'e').replace('û', 'u').replace('û', 'u').replace('ô', 'o').replace('î', 'i').replace('è', 'e')
        return month

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        month_map = {
            "janvier": "01",
            "fevrier": "02",
            "mars": "03",
            "avril": "04",
            "mai": "05",
            "juin": "06",
            "juillet": "07",
            "aout": "08",
            "septembre": "09",
            "octobre": "10",
            "novembre": "11",
            "decembre": "12"
        }

        month_entity = tracker.get_slot('month')

        if month_entity:
            preprocessed_month = self.preprocess_month(month_entity)
            month_num = month_map.get(preprocessed_month)
            if month_num:
                conn = se_connecter_a_ssms()        
                cursor = conn.cursor()
                cursor.execute("SELECT SUM(f.montant) FROM dbo.fait f JOIN dbo.[Dimension_dates] date ON f.FK_Date = date.DateKey WHERE MONTH(date) = ?", (month_num,))
                total_montant = cursor.fetchone()[0]

                if total_montant:
                    dispatcher.utter_message(f"Le montant total des factures pour le mois de {month_entity} est {total_montant}.")
                else:
                    dispatcher.utter_message(f"Aucune donnée disponible pour le mois de {month_entity}.")
            else:
                dispatcher.utter_message("Mois invalide.")
        else:
            dispatcher.utter_message("Je n'ai pas compris le mois.")

        return []
    
# ---------------------------------------------------------------------------------
class ActionMontantTotalEntre2Dates(Action):
    def name(self) -> Text:
        return "action_montant_total_entre_2_dates"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        # Se connecter à la base de données
        conn = se_connecter_a_ssms()  # Assurez-vous d'avoir cette fonction implémentée

        if conn:
            # Récupérer les années à partir des slots
            année_debut = tracker.get_slot('AnnéeD')
            année_fin = tracker.get_slot('AnnéeF')

            if année_debut and année_fin:
                # Exécuter la requête SQL pour obtenir les montants des factures et les détails des factures entre les années spécifiées
                query = f"""
                SELECT facture.Facture, fournisseur.Fournisseur, f.Montant
                FROM dbo.fait f 
                JOIN dbo.[Dimensions facture] facture ON f.FK_facture = facture.PK_facture
                JOIN dbo.[Dimension fournisseur] fournisseur ON f.FK_Fournisseur = fournisseur.Pk_fournisseur
                JOIN dbo.[Dimension_dates] date ON f.FK_Date = date.DateKey
                WHERE YEAR(date.date) BETWEEN {année_debut} AND {année_fin}
                """
                results = executer_requete(conn, query)  # Assurez-vous d'avoir cette fonction implémentée

                if results:
                    montant_total = 0
                    for row in results:
                        facture = row[0]
                        fournisseur = row[1]
                        montant = row[2]
                        montant_total += montant
                        dispatcher.utter_message(
                            # text=f"La facture {facture} pour le fournisseur {fournisseur} a un montant de {montant}."
                        )
                    dispatcher.utter_message(
                        text=f"Le montant total des factures entre {année_debut} et {année_fin} est de {montant_total}."
                    )
                else:
                    dispatcher.utter_message(text="Désolé, je n'ai pas pu trouver les informations sur les factures pour les années spécifiées.")
            else:
                dispatcher.utter_message(text="Veuillez spécifier à la fois l'année de début et l'année de fin.")
        else:
            dispatcher.utter_message(text="Désolé, je n'ai pas pu me connecter à la base de données.")

        return []




#---------------------------------------------fonctionne pas-----------------------------------------------------

    
class ActionObtenirMontantAnnee(Action):
    def name(self) -> Text:
        return "action_obtenir_montant_annee"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Obtenir la date de la requête de l'utilisateur
        date = tracker.get_slot('Année')
        
        # Requête SQL pour obtenir tous les montants correspondant à l'année
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT f.montant FROM dbo.fait f JOIN dbo.[Dimension_dates] date ON f.FK_Date = Date.DateKey  WHERE YEAR(date) = ?", (date,))
        rows = cursor.fetchall()
        
        if rows:
            montants = [row[0] for row in rows]
            montant_str = ", ".join(str(montant) for montant in montants)
            dispatcher.utter_message(text=f"Les montants pour l'année {date} sont : {montant_str} TND.")
        else:
            dispatcher.utter_message(text=f"Aucun montant trouvé pour l'année {date}.")
        
        return []
    

    # -------------------------------------------------------------------
class ActionMontantTotalEntreLesDates(Action):
    def name(self) -> Text:
        return "action_montant_total_entre_les_dates"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        # Se connecter à la base de données
        conn = se_connecter_a_ssms()  # Assurez-vous d'avoir cette fonction implémentée

        if conn:
            # Initialiser les parties de la requête SQL
            where_conditions = []

            # Récupérer les slots non nuls
            slots = {
                "AnnéeD": tracker.get_slot('AnnéeD'),
                "AnnéeF": tracker.get_slot('AnnéeF'),
                "monthD": tracker.get_slot('monthD'),
                "monthF": tracker.get_slot('monthF'),
                "JourD": tracker.get_slot('JourD'),
                "JourF": tracker.get_slot('JourF')
            }
            if slots["AnnéeD"] is None and slots["AnnéeF"] is None:
                slots["AnnéeD"] = 2023
            # Générer les conditions pour les slots non nuls
            for slot, value in slots.items():
                if value is not None:
                    if slot.startswith("Année"):
                        where_conditions.append(f"YEAR(date.date) = {value}")
                    elif slot.startswith("month"):
                        where_conditions.append(f"MONTH(date.date) = {value}")
                    elif slot.startswith("Jour"):
                        where_conditions.append(f"DAY(date.date) = {value}")

            # Générer la clause WHERE
            where_clause = " AND ".join(where_conditions)

            # Exécuter la requête SQL avec la clause WHERE dynamique
            query = f"""
            SELECT facture.Facture, fournisseur.Fournisseur, f.Montant
            FROM dbo.fait f 
            JOIN dbo.[Dimensions facture] facture ON f.FK_facture = facture.PK_facture
            JOIN dbo.[Dimension fournisseur] fournisseur ON f.FK_Fournisseur = fournisseur.Pk_fournisseur
            JOIN dbo.[Dimension_dates] date ON f.FK_Date = date.DateKey
            WHERE {where_clause}
            """
            results = executer_requete(conn, query)  # Assurez-vous d'avoir cette fonction implémentée

            if results:
                montant_total = 0
                for row in results:
                    facture = row[0]
                    fournisseur = row[1]
                    montant = row[2]
                    montant_total += montant
                    dispatcher.utter_message(
                        text=f"La facture {facture} pour le fournisseur {fournisseur} a un montant de {montant}."
                    )
                dispatcher.utter_message(
                    text=f"Le montant total des factures est de {montant_total}."
                )
            else:
                dispatcher.utter_message(text="Désolé, je n'ai pas pu trouver les informations sur les factures pour les dates spécifiées.")
        else:
            dispatcher.utter_message(text="Désolé, je n'ai pas pu me connecter à la base de données.")

        return []
