
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
from rasa_sdk.events import SlotSet

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
                    montant_formatte = "{:,.2f}".format(montant)
                    dispatcher.utter_message(template="utter_montant", montant=montant_formatte, Référence=ref)  # Assurez-vous que la valeur du slot montant est fournie
                else:
                    dispatcher.utter_message(text="Désolé, je n'ai pas pu trouver le montant pour cette Reference.")
            else:
                dispatcher.utter_message(text="Désolé, je n'ai pas pu me connecter à la base de données.")
        else:
            dispatcher.utter_message(text="Désolé, je n'ai pas pu extraire le numéro de Reference.")
        
        return [SlotSet(slot, None) for slot in ["start_date", "end_date", "Etat", "type", "Montant", "Date", "Fournisseur", "Facture", "top", "Jour", "JourD", "JourF", "month", "monthD", "monthF", "Année", "AnnéeD", "AnnéeF", "session_started_metadata"]]


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
                        montant_formatte = "{:,.2f}".format(montant) 
                        dispatcher.utter_message(template="utter_inf", 
                                                 reference=reference, 
                                                 fournisseur=fournisseur, 
                                                 facture=facture, 
                                                 date=date_str, 
                                                 montant=montant_formatte, 
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

        return [SlotSet(slot, None) for slot in ["start_date", "end_date", "Etat", "type", "Montant", "Date", "Fournisseur", "Facture", "top", "Jour", "JourD", "JourF", "month", "monthD", "monthF", "Année", "AnnéeD", "AnnéeF", "session_started_metadata"]]


 
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
                        montant_formatte = "{:,.2f}".format(montant)
                        dispatcher.utter_message(template="utter_sup", 
                                                 reference=reference, 
                                                 fournisseur=fournisseur, 
                                                 facture=facture, 
                                                 date=date_str, 
                                                 montant=montant_formatte, 
                                                 etat=etat, 
                                                 type_facture=type_facture)
                else:
                    dispatcher.utter_message(text="Aucune facture trouvée avec un montant supérieur à celui spécifié.")
            else:
                dispatcher.utter_message(text="Désolé, je n'ai pas pu me connecter à la base de données.")
        else:
            dispatcher.utter_message(text="Désolé, je n'ai pas pu extraire le montant spécifié.")
        
        return [SlotSet(slot, None) for slot in ["start_date", "end_date", "Etat", "type", "Montant", "Date", "Fournisseur", "Facture", "top", "Jour", "JourD", "JourF", "month", "monthD", "monthF", "Année", "AnnéeD", "AnnéeF", "session_started_metadata"]]


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
                        montant_formatte = "{:,.2f}".format(montant)
                        dispatcher.utter_message(template="utter_egal", 
                                                 reference=reference, 
                                                 fournisseur=fournisseur, 
                                                 facture=facture, 
                                                 date=date_str, 
                                                 montant=montant_formatte, 
                                                 etat=etat, 
                                                 type_facture=type_facture)
                else:
                    dispatcher.utter_message(text="Aucune facture trouvée avec un montant égal à celui spécifié.")
            else:
                dispatcher.utter_message(text="Désolé, je n'ai pas pu me connecter à la base de données.")
        else:
            dispatcher.utter_message(text="Désolé, je n'ai pas pu extraire le montant spécifié.")
        
        return [SlotSet(slot, None) for slot in ["start_date", "end_date", "Etat", "type", "Montant", "Date", "Fournisseur", "Facture", "top", "Jour", "JourD", "JourF", "month", "monthD", "monthF", "Année", "AnnéeD", "AnnéeF", "session_started_metadata"]]

    
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
            query = """
            SELECT Fournisseur.Fournisseur, SUM(f.Montant) AS MontantTotalFournisseur
            FROM dbo.fait f 
            JOIN dbo.[Dimension fournisseur] Fournisseur ON f.FK_Fournisseur = Fournisseur.Pk_fournisseur
            GROUP BY Fournisseur.Fournisseur
            """  
            results = executer_requete(conn, query)  # Assurez-vous d'avoir cette fonction implémentée

            if results:
                montants_fournisseurs = []
                for row in results:
                    fournisseur = row[0]
                    montant_total = row[1]
                    dispatcher.utter_message(
                        text=f"Le fournisseur {fournisseur} doit un montant total de {montant_total}."
                    )
                    montants_fournisseurs.append(montant_total)

                somme_total_montants = sum(montants_fournisseurs)
                dispatcher.utter_message(
                    text=f"La somme totale des montants dus par les fournisseurs est {somme_total_montants}."
                )
                
            else:
                dispatcher.utter_message(text="Désolé, je n'ai pas pu trouver les informations sur les montants dus par fournisseur.")
        else:
            dispatcher.utter_message(text="Désolé, je n'ai pas pu me connecter à la base de données.")

        return [SlotSet(slot, None) for slot in ["start_date", "end_date", "Etat", "type", "Montant", "Date", "Fournisseur", "Facture", "top", "Jour", "JourD", "JourF", "month", "monthD", "monthF", "Année", "AnnéeD", "AnnéeF", "session_started_metadata"]]



# -----------------------------------------------------------------------------------------------------------------

from datetime import datetime

class ActionObtenirMontantDate(Action):
    def name(self) -> Text:
        return "action_obtenir_montant_Date"

    def normalize_date(self, date_str):
        # Essayer de convertir la date en YYYY-MM-DD
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            return date_obj.strftime('%Y-%m-%d')
        except ValueError:
            pass
        
        # Essayer de convertir la date en DD-MM-YYYY
        try:
            date_obj = datetime.strptime(date_str, '%d-%m-%Y')
            return date_obj.strftime('%Y-%m-%d')
        except ValueError:
            pass
                
        # Si aucun format ne correspond, retourner None
        return None

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Obtenir la date de la requête de l'utilisateur
        date_str = tracker.get_slot('Date')
        
        # Normaliser la date au format YYYY-MM-DD
        normalized_date = self.normalize_date(date_str)
        
        if normalized_date is None:
            dispatcher.utter_message(text="Format de date non valide. Veuillez entrer une date au format YYYY-MM-DD, DD-MM-YYYY ou DD MM YYYY.")
            return []
        
        # Requête SQL pour obtenir tous les montants correspondant à la date
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT f.montant FROM dbo.fait f JOIN dbo.[Dimension_dates] date ON f.FK_Date = Date.DateKey  WHERE date.date = ?", (normalized_date,))
        rows = cursor.fetchall()
        
        if rows:
            amounts = [row[0] for row in rows]
            amount_str = ", ".join(str(amount) for amount in amounts)
            dispatcher.utter_message(text=f"Les montants pour la date {normalized_date} sont : {amount_str} TND.")
        else:
            dispatcher.utter_message(text=f"Aucun montant trouvé pour la date {normalized_date}.")
        
        return [SlotSet(slot, None) for slot in ["start_date", "end_date", "Etat", "type", "Montant", "Date", "Fournisseur", "Facture", "top", "Jour", "JourD", "JourF", "month", "monthD", "monthF", "Année", "AnnéeD", "AnnéeF", "session_started_metadata"]]


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

        return [SlotSet(slot, None) for slot in ["start_date", "end_date", "Etat", "type", "Montant", "Date", "Fournisseur", "Facture", "top", "Jour", "JourD", "JourF", "month", "monthD", "monthF", "Année", "AnnéeD", "AnnéeF", "session_started_metadata"]]



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

        total_montant = 0  # Initialise le montant total

        if results:
            for result in results:
                # Récupérer les détails de chaque facture
                fournisseur, reference, facture, date, montant, etat, type = result
                date_str = date.strftime("%Y-%m-%d")
                dispatcher.utter_message(
                        text=f"Le fournisseur {fournisseur} a une facture {facture} d'un montant de {montant} avec un état {etat}."
                    )
                total_montant += montant  # Ajoute le montant au total

            # Affiche le montant total à la fin
            dispatcher.utter_message(text=f"Le montant total des factures validées est de : {total_montant}.")
        else:
            # Aucun montant trouvé pour l'état Validé
            dispatcher.utter_message(text=f"Aucun montant trouvé pour l'état 'Validé'.")

        return [SlotSet(slot, None) for slot in ["start_date", "end_date", "Etat", "type", "Montant", "Date", "Fournisseur", "Facture", "top", "Jour", "JourD", "JourF", "month", "monthD", "monthF", "Année", "AnnéeD", "AnnéeF", "session_started_metadata"]]


# -----------------------------------------------------------------------------------------------------------------
         
class ActionAfficherMontantsEtatCree(Action):
    def name(self) -> Text:
        return "action_afficher_montants_etat_crees"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Connexion à la base de données (assurez-vous que "conn" est correctement défini)
        cursor = conn.cursor()
        # Requête SQL pour obtenir tous les montants correspondant à l'état Créé
        query = """SELECT Fournisseur.Fournisseur , Facture.Référence , Facture.Facture , Date.Date , f.Montant , Facture.Etat , Fournisseur.type
                    FROM dbo.fait f 
                    JOIN dbo.[Dimension fournisseur] fournisseur ON f.FK_Fournisseur = fournisseur.Pk_fournisseur
                    JOIN dbo.[Dimensions facture] facture ON f.FK_facture = facture.PK_facture
                    JOIN dbo.[Dimension_dates] date ON f.FK_Date = Date.DateKey WHERE facture.etat = 'Créé'"""
        results = executer_requete(conn, query)  # Vous devez implémenter cette fonction

        total_montant = 0  # Initialise le montant total

        if results:
            for result in results:
                # Récupérer les détails de chaque facture
                fournisseur, reference, facture, date, montant, etat, type = result
                date_str = date.strftime("%Y-%m-%d")
                dispatcher.utter_message(
                        text=f"Le fournisseur {fournisseur} a une facture {facture} d'un montant de {montant} avec un état {etat}."
                    )
                total_montant += montant  # Ajoute le montant au total

            # Affiche le montant total à la fin
            dispatcher.utter_message(text=f"Le montant total des factures créées est de : {total_montant}.")
        else:
            # Aucun montant trouvé pour l'état Créé
            dispatcher.utter_message(text=f"Aucun montant trouvé pour l'état 'Créé'.")

        return [SlotSet(slot, None) for slot in ["start_date", "end_date", "Etat", "type", "Montant", "Date", "Fournisseur", "Facture", "top", "Jour", "JourD", "JourF", "month", "monthD", "monthF", "Année", "AnnéeD", "AnnéeF", "session_started_metadata"]]

# -----------------------------------------------------------------------------------------------------------------
         
class ActionAfficherMontantsEtatPret(Action):
    def name(self) -> Text:
        return "action_afficher_montants_etat_prets"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Connexion à la base de données (assurez-vous que "conn" est correctement défini)
        cursor = conn.cursor()
        # Requête SQL pour obtenir tous les montants correspondant à l'état Prêt pour paiement
        query = """SELECT Fournisseur.Fournisseur , Facture.Référence , Facture.Facture , Date.Date , f.Montant , Facture.Etat , Fournisseur.type
            FROM dbo.fait f 
            JOIN dbo.[Dimension fournisseur] fournisseur ON f.FK_Fournisseur = fournisseur.Pk_fournisseur
            JOIN dbo.[Dimensions facture] facture ON f.FK_facture = facture.PK_facture
            JOIN dbo.[Dimension_dates] date ON f.FK_Date = Date.DateKey WHERE facture.etat = 'Prét pour paiement'"""

        results = executer_requete(conn, query)  # Vous devez implémenter cette fonction

        total_montant = 0  # Initialise le montant total

        if results:
            for result in results:
                # Récupérer les détails de chaque facture
                fournisseur, reference, facture, date, montant, etat, type = result
                date_str = date.strftime("%Y-%m-%d")
                dispatcher.utter_message(
                        text=f"Le fournisseur {fournisseur} a une facture {facture} d'un montant de {montant} avec un état {etat}."
                    )
                total_montant += montant  # Ajoute le montant au total

            # Affiche le montant total à la fin
            dispatcher.utter_message(text=f"Le montant total des factures prêtes pour paiement est de : {total_montant}.")
        else:
            # Aucun montant trouvé pour l'état Prêt pour paiement
            dispatcher.utter_message(text=f"Aucun montant trouvé pour l'état 'Prêt pour paiement'.")

        return [SlotSet(slot, None) for slot in ["start_date", "end_date", "Etat", "type", "Montant", "Date", "Fournisseur", "Facture", "top", "Jour", "JourD", "JourF", "month", "monthD", "monthF", "Année", "AnnéeD", "AnnéeF", "session_started_metadata"]]

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

        return [SlotSet(slot, None) for slot in ["start_date", "end_date", "Etat", "type", "Montant", "Date", "Fournisseur", "Facture", "top", "Jour", "JourD", "JourF", "month", "monthD", "monthF", "Année", "AnnéeD", "AnnéeF", "session_started_metadata"]]
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
            query = """
                    SELECT Fournisseur.type , SUM(f.Montant) AS MontantTotal 
                    FROM dbo.fait f 
                    JOIN dbo.[Dimension fournisseur] fournisseur ON f.FK_Fournisseur = fournisseur.Pk_fournisseur
                    GROUP BY type 
                    """
            results = executer_requete(conn, query)  # Assurez-vous d'avoir cette fonction implémentée

            if results:
                total_general = 0  # Initialiser le total général à 0
                for row in results:
                    type = row[0]
                    montant_total = row[1]
                    total_general += montant_total  # Ajouter le montant total de chaque type au total général
                    dispatcher.utter_message(
                        text=f"Type: {type} -> Montant total: {montant_total}."
                    )
                # Afficher le montant total général
                dispatcher.utter_message(
                    text=f"Montant total de tous les types: {total_general}."
                )
            else:
                dispatcher.utter_message(text="Désolé, je n'ai pas pu trouver les informations sur les montants dus par type.")
        else:
            dispatcher.utter_message(text="Désolé, je n'ai pas pu me connecter à la base de données.")

        return [SlotSet(slot, None) for slot in ["start_date", "end_date", "Etat", "type", "Montant", "Date", "Fournisseur", "Facture", "top", "Jour", "JourD", "JourF", "month", "monthD", "monthF", "Année", "AnnéeD", "AnnéeF", "session_started_metadata"]]

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

        total_amount = 0  # Variable pour stocker le montant total

        if results:
            fournisseurs = []  # Liste pour stocker les noms des fournisseurs
            for result in results:
                # Récupérer les détails de chaque facture
                fournisseur, montant, _ = result
                total_amount += montant  # Ajouter le montant à la somme totale
                fournisseurs.append(fournisseur)  # Ajouter le nom du fournisseur à la liste
                dispatcher.utter_message(
                    text=f"Le fournisseur {fournisseur} a un montant de {montant} pour le type {requested_type}."
                )

            # Afficher le montant total pour le type spécifié
            dispatcher.utter_message(
                text=f"Le montant total pour le type {requested_type} est : {total_amount}."
            )
        else:
            # Aucun montant trouvé pour le type demandé
            dispatcher.utter_message(text=f"Aucun montant trouvé pour le type demandé.")

        return [SlotSet(slot, None) for slot in ["start_date", "end_date", "Etat", "type", "Montant", "Date", "Fournisseur", "Facture", "top", "Jour", "JourD", "JourF", "month", "monthD", "monthF", "Année", "AnnéeD", "AnnéeF", "session_started_metadata"]]

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

        total_montant = 0  # Initialise le montant total

        if results:
            for result in results:
                # Récupérer les détails de chaque facture
                fournisseur, montant, etat , facture = result
                dispatcher.utter_message(
                    text=f"Le fournisseur {fournisseur} pour la facture {facture} a un montant de {montant} pour l'état {etat}."
                )
                total_montant += montant  # Ajoute le montant au total

            # Affiche le montant total à la fin
            dispatcher.utter_message(text=f"Le montant total des factures pour le fournisseur {requested_fournisseur} est de : {total_montant}.")
        else:
            # Aucun montant trouvé pour le fournisseur demandé
            dispatcher.utter_message(text=f"Aucun montant trouvé pour le fournisseur demandé.")

        return [SlotSet(slot, None) for slot in ["start_date", "end_date", "Etat", "type", "Montant", "Date", "Fournisseur", "Facture", "top", "Jour", "JourD", "JourF", "month", "monthD", "monthF", "Année", "AnnéeD", "AnnéeF", "session_started_metadata"]]

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

        return [SlotSet(slot, None) for slot in ["start_date", "end_date", "Etat", "type", "Montant", "Date", "Fournisseur", "Facture", "top", "Jour", "JourD", "JourF", "month", "monthD", "monthF", "Année", "AnnéeD", "AnnéeF", "session_started_metadata"]]
    

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

        return [SlotSet(slot, None) for slot in ["start_date", "end_date", "Etat", "type", "Montant", "Date", "Fournisseur", "Facture", "top", "Jour", "JourD", "JourF", "month", "monthD", "monthF", "Année", "AnnéeD", "AnnéeF", "session_started_metadata"]]
    
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

        return [SlotSet(slot, None) for slot in ["start_date", "end_date", "Etat", "type", "Montant", "Date", "Fournisseur", "Facture", "top", "Jour", "JourD", "JourF", "month", "monthD", "monthF", "Année", "AnnéeD", "AnnéeF", "session_started_metadata"]]

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
        
        return [SlotSet(slot, None) for slot in ["start_date", "end_date", "Etat", "type", "Montant", "Date", "Fournisseur", "Facture", "top", "Jour", "JourD", "JourF", "month", "monthD", "monthF", "Année", "AnnéeD", "AnnéeF", "session_started_metadata"]]

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

        return [SlotSet(slot, None) for slot in ["start_date", "end_date", "Etat", "type", "Montant", "Date", "Fournisseur", "Facture", "top", "Jour", "JourD", "JourF", "month", "monthD", "monthF", "Année", "AnnéeD", "AnnéeF", "session_started_metadata"]]


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
            top_value = 1  # Par défaut, si aucun slot n'est fourni, on utilise top 5
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

        return [SlotSet(slot, None) for slot in ["start_date", "end_date", "Etat", "type", "Montant", "Date", "Fournisseur", "Facture", "top", "Jour", "JourD", "JourF", "month", "monthD", "monthF", "Année", "AnnéeD", "AnnéeF", "session_started_metadata"]]
    
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
            top_value = 1  # Par défaut, si aucun slot n'est fourni, on utilise top 1
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

        return [SlotSet(slot, None) for slot in ["start_date", "end_date", "Etat", "type", "Montant", "Date", "Fournisseur", "Facture", "top", "Jour", "JourD", "JourF", "month", "monthD", "monthF", "Année", "AnnéeD", "AnnéeF", "session_started_metadata"]]

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

        return [SlotSet(slot, None) for slot in ["start_date", "end_date", "Etat", "type", "Montant", "Date", "Fournisseur", "Facture", "top", "Jour", "JourD", "JourF", "month", "monthD", "monthF", "Année", "AnnéeD", "AnnéeF", "session_started_metadata"]]

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

        return [SlotSet(slot, None) for slot in ["start_date", "end_date", "Etat", "type", "Montant", "Date", "Fournisseur", "Facture", "top", "Jour", "JourD", "JourF", "month", "monthD", "monthF", "Année", "AnnéeD", "AnnéeF", "session_started_metadata"]]
    
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
            query = """
            SELECT Fournisseur.Fournisseur,Facture.Facture,SUM(f.Montant) AS MontantTotalFacture
            FROM dbo.fait f 
            JOIN dbo.[Dimensions facture] Facture ON f.FK_facture = Facture.PK_facture
            JOIN dbo.[Dimension fournisseur] Fournisseur ON f.FK_Fournisseur = Fournisseur.Pk_fournisseur
            GROUP BY Fournisseur.Fournisseur, Facture.Facture
            """  
            results = executer_requete(conn, query)  # Assurez-vous d'avoir cette fonction implémentée

            if results:
                montants_factures = []
                for row in results:
                    fournisseur = row[0]
                    facture = row[1]
                    montant_total_facture = row[2]
                    dispatcher.utter_message(
                        text=f"La facture {facture} pour le fournisseur {fournisseur} doit un montant total de {montant_total_facture}."
                    )
                    montants_factures.append(montant_total_facture)

                somme_total_montants = sum(montants_factures)
                dispatcher.utter_message(
                    text=f"Le montant total des factures est {somme_total_montants}."
                )
                
            else:
                dispatcher.utter_message(text="Désolé, je n'ai pas pu trouver les informations sur les montants dus par facture.")
        else:
            dispatcher.utter_message(text="Désolé, je n'ai pas pu me connecter à la base de données.")

        return [SlotSet(slot, None) for slot in ["start_date", "end_date", "Etat", "type", "Montant", "Date", "Fournisseur", "Facture", "top", "Jour", "JourD", "JourF", "month", "monthD", "monthF", "Année", "AnnéeD", "AnnéeF", "session_started_metadata"]]



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
        year_entity = tracker.get_slot('Année')

        if month_entity:
            preprocessed_month = self.preprocess_month(month_entity)
            month_num = month_map.get(preprocessed_month)
            if month_num:
                if year_entity:
                    conn = se_connecter_a_ssms()        
                    cursor = conn.cursor()
                    cursor.execute("SELECT SUM(f.montant) FROM dbo.fait f JOIN dbo.[Dimension_dates] date ON f.FK_Date = date.DateKey WHERE MONTH(date) = ? AND YEAR(date.date) = ?", (month_num, year_entity,))
                    total_montant = cursor.fetchone()[0]

                    if total_montant:
                        dispatcher.utter_message(f"Le montant total des factures pour le mois de {month_entity} de l'année {year_entity} est {total_montant}.")
                    else:
                        dispatcher.utter_message(f"Aucune donnée disponible pour le mois de {month_entity} de l'année {year_entity}.")
                    return [SlotSet(slot, None) for slot in ["start_date", "end_date", "Etat", "type", "Montant", "Date", "Fournisseur", "Facture", "top", "Jour", "JourD", "JourF", "month", "monthD", "monthF", "Année", "AnnéeD", "AnnéeF", "session_started_metadata"]]
    
                else: 
                    conn = se_connecter_a_ssms()        
                    cursor = conn.cursor()
                    cursor.execute("SELECT SUM(f.montant) FROM dbo.fait f JOIN dbo.[Dimension_dates] date ON f.FK_Date = date.DateKey WHERE MONTH(date) = ?", (month_num,))
                    total_montant = cursor.fetchone()[0]

                    if total_montant:
                        dispatcher.utter_message(f"Le montant total des factures pour le mois de {month_entity} est {total_montant}.")
                    else:
                        dispatcher.utter_message(f"Aucune donnée disponible pour le mois de {month_entity}.")
                    return [SlotSet(slot, None) for slot in ["start_date", "end_date", "Etat", "type", "Montant", "Date", "Fournisseur", "Facture", "top", "Jour", "JourD", "JourF", "month", "monthD", "monthF", "Année", "AnnéeD", "AnnéeF", "session_started_metadata"]]
    
            else:
                dispatcher.utter_message("Mois invalide.")
        else:
            dispatcher.utter_message("Je n'ai pas compris le mois.")

        return [SlotSet(slot, None) for slot in ["start_date", "end_date", "Etat", "type", "Montant", "Date", "Fournisseur", "Facture", "top", "Jour", "JourD", "JourF", "month", "monthD", "monthF", "Année", "AnnéeD", "AnnéeF", "session_started_metadata"]]
    
# ---------------------------------------------------------------------------------
class ActionMontantTotalPluriannuel(Action):
    def name(self) -> Text:
        return "action_montant_total_pluriannuel"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        # Se connecter à la base de données
        conn = se_connecter_a_ssms()  # Assurez-vous d'avoir cette fonction implémentée

        if conn:
            # Récupérer les années spécifiées dans la phrase
            annees = []
            for entity in tracker.latest_message.get("entities"):
                if entity["entity"] == "Année":
                    annees.append(entity["value"])

            if len(annees) >= 1:
                montant_total_pluriannuel = 0
                for annee in annees:
                    # Construire la requête SQL pour obtenir le montant total pour chaque année spécifiée
                    query = f"""
                    SELECT SUM(f.Montant)
                    FROM dbo.fait f 
                    JOIN dbo.[Dimension_dates] date ON f.FK_Date = date.DateKey
                    WHERE YEAR(date.date) = {annee}
                    """
                    results = executer_requete(conn, query)  # Assurez-vous d'avoir cette fonction implémentée

                    if results and results[0][0]:
                        montant_total_pluriannuel += results[0][0]
                    else:
                        dispatcher.utter_message(text=f"Aucune facture trouvée pour l'année {annee}.")

                dispatcher.utter_message(
                    text=f"Le montant total des factures pour les années {', '.join(annees)} est de {montant_total_pluriannuel}."
                )
            else:
                dispatcher.utter_message(text="Je n'ai pas compris pour quelles années vous voulez obtenir le montant total des factures.")
        else:
            dispatcher.utter_message(text="Erreur de connexion à la base de données.")

        return [SlotSet(slot, None) for slot in ["start_date", "end_date", "Etat", "type", "Montant", "Date", "Fournisseur", "Facture", "top", "Jour", "JourD", "JourF", "month", "monthD", "monthF", "Année", "AnnéeD", "AnnéeF", "session_started_metadata"]]
    
#----------------------------------------------------------------------------------------------------
import re

import unicodedata

def preprocess_month_name(month_name):
    # Supprimer les accents et les circonflexes
    normalized_month_name = unicodedata.normalize('NFKD', month_name).encode('ASCII', 'ignore').decode('utf-8')
    return normalized_month_name.lower()

class ActionMontantTotalDeuxMois(Action):
    def name(self) -> Text:
        return "action_total_Deux_mois"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        # Correspondance de motifs pour les noms des mois
        month_patterns = {
            'janvier': 1, 'février': 2, 'mars': 3, 'avril': 4, 'mai': 5, 'juin': 6,
            'juillet': 7, 'août': 8, 'septembre': 9, 'octobre': 10, 'novembre': 11, 'décembre': 12
        }

        # Correspondance de motifs pour les années
        year_pattern = r'\b(20\d{2})\b'

        # Extraction de la phrase de l'utilisateur
        user_input = tracker.latest_message.get("text")

        # Prétraitement des noms des mois dans la phrase de l'utilisateur
        preprocessed_input = preprocess_month_name(user_input)

        # Recherche des noms des mois dans la phrase de l'utilisateur
        detected_months = []
        for month_name, month_number in month_patterns.items():
            if re.search(r'\b{}\b'.format(preprocess_month_name(month_name)), preprocessed_input, re.IGNORECASE):
                detected_months.append((month_name, month_number))

        if not detected_months:
            dispatcher.utter_message("Je n'ai détecté aucun mois dans votre phrase.")
            return []

        # Sélection du premier et dernier mois détectés
        start_month_name, start_month = detected_months[0]
        end_month_name, end_month = detected_months[-1]

        # Recherche de l'année dans la phrase de l'utilisateur
        match = re.search(year_pattern, user_input)
        if not match:
            dispatcher.utter_message("Je n'ai détecté aucune année dans votre phrase.")
            return []
        year = int(match.group(1))

        # Connexion à la base de données
        conn = se_connecter_a_ssms()  # Assurez-vous de remplacer cette fonction par la méthode réelle de connexion

        # Récupération du montant total des factures
        cursor = conn.cursor()
        cursor.execute("""
            SELECT SUM(f.montant) 
            FROM dbo.fait f 
            JOIN dbo.[Dimension_dates] date ON f.FK_Date = date.DateKey
            WHERE MONTH(date.date) BETWEEN ? AND ? AND YEAR(date.date) = ?
            """, (start_month, end_month, year))
        total_montant = cursor.fetchone()[0]


        # Réponse du chatbot
        if total_montant:
            dispatcher.utter_message(f"Le montant total des factures entre {start_month_name} et {end_month_name} pour l'année {year} est de {total_montant}.")
        else:
            dispatcher.utter_message("Aucune facture trouvée pour les mois spécifiés.")

        return [SlotSet(slot, None) for slot in ["start_date", "end_date", "Etat", "type", "Montant", "Date", "Fournisseur", "Facture", "top", "Jour", "JourD", "JourF", "month", "monthD", "monthF", "Année", "AnnéeD", "AnnéeF", "session_started_metadata"]]

#---------------------------------------------------------------------------------------------------------------------------------------------------

class ActionGetFournisseurMoisAnnée(Action):
    def name(self):
        return "action_get_Fournisseur_Mois_Année"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        # Extraire les entités du tracker
        fournisseur = tracker.get_slot("Fournisseur")
        mois = tracker.get_slot("month")
        annee = tracker.get_slot("Année")
        print("annee", annee," mois",mois,"fournisseur", fournisseur)
        # Vérifier si l'année est spécifiée, sinon utiliser 2023 par défaut
        if not annee:
            annee = 2023

        # Convertir le nom du mois en numéro du mois (utilisation d'un dictionnaire pour la correspondance)
        mois_mapping = {
            "janvier": 1, "fevrier": 2, "mars": 3, "avril": 4, "mai": 5, "juin": 6,
            "juillet": 7, "aout": 8, "septembre": 9, "octobre": 10, "novembre": 11, "decembre": 12
        }

        # Vérifier si le mois est en français, si oui, convertir en anglais
        mois = mois.lower()
        if mois in mois_mapping:
            mois = mois_mapping[mois]

        # Connexion à la base de données
        conn = se_connecter_a_ssms()

        # Exécuter la requête SQL pour obtenir le montant total
        cursor = conn.cursor()
        query = f"SELECT SUM(f.montant) FROM dbo.fait f JOIN dbo.[Dimension fournisseur] fournisseur ON f.FK_Fournisseur = fournisseur.Pk_fournisseur JOIN dbo.[Dimension_dates] date ON f.FK_Date = date.DateKey WHERE fournisseur.Fournisseur = ? AND MONTH(date.date) = ? AND YEAR(date.date) = ?"
        cursor.execute(query, (fournisseur, mois, annee))
        total_amount = cursor.fetchone()[0]


        # Envoyer la réponse au dispatcher
        if total_amount:
            dispatcher.utter_message(f"Le montant total pour {fournisseur} pour le mois {mois} de l'année {annee} est {total_amount}.")
        else:
            dispatcher.utter_message(f"Aucun montant trouvé pour {fournisseur} pour le mois {mois} de l'année {annee}.")

        return [SlotSet(slot, None) for slot in ["start_date", "end_date", "Etat", "type", "Montant", "Date", "Fournisseur", "Facture", "top", "Jour", "JourD", "JourF", "month", "monthD", "monthF", "Année", "AnnéeD", "AnnéeF", "session_started_metadata"]]
    
#---------------------------------------------------------------------------------------------------------------------------------------------------

from datetime import datetime
import calendar

class ActionAfficherMontantsEtatValideesDate(Action):
    def name(self) -> Text:
        return "action_afficher_montants_etat_validees_Date"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Récupérer le mois et l'année spécifiés, avec des valeurs par défaut si non spécifiés
        month = tracker.get_slot("month") or datetime.now().month
        year = tracker.get_slot("Année") or 2023  # Assurez-vous que le nom du slot est correct
        
        # Mapping des noms de mois français aux numéros de mois
        month_map = {
            "janvier": 1,
            "fevrier": 2,
            "mars": 3,
            "avril": 4,
            "mai": 5,
            "juin": 6,
            "juillet": 7,
            "aout": 8,
            "septembre": 9,
            "octobre": 10,
            "novembre": 11,
            "decembre": 12
        }
        
        # Vérifier si le mois spécifié est en français et le mapper au numéro de mois correspondant
        if isinstance(month, str):
            month = month_map.get(month.lower(), month)
        
        # Convertir le mois en entier
        month = int(month)
        
        # Convertir l'année en entier
        year = int(year)
        
        # Connexion à la base de données (assurez-vous que "conn" est correctement défini)
        conn = se_connecter_a_ssms() 
        
        # Obtenir le nombre de jours dans le mois spécifié pour la requête
        num_days = calendar.monthrange(year, month)[1]
        
        # Requête SQL pour obtenir tous les montants correspondant à l'état Validé pour le mois et l'année spécifiés
        query = f"""SELECT Fournisseur.Fournisseur , Facture.Facture , Date.Date , SUM(f.Montant) AS MontantTotal
                    FROM dbo.fait f 
                    JOIN dbo.[Dimension fournisseur] fournisseur ON f.FK_Fournisseur = fournisseur.Pk_fournisseur
                    JOIN dbo.[Dimensions facture] facture ON f.FK_facture = facture.PK_facture
                    JOIN dbo.[Dimension_dates] date ON f.FK_Date = Date.DateKey 
                    WHERE facture.etat = 'Validé' AND MONTH(Date.Date) = {month} AND YEAR(Date.Date) = {year}
                    GROUP BY Fournisseur.Fournisseur, Facture.Facture, Date.Date"""
        
        results = executer_requete(conn, query)  # Vous devez implémenter cette fonction

        if results:
            total_amount = 0
            for result in results:
                # Récupérer les détails de chaque facture
                fournisseur, facture, date, montant_total = result
                total_amount += montant_total
                date_str = date.strftime("%Y-%m-%d")
                dispatcher.utter_message(
                    text=f"Le fournisseur {fournisseur} a une facture {facture} avec une etat validé datée du {date_str}."
                )
            dispatcher.utter_message(
                text=f"Le montant total des factures validées pour le mois {calendar.month_name[month]} {year} est de {total_amount}."
            )
        else:
            # Aucun montant trouvé pour l'état Validé ce mois-ci
            dispatcher.utter_message(text=f"Aucun montant trouvé pour l'état 'Validé' pour le mois {calendar.month_name[month]} {year}.")

        return [SlotSet(slot, None) for slot in ["start_date", "end_date", "Etat", "type", "Montant", "Date", "Fournisseur", "Facture", "top", "Jour", "JourD", "JourF", "month", "monthD", "monthF", "Année", "AnnéeD", "AnnéeF", "session_started_metadata"]]


#----------------------------------------créé-------------------------------------------
from datetime import datetime
import calendar

class ActionAfficherMontantsEtatCrééDate(Action):
    def name(self) -> Text:
        return "action_afficher_montants_etat_créé_Date"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Récupérer le mois et l'année spécifiés, avec des valeurs par défaut si non spécifiés
        month = tracker.get_slot("month") or datetime.now().month
        year = tracker.get_slot("Année") or 2023  # Assurez-vous que le nom du slot est correct
        
        # Mapping des noms de mois français aux numéros de mois
        month_map = {
            "janvier": 1,
            "fevrier": 2,
            "mars": 3,
            "avril": 4,
            "mai": 5,
            "juin": 6,
            "juillet": 7,
            "aout": 8,
            "septembre": 9,
            "octobre": 10,
            "novembre": 11,
            "decembre": 12
        }
        
        # Vérifier si le mois spécifié est en français et le mapper au numéro de mois correspondant
        if isinstance(month, str):
            month = month_map.get(month.lower(), month)
        
        # Convertir le mois en entier
        month = int(month)
        
        # Convertir l'année en entier
        year = int(year)
        
        # Connexion à la base de données (assurez-vous que "conn" est correctement défini)
        conn = se_connecter_a_ssms() 
        
        # Obtenir le nombre de jours dans le mois spécifié pour la requête
        num_days = calendar.monthrange(year, month)[1]
        
        # Requête SQL pour obtenir tous les montants correspondant à l'état Validé pour le mois et l'année spécifiés
        query = f"""SELECT Fournisseur.Fournisseur , Facture.Facture , Date.Date , SUM(f.Montant) AS MontantTotal
                    FROM dbo.fait f 
                    JOIN dbo.[Dimension fournisseur] fournisseur ON f.FK_Fournisseur = fournisseur.Pk_fournisseur
                    JOIN dbo.[Dimensions facture] facture ON f.FK_facture = facture.PK_facture
                    JOIN dbo.[Dimension_dates] date ON f.FK_Date = Date.DateKey 
                    WHERE facture.etat = 'créé' AND MONTH(Date.Date) = {month} AND YEAR(Date.Date) = {year}
                    GROUP BY Fournisseur.Fournisseur, Facture.Facture, Date.Date"""
        
        results = executer_requete(conn, query)  # Vous devez implémenter cette fonction

        if results:
            total_amount = 0
            for result in results:
                # Récupérer les détails de chaque facture
                fournisseur, facture, date, montant_total = result
                total_amount += montant_total
                date_str = date.strftime("%Y-%m-%d")
                dispatcher.utter_message(
                    text=f"Le fournisseur {fournisseur} a une facture {facture} avec une etat créé datée du {date_str}."
                )
            dispatcher.utter_message(
                text=f"Le montant total des factures créé pour le mois {calendar.month_name[month]} {year} est de {total_amount}."
            )
        else:
            # Aucun montant trouvé pour l'état Validé ce mois-ci
            dispatcher.utter_message(text=f"Aucun montant trouvé pour l'état 'créé' pour le mois {calendar.month_name[month]} {year}.")

        return [SlotSet(slot, None) for slot in ["start_date", "end_date", "Etat", "type", "Montant", "Date", "Fournisseur", "Facture", "top", "Jour", "JourD", "JourF", "month", "monthD", "monthF", "Année", "AnnéeD", "AnnéeF", "session_started_metadata"]]

#---------------------------------------------pret pour paiement------------------------------------------------------
from datetime import datetime
import calendar

class ActionAfficherMontantsEtatPrêtPourPaiementDate(Action):
    def name(self) -> Text:
        return "action_afficher_montants_etat_Prêt_pour_paiement_Date"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Récupérer le mois et l'année spécifiés, avec des valeurs par défaut si non spécifiés
        month = tracker.get_slot("month") or datetime.now().month
        year = tracker.get_slot("Année") or 2023  # Assurez-vous que le nom du slot est correct
        
        # Mapping des noms de mois français aux numéros de mois
        month_map = {
            "janvier": 1,
            "fevrier": 2,
            "mars": 3,
            "avril": 4,
            "mai": 5,
            "juin": 6,
            "juillet": 7,
            "aout": 8,
            "septembre": 9,
            "octobre": 10,
            "novembre": 11,
            "decembre": 12
        }
        
        # Vérifier si le mois spécifié est en français et le mapper au numéro de mois correspondant
        if isinstance(month, str):
            month = month_map.get(month.lower(), month)
        
        # Convertir le mois en entier
        month = int(month)
        
        # Convertir l'année en entier
        year = int(year)
        
        # Connexion à la base de données (assurez-vous que "conn" est correctement défini)
        conn = se_connecter_a_ssms() 
        
        # Obtenir le nombre de jours dans le mois spécifié pour la requête
        num_days = calendar.monthrange(year, month)[1]
        
        # Requête SQL pour obtenir tous les montants correspondant à l'état Validé pour le mois et l'année spécifiés
        query = f"""SELECT Fournisseur.Fournisseur , Facture.Facture , Date.Date , SUM(f.Montant) AS MontantTotal
                    FROM dbo.fait f 
                    JOIN dbo.[Dimension fournisseur] fournisseur ON f.FK_Fournisseur = fournisseur.Pk_fournisseur
                    JOIN dbo.[Dimensions facture] facture ON f.FK_facture = facture.PK_facture
                    JOIN dbo.[Dimension_dates] date ON f.FK_Date = Date.DateKey 
                    WHERE facture.etat = 'Prét pour paiement' AND MONTH(Date.Date) = {month} AND YEAR(Date.Date) = {year}
                    GROUP BY Fournisseur.Fournisseur, Facture.Facture, Date.Date"""
        
        results = executer_requete(conn, query)  # Vous devez implémenter cette fonction

        if results:
            total_amount = 0
            for result in results:
                # Récupérer les détails de chaque facture
                fournisseur, facture, date, montant_total = result
                total_amount += montant_total
                date_str = date.strftime("%Y-%m-%d")
                dispatcher.utter_message(
                    text=f"Le fournisseur {fournisseur} a une facture {facture} avec une etat Prêt pour paiement datée du {date_str}."
                )
            dispatcher.utter_message(
                text=f"Le montant total des factures Prêt pour paiement pour le mois {calendar.month_name[month]} {year} est de {total_amount}."
            )
        else:
            # Aucun montant trouvé pour l'état Validé ce mois-ci
            dispatcher.utter_message(text=f"Aucun montant trouvé pour l'état 'Prêt pour paiement' pour le mois {calendar.month_name[month]} {year}.")

        return [SlotSet(slot, None) for slot in ["start_date", "end_date", "Etat", "type", "Montant", "Date", "Fournisseur", "Facture", "top", "Jour", "JourD", "JourF", "month", "monthD", "monthF", "Année", "AnnéeD", "AnnéeF", "session_started_metadata"]]


#----------------------------------------------------------------------------------------------------
 
class ActionGetFactureJusquauMois(Action):
    def name(self) -> Text:
        return "action_get_Facture_Jusquau_Mois"

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
        year_entity = tracker.get_slot('Année')

        if month_entity:
            preprocessed_month = self.preprocess_month(month_entity)
            month_num = month_map.get(preprocessed_month)
            if month_num:
                if year_entity:
                    conn = se_connecter_a_ssms()        
                    cursor = conn.cursor()
                    cursor.execute("SELECT SUM(f.montant) FROM dbo.fait f JOIN dbo.[Dimension_dates] date ON f.FK_Date = date.DateKey WHERE YEAR(date.date) = ? AND MONTH(date.date) <= ? ", (year_entity, month_num,))
                    total_montant = cursor.fetchone()[0]

                    if total_montant:
                        dispatcher.utter_message(f"Le montant total des factures jusqu'au mois de {month_entity} de l'année {year_entity} est {total_montant}.")
                    else:
                        dispatcher.utter_message(f"Aucune donnée disponible jusqu'au mois de {month_entity} de l'année {year_entity}.")
                    return [SlotSet(slot, None) for slot in ["start_date", "end_date", "Etat", "type", "Montant", "Date", "Fournisseur", "Facture", "top", "Jour", "JourD", "JourF", "month", "monthD", "monthF", "Année", "AnnéeD", "AnnéeF", "session_started_metadata"]]
                else: 
                    conn = se_connecter_a_ssms()        
                    cursor = conn.cursor()
                    cursor.execute("SELECT SUM(f.montant) FROM dbo.fait f JOIN dbo.[Dimension_dates] date ON f.FK_Date = date.DateKey WHERE MONTH(date.date) <= ?", (month_num,))
                    total_montant = cursor.fetchone()[0]

                    if total_montant:
                        dispatcher.utter_message(f"Le montant total des factures jusqu'au mois de {month_entity} est {total_montant}.")
                    else:
                        dispatcher.utter_message(f"Aucune donnée disponible jusqu'au mois de {month_entity}.")
                    return [SlotSet(slot, None) for slot in ["start_date", "end_date", "Etat", "type", "Montant", "Date", "Fournisseur", "Facture", "top", "Jour", "JourD", "JourF", "month", "monthD", "monthF", "Année", "AnnéeD", "AnnéeF", "session_started_metadata"]]
            else:
                dispatcher.utter_message("Mois invalide.")
        else:
            dispatcher.utter_message("Je n'ai pas compris le mois.")

        return [SlotSet(slot, None) for slot in ["start_date", "end_date", "Etat", "type", "Montant", "Date", "Fournisseur", "Facture", "top", "Jour", "JourD", "JourF", "month", "monthD", "monthF", "Année", "AnnéeD", "AnnéeF", "session_started_metadata"]]

#---------------------------------------------------------------------------------------------------------------------------------

class ActionGetFactureDeuxMoisDeuxAnnee(Action):  
    def name(self) -> Text:
        return "action_get_Facture_deux_mois_deux_annee"

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

        month_entity1 = tracker.get_slot('monthD')
        month_entity2 = tracker.get_slot('monthF')
        year_entity1 = tracker.get_slot('AnnéeD')
        year_entity2 = tracker.get_slot('AnnéeF')

        print("monthD ",month_entity1, "yearD ",year_entity1 )
        print("monthF" ,month_entity2 ,"yearF ",year_entity2 )
        
        if month_entity1 and month_entity2 and year_entity1 and year_entity2:
            preprocessed_month1 = self.preprocess_month(month_entity1)
            preprocessed_month2 = self.preprocess_month(month_entity2)
            month_num1 = month_map.get(preprocessed_month1)
            month_num2 = month_map.get(preprocessed_month2)

            if month_num1 and month_num2:
                # Conversion des dates en objets datetime
                date1 = datetime(int(year_entity1), int(month_num1), 1)
                date2 = datetime(int(year_entity2), int(month_num2), 1)
                
                if date1 <= date2:
                    start_date, end_date = date1, date2
                else:
                    start_date, end_date = date2, date1

                conn = se_connecter_a_ssms()        
                cursor = conn.cursor()
                cursor.execute("SELECT SUM(f.montant) FROM dbo.fait f JOIN dbo.[Dimension_dates] date ON f.FK_Date = date.DateKey WHERE date.FullDate BETWEEN ? AND ?", (start_date, end_date,))
                total_montant = cursor.fetchone()[0]

                if total_montant:
                    dispatcher.utter_message(f"Le montant total des factures entre {month_entity1} {year_entity1} et {month_entity2} {year_entity2} est {total_montant}.")
                else:
                    dispatcher.utter_message(f"Aucune donnée disponible pour la période entre {month_entity1} {year_entity1} et {month_entity2} {year_entity2}.")
            else:
                dispatcher.utter_message("Mois invalide.")
        else:
            dispatcher.utter_message("Je n'ai pas compris les mois ou les années.")

        return [SlotSet(slot, None) for slot in ["Etat", "type", "Montant", "Date", "Fournisseur", "Facture", "top", "Jour", "JourD", "JourF", "month", "monthD", "monthF", "Année", "AnnéeD", "AnnéeF", "session_started_metadata"]]

#---------------------------------------------fonctionne pas-----------------------------------------------------

import pyodbc
from typing import Optional

class ActionMontantEntreDates(Action):
    def name(self) -> Text:
        return "action_montant_entre_dates"

    def preprocess_month(self, month: Text) -> Text:
        """
        Preprocesses the month entity to remove accents and circumflexes.
        """
        replacements = {'é': 'e', 'ê': 'e', 'û': 'u', 'ô': 'o', 'î': 'i', 'è': 'e'}
        return ''.join(replacements.get(c, c) for c in month.lower())

    def extract_date(self, tracker: Tracker, prefix: str) -> Optional[str]:
        day = tracker.get_slot(f'{prefix}Jour')
        month = tracker.get_slot(f'{prefix}month')
        year = tracker.get_slot(f'{prefix}Année')
        if day and month and year:
            return f"{year}-{self.preprocess_month(month)}-{day}"
        return None

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        start_date = self.extract_date(tracker, "D")
        end_date = self.extract_date(tracker, "F")

        if not (start_date and end_date):
            dispatcher.utter_message("Veuillez préciser correctement les dates.")
            return [SlotSet(slot, None) for slot in ["start_date", "end_date"]]
        
        conn = pyodbc.connect('DRIVER={SQL Server};SERVER=your_server;DATABASE=your_database;UID=username;PWD=password') # Remplacer les valeurs par les vôtres
        cursor = conn.cursor()

        cursor.execute("SELECT SUM(f.montant) FROM dbo.fait f JOIN dbo.[Dimension_dates] date ON f.FK_Date = date.DateKey WHERE date BETWEEN ? AND ?", (start_date, end_date,))
        total_montant = cursor.fetchone()[0]

        if total_montant:
            dispatcher.utter_message(f"Le montant total des factures entre {start_date} et {end_date} est {total_montant}.")
        else:
            dispatcher.utter_message(f"Aucune donnée disponible entre {start_date} et {end_date}.")

        cursor.close()
        conn.close()

        return [SlotSet(slot, None) for slot in ["start_date", "end_date"]]


