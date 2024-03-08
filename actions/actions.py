
from tkinter import EventType
import pyodbc

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
                        dispatcher.utter_message(template="utter_details_facture", 
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
                        dispatcher.utter_message(template="utter_details_facture", 
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
                        dispatcher.utter_message(template="utter_details_facture", 
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
        cursor.execute("SELECT f.montant FROM dbo.fait f JOIN dbo.[Dimension_dates] date ON f.FK_Date = Date.DateKey  WHERE date.date = ?", (date,))
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
                        text=f"La référence {reference}, fournisseur {fournisseur}, facture {facture}, date {date_str} doit un montant total de {montant} avec un état {etat}."
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
                        text=f"La référence {reference}, fournisseur {fournisseur}, facture {facture}, date {date_str} doit un montant total de {montant} avec un état {etat}."
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
                        text=f"La référence {reference}, fournisseur {fournisseur}, facture {facture}, date {date_str} doit un montant total de {montant} avec un état {etat}."
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
        cursor.execute("SELECT founrisseur.type FROM dbo.fait f JOIN dbo.[Dimension fournisseur] fournisseur ON f.FK_Fournisseur = fournisseur.Pk_fournisseur WHERE f.Montant = ?", (amount,))
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
            query = "SELECT type, SUM(Montant) AS MontantTotal FROM dbo.source GROUP BY type"
            results = executer_requete(conn, query)  # Assurez-vous d'avoir cette fonction implémentée

            if results:
                for row in results:
                    type = row[0]
                    montant_total = row[1]
                    dispatcher.utter_message(
                        text=f"Type' {type} -> {montant_total}."
                    )
            else:
                dispatcher.utter_message(text="Désolé, je n'ai pas pu trouver les informations sur les montants dus par type.")
        else:
            dispatcher.utter_message(text="Désolé, je n'ai pas pu me connecter à la base de données.")

        return []






