from datetime import datetime
import re
import unicodedata
import calendar
from rasa_sdk.events import UserUtteranceReverted, FollowupAction
from typing import Type, Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from langchain_community.llms import GPT4All
from rasa_sdk import Action, Tracker
import pyodbc
from huggingface_hub import InferenceClient

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


class ActionSayHello(Action):
    def name(self) -> Text:
        return "action_salutation"
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        user_input = tracker.latest_message.get("text")
        try:
            # Charger le modèle avec les paramètres personnalisés
            llm = InferenceClient(model = 'mistralai/Mistral-7B-Instruct-v0.2', token = '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')
            # Appeler la méthode invoke avec le prompt et le contexte système
            prompt = "<s> [INST] You are a friendly chatbot and a financial advisor who answers to user greetings. At every greeting say your name and say that you are a financial advisor "
            prompt += """Your name is InvoiceBot and you are designed to provide polite responses in French, answer to this text: """
            prompt += user_input +" [/INST]"
            
            # Call the model with the prompt and extract the answer
            result = llm.text_generation(prompt,max_new_tokens=1000,temperature=0.7,top_p=0.7,top_k=50,)
            print(result)
            answer_start=0
            # if (response.find("Output: ")!=0):
            #     answer_start = response.find("Output: ") + 7
            # elif(response.find("Réponse: ")!=0):
            #     answer_start = response.find("Réponse: ") + 8
            answer_end = len(result) - 1
            answer = result[answer_start:answer_end].strip()
            # Display the answer
            dispatcher.utter_message(text=answer)
        except Exception as e:
            # Gérer les exceptions et afficher un message approprié
            print("Une erreur s'est produite:", e)

        return []


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
        
        return [SlotSet(slot, None) for slot in ["start_date", "end_date", "Etat", "type", "Montant", "Date", "Fournisseur", "Facture", "top", "Jour", "JourD", "JourF", "month", "monthD", "monthF", "Annee", "AnneeD", "AnneeF", "session_started_metadata"]]


# -----------------------------------------------------------------------------------------------------------------   
class ActionObtenirMontantInf(Action):
    def name(self) -> Text:
        return "action_obtenir_montant_inf"
    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        user_input = tracker.latest_message.get("text")
        # # Initialisation de la facture détectée et de sa longueur
        for f in factures:
            if f.lower() in user_input.lower():
                    return [UserUtteranceReverted(), FollowupAction("action_obtenir_Facture_montant")]
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

        return [SlotSet(slot, None) for slot in ["start_date", "end_date", "Etat", "type", "Montant", "Date", "Fournisseur", "Facture", "top", "Jour", "JourD", "JourF", "month", "monthD", "monthF", "Annee", "AnneeD", "AnneeF", "session_started_metadata"]]


 
# ------------------------------------------------------------------------------------------------------------------

class ActionObtenirMontantSup(Action):
    def name(self) -> Text:
        return "action_obtenir_montant_sup"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        user_input = tracker.latest_message.get("text")
        for f in factures:
            if f.lower() in user_input.lower():
                    return [UserUtteranceReverted(), FollowupAction("action_obtenir_Facture_montant")]
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
        
        return [SlotSet(slot, None) for slot in ["start_date", "end_date", "Etat", "type", "Montant", "Date", "Fournisseur", "Facture", "top", "Jour", "JourD", "JourF", "month", "monthD", "monthF", "Annee", "AnneeD", "AnneeF", "session_started_metadata"]]


# ------------------------------------------------------------------------------------------------------------------

class ActionObtenirMontantegal(Action):
    def name(self) -> Text:
        return "action_obtenir_montant_egal"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        user_input = tracker.latest_message.get("text")
        for f in factures:
            if f.lower() in user_input.lower():
                    return [UserUtteranceReverted(), FollowupAction("action_obtenir_Facture_montant")]
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
        
        return [SlotSet(slot, None) for slot in ["start_date", "end_date", "Etat", "type", "Montant", "Date", "Fournisseur", "Facture", "top", "Jour", "JourD", "JourF", "month", "monthD", "monthF", "Annee", "AnneeD", "AnneeF", "session_started_metadata"]]

    
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
                    montant_formatte = "{:,.2f}".format(montant_total)  # Formatage du montant
                    dispatcher.utter_message(
                        text=f"Le fournisseur {fournisseur} doit un montant total de {montant_formatte}."
                    )
                    montants_fournisseurs.append(montant_total)

                somme_total_montants = sum(montants_fournisseurs)
                somme_total_formattee = "{:,.2f}".format(somme_total_montants)  # Formatage de la somme totale
                dispatcher.utter_message(
                    text=f"La somme totale des montants dus par les fournisseurs est {somme_total_formattee}."
                )
                
            else:
                dispatcher.utter_message(text="Désolé, je n'ai pas pu trouver les informations sur les montants dus par fournisseur.")
        else:
            dispatcher.utter_message(text="Désolé, je n'ai pas pu me connecter à la base de données.")

        return [SlotSet(slot, None) for slot in ["start_date", "end_date", "Etat", "type", "Montant", "Date", "Fournisseur", "Facture", "top", "Jour", "JourD", "JourF", "month", "monthD", "monthF", "Annee", "AnneeD", "AnneeF", "session_started_metadata"]]


# -----------------------------------------------------------------------------------------------------------------


# class ActionObtenirMontantDate(Action):
#     def name(self) -> Text:
#         return "action_obtenir_montant_Date"

#     def normalize_date(self, date_str):
#         # Essayer de convertir la date en YYYY-MM-DD
#         try:
#             date_obj = datetime.strptime(date_str, '%Y-%m-%d')
#             return date_obj.strftime('%Y-%m-%d')
#         except ValueError:
#             pass
        
#         # Essayer de convertir la date en DD-MM-YYYY
#         try:
#             date_obj = datetime.strptime(date_str, '%d-%m-%Y')
#             return date_obj.strftime('%Y-%m-%d')
#         except ValueError:
#             pass
                
#         # Si aucun format ne correspond, retourner None
#         return None

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
#         # Obtenir la date de la requête de l'utilisateur
#         date_str = tracker.get_slot('Date')
        
#         # Normaliser la date au format YYYY-MM-DD
#         normalized_date = self.normalize_date(date_str)
        
#         if normalized_date is None:
#             dispatcher.utter_message(text="Format de date non valide. Veuillez entrer une date au format YYYY-MM-DD, DD-MM-YYYY ou DD MM YYYY.")
#             return []
        
#         # Requête SQL pour obtenir tous les montants correspondant à la date
#         cursor = conn.cursor()
#         cursor.execute("SELECT DISTINCT f.montant FROM dbo.fait f JOIN dbo.[Dimension_dates] date ON f.FK_Date = Date.DateKey  WHERE date.date = ?", (normalized_date,))
#         rows = cursor.fetchall()
        
#         if rows:
#             amounts = [row[0] for row in rows]
#             amount_str = ", ".join(str(amount) for amount in amounts)
#             dispatcher.utter_message(text=f"Les montants pour la date {normalized_date} sont : {amount_str} TND.")
#         else:
#             dispatcher.utter_message(text=f"Aucun montant trouvé pour la date {normalized_date}.")
        
#         return [SlotSet(slot, None) for slot in ["start_date", "end_date", "Etat", "type", "Montant", "Date", "Fournisseur", "Facture", "top", "Jour", "JourD", "JourF", "month", "monthD", "monthF", "Annee", "AnneeD", "AnneeF", "session_started_metadata"]]


# -----------------------------------------------------------------------------------------------------------------


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
                    etat = row[0]
                    montant_total = row[1]
                    montant_formatte = "{:,.2f}".format(montant_total)  # Formatage du montant
                    dispatcher.utter_message(
                        text=f"L'Etat {etat} doit un montant total de {montant_formatte}."
                    )
            else:
                dispatcher.utter_message(text="Désolé, je n'ai pas pu trouver les informations sur les montants dus par etat.")
        else:
            dispatcher.utter_message(text="Désolé, je n'ai pas pu me connecter à la base de données.")

        return [SlotSet(slot, None) for slot in ["start_date", "end_date", "Etat", "type", "Montant", "Date", "Fournisseur", "Facture", "top", "Jour", "JourD", "JourF", "month", "monthD", "monthF", "Annee", "AnneeD", "AnneeF", "session_started_metadata"]]


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
                montant_formatte = "{:,.2f}".format(montant)  # Formatage du montant
                dispatcher.utter_message(
                        text=f"Le fournisseur {fournisseur} a une facture {facture} d'un montant de {montant_formatte} avec un état {etat}."
                    )
                total_montant += montant  # Ajoute le montant au total

            # Formatage du montant total
            total_montant_formatte = "{:,.2f}".format(total_montant)
            # Affiche le montant total à la fin
            dispatcher.utter_message(text=f"Le montant total des factures validées est de : {total_montant_formatte}.")
        else:
            # Aucun montant trouvé pour l'état Validé
            dispatcher.utter_message(text=f"Aucun montant trouvé pour l'état 'Validé'.")

        return [SlotSet(slot, None) for slot in ["start_date", "end_date", "Etat", "type", "Montant", "Date", "Fournisseur", "Facture", "top", "Jour", "JourD", "JourF", "month", "monthD", "monthF", "Annee", "AnneeD", "AnneeF", "session_started_metadata"]]

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
                montant_formatte = "{:,.2f}".format(montant)  # Formatage du montant
                dispatcher.utter_message(
                        text=f"Le fournisseur {fournisseur} a une facture {facture} d'un montant de {montant_formatte} avec un état {etat}."
                    )
                total_montant += montant  # Ajoute le montant au total

            # Formatage du montant total
            total_montant_formatte = "{:,.2f}".format(total_montant)
            # Affiche le montant total à la fin
            dispatcher.utter_message(text=f"Le montant total des factures créées est de : {total_montant_formatte}.")
        else:
            # Aucun montant trouvé pour l'état Créé
            dispatcher.utter_message(text=f"Aucun montant trouvé pour l'état 'Créé'.")

        return [SlotSet(slot, None) for slot in ["start_date", "end_date", "Etat", "type", "Montant", "Date", "Fournisseur", "Facture", "top", "Jour", "JourD", "JourF", "month", "monthD", "monthF", "Annee", "AnneeD", "AnneeF", "session_started_metadata"]]

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
                montant_formatte = "{:,.2f}".format(montant)  # Formatage du montant
                dispatcher.utter_message(
                        text=f"Le fournisseur {fournisseur} a une facture {facture} d'un montant de {montant_formatte} avec un état {etat}."
                    )
                total_montant += montant  # Ajoute le montant au total

            # Formatage du montant total
            total_montant_formatte = "{:,.2f}".format(total_montant)
            # Affiche le montant total à la fin
            dispatcher.utter_message(text=f"Le montant total des factures prêtes pour paiement est de : {total_montant_formatte}.")
        else:
            # Aucun montant trouvé pour l'état Prêt pour paiement
            dispatcher.utter_message(text=f"Aucun montant trouvé pour l'état 'Prêt pour paiement'.")

        return [SlotSet(slot, None) for slot in ["start_date", "end_date", "Etat", "type", "Montant", "Date", "Fournisseur", "Facture", "top", "Jour", "JourD", "JourF", "month", "monthD", "monthF", "Annee", "AnneeD", "AnneeF", "session_started_metadata"]]

# -----------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------



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
                    montant_formatte = "{:,.2f}".format(montant_total)  # Formatage du montant
                    total_general += montant_total  # Ajouter le montant total de chaque type au total général
                    dispatcher.utter_message(
                        text=f"Type: {type} -> Montant total: {montant_formatte}."
                    )
                # Formatage du montant total général
                total_general_formatte = "{:,.2f}".format(total_general)
                # Afficher le montant total général
                dispatcher.utter_message(
                    text=f"Montant total de tous les types: {total_general_formatte}."
                )
            else:
                dispatcher.utter_message(text="Désolé, je n'ai pas pu trouver les informations sur les montants dus par type.")
        else:
            dispatcher.utter_message(text="Désolé, je n'ai pas pu me connecter à la base de données.")

        return [SlotSet(slot, None) for slot in ["start_date", "end_date", "Etat", "type", "Montant", "Date", "Fournisseur", "Facture", "top", "Jour", "JourD", "JourF", "month", "monthD", "monthF", "Annee", "AnneeD", "AnneeF", "session_started_metadata"]]

# -----------------------------------------------------------------------------------------------------------------
class ActionCountFournisseurParAnnee(Action):
    def name(self) -> Text:
        return "action_count_Fournisseur_par_annee"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        try:
            # Récupérer l'année spécifiée par l'utilisateur
            year_entity = tracker.get_slot("Annee")

            if year_entity:
                # Exécuter la requête pour compter les fournisseurs pour l'année spécifiée
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(DISTINCT Fournisseur) FROM dbo.fait f JOIN dbo.[Dimension_dates] date ON f.FK_Date = Date.DateKey JOIN dbo.[Dimension Fournisseur] fournisseur ON f.FK_Fournisseur = fournisseur.PK_Fournisseur WHERE YEAR(date.date) = ?", (year_entity,))
                count = cursor.fetchone()[0]  # Obtenir le nombre de fournisseurs pour l'année spécifiée

                # Envoyer la réponse avec le nombre de fournisseurs pour l'année spécifiée
                dispatcher.utter_message(text=f"Nombre de fournisseurs pour l'année {year_entity} : {count}")
            else:
                # Exécuter la requête pour compter le nombre total de fournisseurs par année
                cursor = conn.cursor()
                cursor.execute("SELECT YEAR(date.date), COUNT(DISTINCT Fournisseur) FROM dbo.fait f JOIN dbo.[Dimension_dates] date ON f.FK_Date = Date.DateKey JOIN dbo.[Dimension Fournisseur] fournisseur ON f.FK_Fournisseur = fournisseur.PK_Fournisseur GROUP BY YEAR(date.date)")
                counts_by_year = cursor.fetchall()  # Obtenir le nombre total de fournisseurs par année

                # Formatage de la réponse avec les résultats pour chaque année
                response_text = "Nombre de fournisseurs par année :\n"
                for year, count in counts_by_year:
                    response_text += f"{year} : {count}\n"

                # Envoyer la réponse avec le texte formaté
                dispatcher.utter_message(text=response_text)

        except Exception as e:
            # En cas d'erreur, afficher un message d'erreur
            dispatcher.utter_message(text="Une erreur s'est produite lors de la connexion à la base de données.")

        return [SlotSet("Annee", None)]


# -----------------------------------------------------------------------------------------------------------------
class ActionCountFournisseurParMois(Action):
    def name(self) -> Text:
        return "action_count_Fournisseur_par_mois"

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

        # Récupérer l'input complet de l'utilisateur
        user_input = tracker.latest_message.get("text")

        try:
            # Vérifier si l'utilisateur a spécifié un mois
            specified_month = None
            for month, month_num in month_map.items():
                preprocessed_month = self.preprocess_month(month)
                if preprocessed_month in user_input:
                    specified_month = month
                    specified_month_num = month_num
                    break

            # Exécuter la requête SQL pour compter les fournisseurs pour le mois spécifié
            if specified_month:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(DISTINCT Fournisseur) FROM dbo.fait f JOIN dbo.[Dimension_dates] date ON f.FK_Date = Date.DateKey JOIN dbo.[Dimension Fournisseur] fournisseur ON f.FK_Fournisseur = fournisseur.PK_Fournisseur WHERE MONTH(date) = ?", (specified_month_num,))
                count_specified_month = cursor.fetchone()[0]  # Obtenir le nombre de fournisseurs distincts pour le mois spécifié

                # Envoyer la réponse avec le nombre de fournisseurs pour le mois spécifié
                response_text_specified_month = f"Nombre de fournisseurs distincts pour {specified_month.capitalize()} : {count_specified_month}"
                dispatcher.utter_message(text=response_text_specified_month)

            # Si aucun mois spécifié, compter les fournisseurs pour chaque mois
            else:
                # Initialiser un dictionnaire pour stocker les résultats par mois
                counts_by_month = {}

                # Boucle à travers tous les mois
                for month, month_num in month_map.items():
                    # Exécuter la requête SQL pour compter les fournisseurs pour chaque mois
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(DISTINCT Fournisseur) FROM dbo.fait f JOIN dbo.[Dimension_dates] date ON f.FK_Date = Date.DateKey JOIN dbo.[Dimension Fournisseur] fournisseur ON f.FK_Fournisseur = fournisseur.PK_Fournisseur WHERE MONTH(date) = ?", (month_num,))
                    count = cursor.fetchone()[0]  # Obtenir le nombre de fournisseurs distincts pour le mois donné
                    counts_by_month[month] = count

                # Formatage de la réponse avec les résultats pour chaque mois
                response_text_by_month = "Nombre de fournisseurs distincts par mois :\n"
                for month, count in counts_by_month.items():
                    response_text_by_month += f"{month.capitalize()} : {count}\n"

                # Envoyer la réponse avec le texte formaté pour chaque mois
                dispatcher.utter_message(text=response_text_by_month)

        except Exception as e:
            # En cas d'erreur, affichez un message d'erreur
            dispatcher.utter_message(text="Une erreur s'est produite lors de la connexion à la base de données.")

        return [SlotSet(slot, None) for slot in ["start_date", "end_date", "Etat", "type", "Montant", "Date", "Fournisseur", "Facture", "top", "Jour", "JourD", "JourF", "month", "monthD", "monthF", "Annee", "AnneeD", "AnneeF", "session_started_metadata"]]


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

        return [SlotSet(slot, None) for slot in ["start_date", "end_date", "Etat", "type", "Montant", "Date", "Fournisseur", "Facture", "top", "Jour", "JourD", "JourF", "month", "monthD", "monthF", "Annee", "AnneeD", "AnneeF", "session_started_metadata"]]
    

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

        return [SlotSet(slot, None) for slot in ["start_date", "end_date", "Etat", "type", "Montant", "Date", "Fournisseur", "Facture", "top", "Jour", "JourD", "JourF", "month", "monthD", "monthF", "Annee", "AnneeD", "AnneeF", "session_started_metadata"]]
    
# -----------------------------------------------------------------------------------------------------------------

# class ActionRecupererMontantParDate(Action):
#     def name(self):
#         return "action_Recuperer_Montant_Par_Date"

#     def run(self, dispatcher, tracker, domain):
#         # Extraire les slots de date du tracker
#         start_date = tracker.get_slot("start_date")
#         end_date = tracker.get_slot("end_date")

#         # Se connecter à la base de données
#         conn = se_connecter_a_ssms()

#         # Exécuter la requête SQL pour récupérer les montants à payer
#         cursor = conn.cursor()
#         query = f"""SELECT DISTINCT f.montant 
#                     FROM dbo.fait f 
#                     JOIN dbo.[Dimension_dates] date ON f.FK_Date = Date.DateKey                 
#                     WHERE date.date BETWEEN ? AND ?"""
#         cursor.execute(query, (start_date, end_date))
#         rows = cursor.fetchall()

#         # Rassembler les montants récupérés
#         montants = [row[0] for row in rows]
#         # Envoyer les montants récupérés au dispatcher
#         dispatcher.utter_message(f"Les montants à payer sont : {', '.join(map(str, montants))} ")

#         return [SlotSet(slot, None) for slot in ["start_date", "end_date", "Etat", "type", "Montant", "Date", "Fournisseur", "Facture", "top", "Jour", "JourD", "JourF", "month", "monthD", "monthF", "Annee", "AnneeD", "AnneeF", "session_started_metadata"]]

    # -------------------------------------------------------------------------------------------

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

        return [SlotSet(slot, None) for slot in ["start_date", "end_date", "Etat", "type", "Montant", "Date", "Fournisseur", "Facture", "top", "Jour", "JourD", "JourF", "month", "monthD", "monthF", "Annee", "AnneeD", "AnneeF", "session_started_metadata"]]


# -------------------------------------------------------------------------------------------


class ActionCountFactureParMois(Action):
    def name(self) -> Text:
        return "action_count_Facture_par_mois"

    def preprocess_month(self, month: Text) -> Text:
        """
        Preprocesses the month entity to match the format in the database.
        """
        month_map = {
            "janvier": "01",
            "février": "02",
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
        preprocessed_month = month.lower()
        preprocessed_month = preprocessed_month.replace('é', 'e').replace('ê', 'e').replace('û', 'u').replace('û', 'u').replace('ô', 'o').replace('î', 'i').replace('è', 'e')
        return month_map.get(preprocessed_month, None)

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        try:
            # Récupérer le mois spécifié par l'utilisateur
            month_entity = tracker.get_slot("month")

            if month_entity:
                # Prétraiter le mois pour correspondre au format dans la base de données
                month_num = self.preprocess_month(month_entity)

                if month_num:
                    # Exécuter la requête pour compter les factures pour le mois spécifié
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(Facture) FROM dbo.fait f JOIN dbo.[Dimension_dates] date ON f.FK_Date = Date.DateKey JOIN dbo.[Dimensions facture] facture ON f.FK_facture = facture.PK_facture WHERE MONTH(date) = ?", (month_num,))
                    count = cursor.fetchone()[0]  # Obtenir le nombre de factures pour le mois spécifié

                    # Envoyer la réponse avec le nombre de factures pour le mois spécifié
                    dispatcher.utter_message(text=f"Nombre de factures pour {month_entity.capitalize()} : {count}")
                else:
                    dispatcher.utter_message(text="Mois non valide.")

            else:
                # Initialise un dictionnaire pour stocker les résultats par mois
                counts_by_month = {}

                # Liste des mois
                mois_list = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "aout", "septembre", "octobre", "novembre", "decembre"]

                # Boucle à travers tous les mois
                for month in mois_list:
                    month_num = self.preprocess_month(month)

                    # Exécuter la requête pour compter les Facture pour le mois donné
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(Facture) FROM dbo.fait f JOIN dbo.[Dimension_dates] date ON f.FK_Date = Date.DateKey JOIN dbo.[Dimensions facture] facture ON f.FK_facture = facture.PK_facture WHERE MONTH(date) = ?", (month_num,))
                    count = cursor.fetchone()[0]  # Obtenir le nombre de facture pour le mois donné

                    # Stockez le résultat dans le dictionnaire
                    counts_by_month[month] = count

                # Envoyez la réponse avec les résultats pour chaque mois
                response_text = "Nombre de factures par mois :\n"
                for month, count in counts_by_month.items():
                    response_text += f"{month.capitalize()} : {count}\n"

                dispatcher.utter_message(text=response_text)

        except Exception as e:
            # En cas d'erreur, affichez un message d'erreur
            dispatcher.utter_message(text="Une erreur s'est produite lors de la connexion à la base de données.")

        return [SlotSet("month", None)]
# -------------------------------------------------------------------------------------------

class ActionCountFactureParAnnee(Action):
    def name(self) -> Text:
        return "action_count_Facture_par_annee"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        try:
            # Récupérer l'année spécifiée par l'utilisateur
            year_entity = tracker.get_slot("Annee")

            if year_entity:
                # Exécuter la requête pour compter les factures pour l'année spécifiée
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(Facture) FROM dbo.fait f JOIN dbo.[Dimension_dates] date ON f.FK_Date = Date.DateKey JOIN dbo.[Dimensions facture] facture ON f.FK_facture = facture.PK_facture WHERE YEAR(date.date) = ?", (year_entity,))
                count = cursor.fetchone()[0]  # Obtenir le nombre de factures pour l'année spécifiée

                # Envoyer la réponse avec le nombre de factures pour l'année spécifiée
                dispatcher.utter_message(text=f"Nombre de factures pour l'année {year_entity} : {count}")
            else:
                # Exécuter la requête pour compter le nombre total de factures par année
                cursor = conn.cursor()
                cursor.execute("SELECT YEAR(date.date), COUNT(Facture) FROM dbo.fait f JOIN dbo.[Dimension_dates] date ON f.FK_Date = Date.DateKey JOIN dbo.[Dimensions facture] facture ON f.FK_facture = facture.PK_facture GROUP BY YEAR(date.date)")
                counts_by_year = cursor.fetchall()  # Obtenir le nombre total de factures par année

                # Formatage de la réponse avec les résultats pour chaque année
                response_text = "Nombre de factures par année :\n"
                for year, count in counts_by_year:
                    response_text += f"{year} : {count}\n"

                # Envoyer la réponse avec le texte formaté
                dispatcher.utter_message(text=response_text)

        except Exception as e:
            # En cas d'erreur, afficher un message d'erreur
            dispatcher.utter_message(text="Une erreur s'est produite lors de la connexion à la base de données.")

        return [SlotSet("Annee", None)]

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
                montant_formatte = "{:,.2f}".format(total_montant)  # Formatage du montant
                dispatcher.utter_message(
                    text=f"{idx}. {fournisseur} : {montant_formatte} "
                )
        else:
            dispatcher.utter_message(text="Aucun résultat trouvé pour les top fournisseurs.")

        return [SlotSet(slot, None) for slot in ["start_date", "end_date", "Etat", "type", "Montant", "Date", "Fournisseur", "Facture", "top", "Jour", "JourD", "JourF", "month", "monthD", "monthF", "Annee", "AnneeD", "AnneeF", "session_started_metadata"]]
    
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
                montant_formatte = "{:,.2f}".format(total_montant)  # Formatage du montant
                dispatcher.utter_message(
                    text=f"{idx}. {Type} : {montant_formatte} "
                )
        else:
            dispatcher.utter_message(text="Aucun résultat trouvé pour les top Type.")

        return [SlotSet(slot, None) for slot in ["start_date", "end_date", "Etat", "type", "Montant", "Date", "Fournisseur", "Facture", "top", "Jour", "JourD", "JourF", "month", "monthD", "monthF", "Annee", "AnneeD", "AnneeF", "session_started_metadata"]]

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
                montant_formatte = "{:,.2f}".format(total_montant)  # Formatage du montant
                dispatcher.utter_message(
                    text=f"{idx}. {fournisseur} : {montant_formatte} "
                )
        else:
            dispatcher.utter_message(text="Aucun résultat trouvé pour les top fournisseurs.")

        return [SlotSet(slot, None) for slot in ["start_date", "end_date", "Etat", "type", "Montant", "Date", "Fournisseur", "Facture", "top", "Jour", "JourD", "JourF", "month", "monthD", "monthF", "Annee", "AnneeD", "AnneeF", "session_started_metadata"]]

# -----------------------------------------------------------------------------
 
# class ActionFournisseursZero(Action):
#     def name(self):
#         return "action_fournisseurs_zero"

#     def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
#         try:
#             # Connexion à la base de données
#             conn = se_connecter_a_ssms()

#             # Exécuter la requête SQL pour récupérer les fournisseurs avec un montant de 0
#             query = f"""SELECT DISTINCT fournisseur.fournisseur 
#                         FROM dbo.Fait f 
#                         JOIN dbo.[Dimension Fournisseur] Fournisseur ON f.FK_Fournisseur = Fournisseur.Pk_Fournisseur
#                         WHERE montant = 0"""
#             results = executer_requete(conn, query)

#             # Si des résultats sont trouvés, les envoyer au chatbot
#             if results:
#                 fournisseurs = [row[0] for row in results]
#                 dispatcher.utter_message("Les fournisseurs qu'on a jamais travailler avec eux sont : {}".format(", ".join(fournisseurs)))
#             else:
#                 dispatcher.utter_message("Aucun fournisseur n'a été trouvé.")

#         except Exception as e:
#             dispatcher.utter_message("Une erreur s'est produite lors de la récupération des fournisseurs : {}".format(str(e)))

#         return [SlotSet(slot, None) for slot in ["start_date", "end_date", "Etat", "type", "Montant", "Date", "Fournisseur", "Facture", "top", "Jour", "JourD", "JourF", "month", "monthD", "monthF", "Annee", "AnneeD", "AnneeF", "session_started_metadata"]]
    
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
                    montant_formatte = "{:,.2f}".format(montant_total_facture)  # Formatage du montant
                    dispatcher.utter_message(
                        text=f"La facture {facture} pour le fournisseur {fournisseur} doit un montant total de {montant_formatte}."
                    )
                    montants_factures.append(montant_total_facture)

                somme_total_montants = sum(montants_factures)
                total_formatte = "{:,.2f}".format(somme_total_montants)  # Formatage du montant total
                dispatcher.utter_message(
                    text=f"Le montant total des factures est {total_formatte}."
                )
                
            else:
                dispatcher.utter_message(text="Désolé, je n'ai pas pu trouver les informations sur les montants dus par facture.")
        else:
            dispatcher.utter_message(text="Désolé, je n'ai pas pu me connecter à la base de données.")

        return [SlotSet(slot, None) for slot in ["start_date", "end_date", "Etat", "type", "Montant", "Date", "Fournisseur", "Facture", "top", "Jour", "JourD", "JourF", "month", "monthD", "monthF", "Annee", "AnneeD", "AnneeF", "session_started_metadata"]]



#---------------------------------------------------------------------------------------------
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
            # Récupérer les Annees spécifiées dans la phrase
            annees = set()  # Utilisation d'un ensemble pour éviter les doublons
            for entity in tracker.latest_message.get("entities"):
                if entity["entity"] == "Annee":
                    annees.add(entity["value"])

            if len(annees) >= 1:
                montant_total_pluriannuel = 0
                for annee in annees:
                    # Construire la requête SQL pour obtenir le montant total pour chaque Annee spécifiée
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
                        dispatcher.utter_message(text=f"Aucune facture trouvée pour l'Annee {annee}.")

                montant_total_pluriannuel_formatte = "{:,.2f}".format(montant_total_pluriannuel)  # Formatage du montant total
                dispatcher.utter_message(
                    text=f"Le montant total des factures pour les Annees {', '.join(annees)} est de {montant_total_pluriannuel_formatte}."
                )
            else:
                dispatcher.utter_message(text="Je n'ai pas compris pour quelles Annees vous voulez obtenir le montant total des factures.")
        else:
            dispatcher.utter_message(text="Erreur de connexion à la base de données.")

        return [SlotSet(slot, None) for slot in ["start_date", "end_date", "Etat", "type", "Montant", "Date", "Fournisseur", "Facture", "top", "Jour", "JourD", "JourF", "month", "monthD", "monthF", "Annee", "AnneeD", "AnneeF", "session_started_metadata"]]
#----------------------------------------------------------------------------------------------------


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

        # Correspondance de motifs pour les Annees
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

        # Recherche de l'Annee dans la phrase de l'utilisateur
        match = re.search(year_pattern, user_input)
        if not match:
            dispatcher.utter_message("Je n'ai détecté aucune Annee dans votre phrase.")
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

        # Formatage du montant total
        total_montant_formatte = "{:,.2f}".format(total_montant) if total_montant is not None else "0.00"

        # Réponse du chatbot
        dispatcher.utter_message(f"Le montant total des factures entre {start_month_name} et {end_month_name} pour l'Annee {year} est de {total_montant_formatte}.")

        return [SlotSet(slot, None) for slot in ["start_date", "end_date", "Etat", "type", "Montant", "Date", "Fournisseur", "Facture", "top", "Jour", "JourD", "JourF", "month", "monthD", "monthF", "Annee", "AnneeD", "AnneeF", "session_started_metadata"]]
#---------------------------------------------------------------------------------------------------------------------------------------------------
  
#---------------------------------------------------------------------------------------------------------------------------------------------------


class ActionAfficherMontantsEtatValideesDate(Action):
    def name(self) -> Text:
        return "action_afficher_montants_etat_validees_Date"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Récupérer le mois et l'Annee spécifiés, avec des valeurs par défaut si non spécifiés
        month = tracker.get_slot("month") or datetime.now().month
        year = tracker.get_slot("Annee") or 2023  # Assurez-vous que le nom du slot est correct
        
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
        
        # Convertir l'Annee en entier
        year = int(year)
        
        # Connexion à la base de données (assurez-vous que "conn" est correctement défini)
        conn = se_connecter_a_ssms() 
        
        # Obtenir le nombre de jours dans le mois spécifié pour la requête
        num_days = calendar.monthrange(year, month)[1]
        
        # Requête SQL pour obtenir tous les montants correspondant à l'état Validé pour le mois et l'Annee spécifiés
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

        return [SlotSet(slot, None) for slot in ["start_date", "end_date", "Etat", "type", "Montant", "Date", "Fournisseur", "Facture", "top", "Jour", "JourD", "JourF", "month", "monthD", "monthF", "Annee", "AnneeD", "AnneeF", "session_started_metadata"]]


#----------------------------------------créé-------------------------------------------


class ActionAfficherMontantsEtatCrééDate(Action):
    def name(self) -> Text:
        return "action_afficher_montants_etat_cree_Date"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Récupérer le mois et l'Annee spécifiés, avec des valeurs par défaut si non spécifiés
        month = tracker.get_slot("month") or datetime.now().month
        year = tracker.get_slot("Annee") or 2023  # Assurez-vous que le nom du slot est correct
        
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
        
        # Convertir l'Annee en entier
        year = int(year)
        
        # Connexion à la base de données (assurez-vous que "conn" est correctement défini)
        conn = se_connecter_a_ssms() 
        
        # Obtenir le nombre de jours dans le mois spécifié pour la requête
        num_days = calendar.monthrange(year, month)[1]
        
        # Requête SQL pour obtenir tous les montants correspondant à l'état Validé pour le mois et l'Annee spécifiés
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

        return [SlotSet(slot, None) for slot in ["start_date", "end_date", "Etat", "type", "Montant", "Date", "Fournisseur", "Facture", "top", "Jour", "JourD", "JourF", "month", "monthD", "monthF", "Annee", "AnneeD", "AnneeF", "session_started_metadata"]]

#---------------------------------------------pret pour paiement------------------------------------------------------

class ActionAfficherMontantsEtatPrêtPourPaiementDate(Action):
    def name(self) -> Text:
        return "action_afficher_montants_etat_Prêt_pour_paiement_Date"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Récupérer le mois et l'Annee spécifiés, avec des valeurs par défaut si non spécifiés
        month = tracker.get_slot("month") or datetime.now().month
        year = tracker.get_slot("Annee") or 2023  # Assurez-vous que le nom du slot est correct
        
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
        
        # Convertir l'Annee en entier
        year = int(year)
        
        # Connexion à la base de données (assurez-vous que "conn" est correctement défini)
        conn = se_connecter_a_ssms() 
        
        # Obtenir le nombre de jours dans le mois spécifié pour la requête
        num_days = calendar.monthrange(year, month)[1]
        
        # Requête SQL pour obtenir tous les montants correspondant à l'état Validé pour le mois et l'Annee spécifiés
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

        return [SlotSet(slot, None) for slot in ["start_date", "end_date", "Etat", "type", "Montant", "Date", "Fournisseur", "Facture", "top", "Jour", "JourD", "JourF", "month", "monthD", "monthF", "Annee", "AnneeD", "AnneeF", "session_started_metadata"]]


#----------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------

class ActionGetFactureDeuxMoisDeuxAnnee(Action):  
    def name(self) -> Text:
        return "action_get_Facture_deux_mois_deux_annee"
 
    def preprocess_month(self, month: Text) -> Text:
        month = month.lower()
        return month

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        month_map = {
            "janvier": "01",
            "février": "02",
            "février": "02",
            "août": "08",
            "mars": "03",
            "avril": "04",
            "mai": "05",
            "juin": "06",
            "juillet": "07",
            "aout": "08",
            "septembre": "09",
            "octobre": "10",
            "novembre": "11",
            "décembre": "12",
            "decembre": "12"
        }

        month_entity1 = tracker.get_slot('monthD')
        month_entity2 = tracker.get_slot('monthF')
        year_entity1 = tracker.get_slot('AnneeD')
        year_entity2 = tracker.get_slot('AnneeF')

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
                    # Formatage du montant total
                    total_montant_formatted = "{:,.2f}".format(total_montant)
                    dispatcher.utter_message(f"Le montant total des factures entre {month_entity1} {year_entity1} et {month_entity2} {year_entity2} est {total_montant_formatted}.")
                else:
                    dispatcher.utter_message(f"Aucune donnée disponible pour la période entre {month_entity1} {year_entity1} et {month_entity2} {year_entity2}.")
            else:
                dispatcher.utter_message("Mois invalide.")
        else:
            dispatcher.utter_message("Je n'ai pas compris les mois ou les Annees.")

        return [SlotSet(slot, None) for slot in ["Etat", "type", "Montant", "Date", "Fournisseur", "Facture", "top", "Jour", "JourD", "JourF", "month", "monthD", "monthF", "Annee", "AnneeD", "AnneeF", "session_started_metadata"]]

#---------------------------------------------fonctionne pas-----------------------------------------------------
# ---------------------------------------------------------------------------------------------------

#   ------------------------------------------------------------------------------------------------------------
# from dictionnaire_Fournisseur import fournisseurs  
class ActionGetFournisseurMoisAnnee(Action):
    def name(self):
        return "action_get_Fournisseur_Mois_Annee"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        # Récupérer l'input complet de l'utilisateur
        user_input = tracker.latest_message.get("text")

        # La liste des fournisseurs est maintenant définie localement

        # Détecter le fournisseur à partir de la liste
        fournisseur = None
        for f in fournisseurs:
            if f.lower() in user_input.lower():
                fournisseur = f
                break

        # Si aucun fournisseur n'est détecté, envoyer un message à l'utilisateur et retourner
        if not fournisseur:
            dispatcher.utter_message("Je n'ai pas réussi à détecter le fournisseur.")
            return []   

        # Détecter le mois
        mois_mapping = {
            "janvier": 1, "février": 2,"fevrier": 2, "mars": 3, "avril": 4, "mai": 5, "juin": 6,
            "juillet": 7, "août": 8, "aout": 8, "septembre": 9, "octobre": 10, "novembre": 11, "décembre": 12,"decembre": 12
        }
        mois = None
        for m, num in mois_mapping.items():
            if m.lower() in user_input.lower():
                mois = num
                break

        # Si aucun mois n'est détecté, envoyer un message à l'utilisateur et retourner
        if not mois:
            conn = se_connecter_a_ssms()

            cursor = conn.cursor()
                    
            # Requête SQL pour obtenir les montants correspondant à un fournisseur donné
            query = """SELECT Fournisseur.Fournisseur, f.Montant, facture.etat , facture.Facture
                            FROM dbo.Fait f 
                            JOIN dbo.[Dimensions facture] facture ON f.FK_facture = facture.PK_facture
                            JOIN dbo.[Dimension Fournisseur] Fournisseur ON f.FK_Fournisseur = Fournisseur.Pk_Fournisseur
                            WHERE Fournisseur.Fournisseur = ?"""

            # Exécuter la requête SQL avec le fournisseur en tant que paramètre sécurisé
            cursor.execute(query, (fournisseur,))
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
                dispatcher.utter_message(text=f"Le montant total des factures pour le fournisseur {fournisseur} est de : {total_montant}.")
            else:
                # Aucun montant trouvé pour le fournisseur demandé
                dispatcher.utter_message(text=f"Aucun montant trouvé pour le fournisseur demandé pour {fournisseur} .")

            return []

        # Détecter l'année
        annee = None
        for word in user_input.split():
            if word.isdigit() and len(word) == 4:
                annee = int(word)
                break

        # Si aucune année n'est détectée, utiliser l'année actuelle
        if not annee:
            annee = datetime.now().year

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

        return []


# -----------------------------------------------------------------------------------------------------------------
import requests

class MontantParFournisseur(Action):
    def name(self) -> Text:
        return "Montant_Par_Fournisseur"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Récupérer l'input complet de l'utilisateur
        user_input = tracker.latest_message.get("text")

        # Recherche du fournisseur dans l'input utilisateur
        requested_fournisseur = None
        for f in fournisseurs:
            if f.lower() in user_input.lower():
                requested_fournisseur = f
                break
        
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

            # Envoi des données du fournisseur à l'API Plotly
            response = update_plotly_filter(requested_fournisseur)
            if response:
                dispatcher.utter_message(text="Données envoyées à l'API Plotly avec succès.")
            else:
                dispatcher.utter_message(text="Erreur lors de l'envoi des données à l'API Plotly.")
        else:
            # Aucun montant trouvé pour le fournisseur demandé
            dispatcher.utter_message(text=f"Aucun montant trouvé pour le fournisseur demandé pour {requested_fournisseur} .")

        return []

# Fonction pour envoyer les données du fournisseur à l'API Plotly
def update_plotly_filter(fournisseur):
    url = 'http://localhost:8053/'  # URL de votre API Plotly
    data = {'fournisseur': fournisseur}
    
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()  # Raise an error for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
        return None

# ---------------------------------------------------------------------------
# class MontantParFournisseur(Action):
#     def name(self) -> Text:
#         return "Montant_Par_Fournisseur"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

#         # Récupérer l'input complet de l'utilisateur
#         user_input = tracker.latest_message.get("text")

#         # Recherche du fournisseur dans l'input utilisateur
#         requested_fournisseur = None
#         for f in fournisseurs:
#             if f.lower() in user_input.lower():
#                 requested_fournisseur = f
#                 break
        
#         if requested_fournisseur is None:
#             dispatcher.utter_message(text="Désolé, je n'ai pas compris le fournisseur demandé.")
#             return []

#         # Connexion à la base de données (assurez-vous que "conn" est correctement défini)
#         cursor = conn.cursor()
            
#         # Requête SQL pour obtenir les montants correspondant à un fournisseur donné
#         query = """SELECT Fournisseur.Fournisseur, f.Montant, facture.etat , facture.Facture
#                     FROM dbo.Fait f 
#                     JOIN dbo.[Dimensions facture] facture ON f.FK_facture = facture.PK_facture
#                     JOIN dbo.[Dimension Fournisseur] Fournisseur ON f.FK_Fournisseur = Fournisseur.Pk_Fournisseur
#                     WHERE Fournisseur.Fournisseur = ?"""

#         # Exécuter la requête SQL avec le fournisseur en tant que paramètre sécurisé
#         cursor.execute(query, (requested_fournisseur,))
#         results = cursor.fetchall()

#         total_montant = 0  # Initialise le montant total

#         if results:
#             for result in results:
#                 # Récupérer les détails de chaque facture
#                 fournisseur, montant, etat , facture = result
#                 dispatcher.utter_message(
#                     text=f"Le fournisseur {fournisseur} pour la facture {facture} a un montant de {montant} pour l'état {etat}."
#                 )
#                 total_montant += montant  # Ajoute le montant au total

#             # Affiche le montant total à la fin
#             dispatcher.utter_message(text=f"Le montant total des factures pour le fournisseur {requested_fournisseur} est de : {total_montant}.")
#         else:
#             # Aucun montant trouvé pour le fournisseur demandé
#             dispatcher.utter_message(text=f"Aucun montant trouvé pour le fournisseur demandé pour {requested_fournisseur} .")

#         return []

# -------------------------------------------------------------------------------------------------------------
# from dictionnaire_Types import types_factures
class MontantParType(Action):
    def name(self) -> Text:
        return "Montant_Par_Type"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Récupérer l'input complet de l'utilisateur
        user_input = tracker.latest_message.get("text")

        # Recherche du type dans l'input utilisateur
        requested_type = None
        for type_facture in types_factures:
            if type_facture.lower() in user_input.lower():
                requested_type = type_facture
                break
        
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

        return []

# ----------------------------------------------------------------------------------------
 
# --------------------------------------------------------------------------------------------------------------------------------

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
            "février": "02",
            "août": "08",
            "mars": "03",
            "avril": "04",
            "mai": "05",
            "juin": "06",
            "juillet": "07",
            "aout": "08",
            "septembre": "09",
            "octobre": "10",
            "novembre": "11",
            "decembre": "12",
            "décembre": "12"
        }

        # Récupérer l'input complet de l'utilisateur
        user_input = tracker.latest_message.get("text")

        month_entity = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "aout", "septembre", "octobre", "novembre", "decembre"]

        # Recherche du mois dans l'input utilisateur
        month_entity = None
        for word in user_input.split():
            preprocessed_word = self.preprocess_month(word)
            if preprocessed_word in month_map:
                month_entity = preprocessed_word
                break

        if month_entity:
            month_num = month_map.get(month_entity)
            year_entity = tracker.get_slot("Annee")

            if year_entity:
                conn = se_connecter_a_ssms()
                cursor = conn.cursor()
                cursor.execute("SELECT SUM(f.montant) FROM dbo.fait f JOIN dbo.[Dimension_dates] date ON f.FK_Date = date.DateKey WHERE YEAR(date.date) = ? AND MONTH(date.date) <= ? ", (year_entity, month_num,))
                total_montant = cursor.fetchone()[0]

                if total_montant:
                    dispatcher.utter_message(f"Le montant total des factures jusqu'au mois de {month_entity} de l'année {year_entity} est de {total_montant}.")
                else:
                    dispatcher.utter_message(f"Aucune donnée disponible jusqu'au mois de {month_entity} de l'année {year_entity}.")
            else:
                conn = se_connecter_a_ssms()
                cursor = conn.cursor()
                cursor.execute("SELECT SUM(f.montant) FROM dbo.fait f JOIN dbo.[Dimension_dates] date ON f.FK_Date = date.DateKey WHERE MONTH(date.date) <= ?", (month_num,))
                total_montant = cursor.fetchone()[0]

                if total_montant:
                    dispatcher.utter_message(f"Le montant total des factures jusqu'au mois de {month_entity} est de {total_montant}.")
                else:
                    dispatcher.utter_message(f"Aucune donnée disponible jusqu'au mois de {month_entity}.")
        else:
            dispatcher.utter_message("Mois invalide.")

        return [SlotSet(slot, None) for slot in ["start_date", "end_date", "Etat", "type", "Montant", "Date", "Fournisseur", "Facture", "top", "Jour", "JourD", "JourF", "month", "monthD", "monthF", "Annee", "AnneeD", "AnneeF", "session_started_metadata"]]

# -------------------------------------------------------------------------------------------------------------------------

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

        # Récupérer l'input complet de l'utilisateur
        user_input = tracker.latest_message.get("text")

        # Liste des mois
        mois_list = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "aout", "septembre", "octobre", "novembre", "decembre"]

        # Recherche du mois dans l'input utilisateur
        month_entity = None
        for month in mois_list:
            preprocessed_month = self.preprocess_month(month)
            if preprocessed_month in user_input:
                month_entity = month
                break

        if month_entity:
            month_num = month_map.get(month_entity)
            year_entity = tracker.get_slot("Annee")

            if year_entity:
                conn = se_connecter_a_ssms()
                cursor = conn.cursor()
                cursor.execute("SELECT SUM(f.montant) FROM dbo.fait f JOIN dbo.[Dimension_dates] date ON f.FK_Date = date.DateKey WHERE MONTH(date) = ? AND YEAR(date.date) = ?", (month_num, year_entity,))
                total_montant = cursor.fetchone()[0]

                if total_montant:
                    dispatcher.utter_message(f"Le montant total des factures pour le mois de {month_entity} de l'année {year_entity} est {total_montant}.")
                else:
                    dispatcher.utter_message(f"Aucune donnée disponible pour le mois de {month_entity} de l'année {year_entity}.")
            else:
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

        return [SlotSet(slot, None) for slot in ["start_date", "end_date", "Etat", "type", "Montant", "Date", "Fournisseur", "Facture", "top", "Jour", "JourD", "JourF", "month", "monthD", "monthF", "Annee", "AnneeD", "AnneeF", "session_started_metadata"]]

# ---------------------------------------------------new--------------------------------------------------------------
class VerifierFournisseur(Action):
    def name(self) -> Text:
        return "action_verifier_fournisseur"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_input = tracker.latest_message.get("text")

        # Vérifier si l'entrée utilisateur correspond à un nom de fournisseur
        for f in fournisseurs:
            if f.lower() in user_input.lower():
                # Si un nom de fournisseur est trouvé, retourner True
                return [SlotSet("fournisseur_reconnu", True)]

        # Si aucun nom de fournisseur n'est trouvé, retourner False
        return [SlotSet("fournisseur_reconnu", False)]


class ResetFournisseurSlot(Action):
    def name(self) -> Text:
        return "action_reset_fournisseur_slot"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        return [SlotSet("fournisseur_reconnu", None)] 
# -------------------------------------------------------------------------------------------------------------------

class ActionObtenirFactureMontant(Action):
    def name(self) -> Text:
        return "action_obtenir_Facture_montant"
    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:

        # Récupérer l'input complet de l'utilisateur
        # last_input = tracker.get_slot("last_user_message")
        last_input=tracker.events[-3].get("value")
        print('ll1 ',last_input)
        if type(last_input) == type(None):
            last_input=tracker.latest_message.get("text")
            print("here2")
        print('ll2 ',last_input)
        llm = InferenceClient(model = 'mistralai/Mistral-7B-Instruct-v0.2', token = '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')
        prompt = """<s>[INST] 
        context: Your task is to Extract only the Invoice name and nothing else from the French text.
        the Invoice name could contain numbers, letters, spaces, parenthesis, slashes.
        No additional information or instructions should be provided.
        Here are three examples first example: Donne moi la facture  "FT/00748/2022 3/1" output :  Invoice name: FT/00748/2022 3/1.
        Second example: Les details sur la facture "36/2022 (2/2)" output :  Invoice name: 36/2022 (2/2).
        Third example: consulter facture "-1" output :  Invoice name: -1
        You need to do the output exactly like this don't add anything: Invoice name:
        Here is the text you need to work on:"""
        # Combined system context and prompt with template
        prompt +=   last_input+"""  [/INST]"""
        result = llm.text_generation(prompt,max_new_tokens=1000,temperature=0.1,top_p=0.95,top_k=50,)
        print(result)
        result = result.replace("Invoice name: ", "")
        if result.startswith(" "):
            result = result[1:]
        result=result.replace(".",'')
        print(result)
        if result:
            conn = se_connecter_a_ssms()  # Vous devez implémenter cette fonction

            if conn:
                # Exécuter la requête SQL pour obtenir le montant de la facture
                cursor = conn.cursor()
                query = """
                    SELECT f.montant, facture.facture, fournisseur.fournisseur, date.date
                    FROM dbo.fait f
                    JOIN dbo.[Dimension_dates] date ON f.FK_Date = Date.DateKey
                    JOIN dbo.[Dimensions facture] facture ON f.FK_facture = facture.PK_facture
                    JOIN dbo.[Dimension Fournisseur] Fournisseur ON f.FK_Fournisseur = Fournisseur.Pk_Fournisseur
                    WHERE facture.facture = ?
                """
                cursor.execute(query, (result,))
                results = cursor.fetchall()
                
                if results:
                    for result in results:
                        # Récupérer les détails de chaque facture
                        montant, Facture, Fournisseur, Date = result
                        dispatcher.utter_message(
                            text=f"La facture {Facture} est établie au nom du {Fournisseur}, d'un montant de {montant}, et datée du {Date}."
                        )
                else:
                    dispatcher.utter_message(text="Désolé, aucune information trouvée pour la facture spécifiée.")
            else:
                dispatcher.utter_message(text="Désolé, je n'ai pas pu me connecter à la base de données.")
        else:
            dispatcher.utter_message(text="Désolé, je n'ai pas compris le numéro de facture.")

        return [SlotSet("last_user_message", None)
]



# -----------------------------------------------------------------------------------------------------------------
class DefaultFallback(Action):
    def name(self) -> Text:
        return "action_default_fallback"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        SlotSet("last_user_message", None)
        # Récupérer l'entrée utilisateur
        user_input = tracker.latest_message.get("text")
        print('ip: '+user_input)
        fournisseur_detecte = None
        longueur_fournisseur_detecte = 0

        for f in fournisseurs:
            if f.lower() in user_input.lower():
                # Vérifier si le fournisseur courant est plus long que le fournisseur déjà détecté
                if len(f) > longueur_fournisseur_detecte:
                    fournisseur_detecte = f
                longueur_fournisseur_detecte = len(f)

        if fournisseur_detecte:
            # Stocker le dernier message de l'utilisateur dans le slot
            return [SlotSet("last_user_message", user_input), UserUtteranceReverted(), FollowupAction("Montant_Par_Fournisseur")]
 
        if "facture" in user_input:
            # Parcourir la liste des noms de facture
            print("verif1")
            for facture in factures:
                # Vérifier si le nom de facture est présent dans la chaîne
                if f"facture {facture.lower()}" in user_input.lower():
                    # Stocker le dernier message de l'utilisateur dans le slot
                    print("here")
                    return [SlotSet("last_user_message", user_input), UserUtteranceReverted(), FollowupAction("action_obtenir_Facture_montant")]

        # Si aucun nom de fournisseur n'est trouvé, retourner un message d'erreur par défaut
        dispatcher.utter_message(template="utter_default")
        return []

# -----------------------------------------------------------------------------------------------------------------

 
fournisseurs = [
    'ADHECOM SARL',
    'AIRCO',
    'AL MAADEN',
    'le fournisseur AMM',
    'ARC BUREAUTIQUE',
    'ARCHIDOC',
    'ASSAD INDUSTRIAL',
    'AST AVENIR SERVICE TRANSPORT',
    'ATR CORPORATE ET CONSULTING',
    'Avocat Hatem Kourda',
    'BAIEXPRESS',
    'BECHIR FAKHFAKH',
    'BEST CAR',
    'BOUDRANT',
    'BTPEQUIPEMENT',
    'CABINET BEN CHEIKH HENDA',
    'CAR PRO',
    'Cash&Carry',
    'CDTPR',
    'Chiffon d’Essuyage Tunisienne',
    'CMG',
    'CMVI',
    'COMET',
    'COREME',
    'CREATIVE AD. SCHOOL',
    'DELLMANN',
    'DELOITTE',
    'DIESEL ENERGY',
    'Dr. Jamel Darragi',
    'EDT',
    'ELECSATN',
    'ELECTROCNIC DESIGN SERVICE *EDS',
    'ELWIFEK FLEXIBLES',
    'EQUIPEMENT MODERNE AUTOMOTIVE',
    'EQUIPEMENT MODERNE HARDWARE',
    'EQUIPEMENTS SOUSSI',
    'ETS BEN YOUSSEF',
    'ETS BERRAIES',
    'EURO PARTS',
    'EXCELLIA CREANCE',
    'GAM',
    'GARAGE DU NORD BOURAOUI ZARDI',
    'GAS',
    'GATTOUSSI MECANIQUE GENERALE',
    'GEELEC',
    'GEISER',
    'GENERAL RADIATORS',
    'GENERAL TRANSPORT INTERNATIONAL (GTI)',
    "GENERALE D'EQUIPEMENTS ELECTRIQUES",
    'GLAMIVER',
    'GLOBAL RECOUVREMENT',
    'ICAR SA',
    'IDEAL ORAGANISATION SERVICES',
    'IDEALE AUTO NEGOCE',
    'Industrial Technical Services',
    'Innovation mecanique industrielle',
    'INTERNATIONAL TRANSIT',
    'IRES',
    'J.M.S PLUS',
    'JOUINI ELECTRIQUE INDUSTRIEL',
    'KAIS DORGHAM MECANIQUE AUTO',
    'LA BATTERIE',
    'La BATTERIE INDUSTRIELLE',
    'LA PRECISION T.M.T',
    'LE MOTEUR DIESEL',
    'LE PROFESSIONNEL',
    'Loogik Interactive',
    'LOURD DEPANN',
    'MAC BUREAU',
    'Maitre Yahyaoui Mustapha',
    'MARE',
    'MECANICA DIVISION GROS',
    'MEGA NUMERIQUE',
    'MEZGHANI PLUS MEUBLES',
    'MMSE',
    'MONDIAL ELECTRIC',
    'PEARTECH',
    'PIMA',
    'POLYCARGO',
    'QUEEN FORMATION',
    'RAPID POSTE',
    'ROYALTYRE',
    'SBIKA PROTECTION',
    'SCCM BF',
    'SELECT TRAVEL ET TOURS',
    'SHOPEX',
    'SHYK AUTO',
    'SIMEC',
    'SINPAR',
    'SMART ELECTRIC',
    'SMART TACHY',
    'SOCAGE',
    'SOCIETE BEN MESSAOUD FRERES',
    'SOCIETE DE MANUTENSION HELALI SARL',
    'SOCIETE ELBEZ DISTRIBUTION',
    'SOCIETE IMPRIMERIE DU CENTRE',
    'SOCIETE KACEM ET FILS',
    'SOCIETE PIECES ET MATERIELS SPM',
    'SODICA',
    'SOGEMAQ',
    'SOREM',
    'SOTUFLEX',
    'SPAIE',
    'SPIT ENGINS',
    'SSG SOCIETE SADRABAAL DE GARDIENNAGE',
    'SSTM',
    'STAFIM',
    'STAR EQUIPEMENTS',
    'STATION PNEU CHOUCHA (SPC)',
    'STE ALLO SERVICE REMORQUAGE',
    'STE BRAVO DES SERVICES',
    'STE BSA',
    'STE COSTA RENT A CAR',
    'STE EMEM DU CAPBON',
    'STE GHAMMAM NEGOCE',
    'STE JOMAA SA',
    'STE LE MOTEUR HOUSE',
    'STE OTOKAR',
    'STE POLY ELECTRIC AKOUDA',
    'STE POWER PROFESSIONEL TRANSPORT',
    'STE T.D.S',
    'STE ZOUHAIR KARRAY SECURITE',
    'STPR',
    'Strategie Digitale',
    'STRPA',
    'SUD METAL',
    'TASNIME VOYAGE ET TOURISME',
    "TECHNIQUE DE L'ELECTRICITE ET SERVICES T.E.S.",
    'Technique informatique et bureautique',
    'TECHNOMACHINE',
    'TOOFAST TECHNIC SERVICE PNEUS',
    'TOTAL TUNISIE',
    'TOUDECORS SARL',
    'TPS',
    'UHD',
    'USP',
    'VALORIA S.A',
    'VOGUE DISTRIBUTION',
    'ZRIBI MAJDI ARCHITECTE ET EXPERT BATIMENT',
]

factures = [
    '000126-23',
    '000267/23',
    '000455/23',
    '000484/23',
    '000555/23',
    '000594/22',
    '000706-23',
    '000713/23',
    '000734/23',
    '000925/23',
    '000994/23',
    '001038/22',
    '001065/23',
    '001079/23',
    '001143/23',
    '001440-23',
    '001546/22',
    '001563/22',
    '001674/22',
    '001674/22 10/10',
    '001674/22 2/10',
    '001674/22 3/10',
    '001674/22 4/10',
    '001674/22 6/10',
    '001674/22 7/10',
    '001674/22 8/10',
    '001674/22 9/10',
    '001674/22 1/10',
    '0017/2023',
    '0024/2023',
    '0081/2023',
    '0085_2022',
    '009/2023',
    '01/006773',
    '01/006796',
    '01/006822',
    '010-23',
    '0132/2023',
    '0158/2023',
    '019/2023',
    '019379/23',
    '019458/23',
    '019517/23',
    '021/2023',
    '023-23',
    '026/2022',
    '02872 4/1',
    '02872 4/2',
    '02872 4/3',
    '02872 4/4',
    '029/2023',
    '032 2023',
    '0325/2023',
    '0327/2023',
    '036 2023',
    '0376/2023',
    '038/2023',
    '039 2023',
    '039-23',
    '04/2022 du 01/12/2022',
    '0438/2022',
    '045_2023',
    '052/2023',
    '052-23',
    '053-2023',
    '0558/2023',
    '058/2023',
    '058_2023',
    '073/2023',
    '073_2023',
    '082-2023',
    '083/2023',
    '088/2023',
    '091/2023',
    '099-23',
    '-1',
    '-1-',
    '102',
    '102/2023',
    '105/2023',
    '1052',
    '113-23',
    '116/2023',
    '1165',
    '119/2023',
    '1197',
    '12/157/23',
    '12/222/23',
    '12/275/23',
    '12/300/23',
    '12/301/23',
    '12/728/22',
    '12309315',
    '12309317',
    '12309901',
    '12310545',
    '12310547',
    '12310970',
    '12310972',
    '12311507',
    '12312108',
    '12312281',
    '12312282',
    '12312617',
    '12312783',
    '12313222',
    '12313805',
    '12313975',
    '12314039',
    '12314275',
    '1259',
    '127/2023',
    '1273',
    '12877-A',
    '12899-A',
    '1300',
    '13021',
    '13024',
    '13058',
    '13070',
    '1310',
    '132023',
    '1323',
    '1335',
    '135/2023',
    '1351',
    '1363',
    '138/2023',
    '140/2023',
    '1427',
    '143/2023',
    '1452/2023',
    '146/2023',
    '15/2023',
    '1507',
    '1508',
    '153-23',
    '1538',
    '154/2023',
    '155/2023',
    '158/2023',
    '159/2023',
    '165/2023',
    '1666',
    '1667/2022',
    '168/2023',
    '1765',
    '1807',
    '184/11/04/2023',
    '185',
    '185/2023',
    '1859',
    '185DU2023',
    '187',
    '1888',
    '19/28/02/2023',
    '19-2023',
    '1929',
    '1930',
    '1946',
    '1952',
    '196-23',
    '197/2023',
    '199-23',
    '200/2022',
    '200-23',
    '201/2022',
    '201234',
    '201237',
    '201238',
    '201239',
    '201240',
    '202/2022',
    '20201389',
    '20-2023',
    '20212062',
    '20212063',
    '2022/0132',
    '2022/2240',
    '2022/3472',
    '2022/3477',
    '202200671',
    '202200833',
    '20220115',
    '20220120',
    '20220121',
    '2022016874',
    '2022017282',
    '2022017476',
    '202202732',
    '20220576',
    '20222243',
    '2023/0002',
    '2023/0012',
    '2023/0022',
    '2023/0040',
    '2023/0049',
    '2023/0053',
    '2023/0061',
    '2023/0079',
    '2023/0080',
    '2023/0090',
    '2023/0094',
    '2023/0095',
    '2023/0104',
    '2023/0106',
    '2023/0122',
    '2023/0129',
    '2023/0150',
    '2023/0190',
    '2023/0200',
    '2023/0216',
    '2023/0323',
    '2023/0537',
    '2023/0567',
    '2023/0626',
    '2023/0627',
    '2023/0642',
    '2023/0914',
    '2023/1028',
    '2023/1029',
    '2023/1276',
    '2023/12884',
    '2023/1317',
    '2023/1446',
    '2023/1658',
    '2023/1810',
    '2023/2020',
    '2023/2060',
    '2023/2091',
    '2023/2092',
    '2023/2166',
    '2023/2167',
    '2023/2414',
    '2023/2583',
    '2023/2666',
    '2023/2738',
    '2023/2864',
    '2023/2865',
    '2023/2972',
    '2023/3074',
    '2023/3126',
    '2023/3266',
    '2023/3327',
    '2023/3394',
    '2023/3448',
    '2023/3525',
    '2023/3733',
    '2023000160',
    '2023-000164',
    '2023-000273',
    '2023-000353',
    '2023000496',
    '2023000718',
    '202300106',
    '20230020',
    '20230021',
    '20230022',
    '20230031',
    '20230032',
    '202300384',
    '202300389',
    '202300626',
    '202300649',
    '202300763',
    '202301204',
    '20230148',
    '202301821',
    '20230183',
    '202301929',
    '202302023',
    '2023021',
    '202302234',
    '202302372',
    '2023024',
    '20230301',
    '20230302',
    '20230356',
    '20230430',
    '2023047',
    '2023048',
    '2023049',
    '20230495',
    '20230536',
    '2023054',
    '202306-01',
    '20230611',
    '2023071',
    '2023072',
    '2023073',
    '2023092',
    '2023107',
    '2023114',
    '2023118',
    '2023119',
    '20231478',
    '20231658',
    '2023169',
    '2023174',
    '20231886',
    '20232973',
    '20233205',
    '20248/23',
    '2031605',
    '2057',
    '20684',
    '208/2023',
    '21135/22',
    '21-2023',
    '213/2023',
    '216',
    '217',
    '219',
    '22/00351',
    '22/006653',
    '22/006654',
    '22/006815',
    '22/006908',
    '220',
    '2200982',
    '2200994',
    '2200996',
    '2201014',
    '220178',
    '220185',
    '220188',
    '220612/23',
    '221134/22',
    '221136/22',
    '221137/22',
    '221137/22 2/2',
    '221138/22',
    '221139/22',
    '221140/22',
    '221141/22',
    '221142/22',
    '221143/22',
    '221144/22',
    '221145/22',
    '221150/22',
    '221151/22',
    '221152/22',
    '221153/22',
    '221154/22',
    '221155/22',
    '221156/23',
    '221162/23',
    '221163/23',
    '221164/23',
    '221165/23',
    '221166/23',
    '221167/23',
    '221168/23',
    '221169/23',
    '221170/23',
    '221186/23',
    '221187/23',
    '221188/23',
    '221189/23',
    '221190/23',
    '221208/23',
    '221210/23',
    '221211/23',
    '221212/23',
    '221286/23',
    '221287/23',
    '221288/23',
    '221289/23',
    '221290/23',
    '221291/23',
    '221305/23',
    '221306/23',
    '221307/23',
    '221308/23',
    '221309/23',
    '221312/23',
    '221313/23',
    '221321/23',
    '22-2023',
    '2230195',
    '223646',
    '226/2022',
    '227/2022',
    '2281',
    '2292',
    '22FA0665',
    '22-FC50879',
    '22-FCC41573',
    '22-FCC41574',
    '22-FCC41575',
    '22-FCC42593',
    '22-FCC42840',
    '22-FCC42841',
    '22-FCC50044',
    '22-FCC50046',
    '22-FCC51964',
    '22-FCC51965',
    '22-FCC51967',
    '22-FCC51968',
    '22-FCC51969',
    '22-FCC51995',
    '22-FCC52133',
    '22-FCC52134',
    '22-FCC52137',
    '22-FCC52215',
    '22-FCC52216',
    '22-FCC52406',
    '22-FCC52409',
    '22-FCC52415',
    '22MEG03566',
    '22MMEG02634',
    '23/000631',
    '23/000653',
    '23/000722',
    '23/000965',
    '23/001004',
    '23/001419',
    '23/001831',
    '23/002194',
    '23/002544',
    '23/002769',
    '23/002771',
    '23/002821',
    '23/002949',
    '23/003484',
    '23/004456',
    '23/004655',
    '23/0165',
    '23/0308',
    '23/0309',
    '23/0379',
    '23/0380',
    '23/0381',
    '23+FVG006875',
    '23+FVGS002623',
    '23+FVGS004412',
    '23+FVGS005037',
    '23+FVGS005038',
    '23+FVGS005606',
    '23+FVGS006843',
    '23+FVGS006873',
    '23+FVGS006874',
    '23+FVGS008055',
    '23+FVGS008058',
    '23+FVGS008123',
    '2300042',
    '230006',
    '230010',
    '230011',
    '2300112',
    '230023',
    '230038',
    '230039',
    '230054',
    '2300676',
    '230074',
    '230075',
    '230076',
    '2300781',
    '2300783',
    '230084',
    '2301142',
    '230131',
    '230143',
    '230177',
    '230183',
    '230184',
    '230245',
    '2302715',
    '230579',
    '230623',
    '230880',
    '231204',
    '231205',
    '231352',
    '231353',
    '231577',
    '231787',
    '231833',
    '232',
    '232477',
    '234403',
    '234519',
    '234528',
    '235059',
    '238.951',
    '23FA0055',
    '23FA0139',
    '23FA0226',
    '23FA0519',
    '23FA0615',
    '23FA0685',
    '23-FCC55166',
    '23-FCC55168',
    '23-FCC55444',
    '23-FCC56640',
    '23-FCC56641',
    '23-FCC56642',
    '23-FCC56643',
    '23-FCC69566',
    '23-FCC69580',
    '23-FCC69594',
    '23-FCC69595',
    '23-FCC69763',
    '23-FCC69764',
    '23-FCC70848',
    '23FCC70883',
    '23-FCC70885',
    '23-FCC70886',
    '23-FCC70887',
    '23-FCC70900',
    '23-FCC70940',
    '23-FCC70941',
    '23-FCC70945',
    '23-FCC70993',
    '23-FCC71229',
    '23-FCC71230',
    '23-FCC71231',
    '23-FCC71269',
    '23-FCC71271',
    '23-FCC71476',
    '23-FCC71477',
    '23-FCC71515',
    '23-FVGS007149',
    '23-FVPR000984',
    '23MEG00376',
    '23MEG00486',
    '23MEG00744',
    '23MEG02370',
    '23MEG02493',
    '23MEG02776',
    '23MEG03656',
    '23MEG03734',
    '23TSP00087',
    '23TSP00119',
    '246/05/06/2023',
    '247/2022',
    '248/2023',
    '2517',
    '2559',
    '272023',
    '2761',
    '2762',
    '2766',
    '2769',
    '2774',
    '2775',
    '2776',
    '2780',
    '2786',
    '2787',
    '2789',
    '2790',
    '2805',
    '2806',
    '2807',
    '2809',
    '2810',
    '2814',
    '2816',
    '2827',
    '2828',
    '2829',
    '2834',
    '2840',
    '29/ 2023',
    '29/2023',
    '29/2023 -',
    '2921',
    '3000',
    '3023',
    '30392',
    '304/2023',
    '322/2023',
    '328',
    '331/2023',
    '3376',
    '3387',
    '3408',
    '3425',
    '3447',
    '3465',
    '3470',
    '3480',
    '35/2023',
    '350',
    '3503',
    '3508',
    '3523',
    '3528',
    '3537',
    '354',
    '354/',
    '3549',
    '355',
    '36/2022',
    '36/2022 (2/2)',
    '364',
    '365',
    '366',
    '37/2023',
    '374',
    '377',
    '383/2023',
    '391/2023',
    '393',
    '393/2023',
    '395/2023',
    '4',
    '40',
    '40/2023',
    '4005897589',
    '4005898980',
    '4005902305',
    '4005906201',
    '4005916537',
    '4005922644',
    '4005925724',
    '4005930417',
    '4005931059',
    '4005931060',
    '4005931441',
    '4005938019',
    '4005939383',
    '4005940113',
    '4005941590',
    '4005945996',
    '4005952355',
    '4005955095',
    '40462',
    '41',
    '43',
    '437/2023',
    '438/2023',
    '439/2023',
    '448/2023',
    '44927',
    '44958',
    '45078',
    '477/2023',
    '5',
    '50',
    '50416',
    '505',
    '50744',
    '51165',
    '51501',
    '5297/2023',
    '54/2023',
    '55/2023',
    '559',
    '56/2023',
    '57/2023',
    '6',
    '63/2023',
    '641428/2023/000852',
    '647083/2022/000852',
    '649',
    '66/2023',
    '670',
    '68',
    '69/12/09/2023',
    '694',
    '696750/2023/0000852',
    '70/2023',
    '7002023',
    '704',
    '7052023',
    '7092023',
    '73/2023',
    '737',
    '739',
    '755',
    '768',
    '77/2023',
    '783',
    '81/2023',
    '846',
    '847',
    '848',
    '849',
    '85/2023',
    '850',
    '850/2023',
    '872',
    '88',
    '893',
    '898',
    '900',
    '9102302292',
    '9102303480',
    '9201001308',
    '9201001385',
    '9201001446',
    '9201001570',
    '9201001661',
    '9201002111',
    '9201002202',
    '94/2023',
    '9401001219',
    '9401001344',
    '9401001389',
    '9401001851',
    '941001769',
    '958',
    '959',
    'A202203948',
    'A202300397',
    'A202300397 2/3',
    'A202300397 3/3',
    'A202300399A',
    'A202301420',
    'A202301421',
    'A202302356',
    'A202302701',
    'AVRIL 2023',
    'BL1020360',
    'EDT-23-FCC69596',
    'ELS-22FAC1001',
    'F TN000628/23',
    'F00853',
    'F0191/2023',
    'F20225908',
    'F20231441',
    'F20231856',
    'F20232448',
    'F20232968',
    'F20233339',
    'F20233977',
    'F20234506',
    'F20234993',
    'F2225382',
    'F2300023',
    'F230134',
    'F2307-00418',
    'F231007',
    'FA000378',
    'FA000380',
    'FA000384',
    'FA000398',
    'FA000399',
    'FA000400',
    'FA000402',
    'FA000404',
    'FA000405',
    'FA000406',
    'FA000410',
    'FA000431',
    'FA000439',
    'FA000443',
    'FA000450',
    'FA000454',
    'FA0010546',
    'FA0010608',
    'FA105601',
    'FA105602',
    'FA105637',
    'FA105644',
    'FA202239',
    'FA2023024',
    'FA22023',
    'FA221513',
    'FA221668',
    'FA23/0191',
    'FA230315',
    'FA230430',
    'FA230841',
    'FAB004338',
    'FAB004468',
    'FAC/2022/1617',
    'FAC/2022/1873',
    'FAC/2022/2086',
    'FAC/2023/0124',
    'FAC/2023/0285',
    'FAC/2023/1006',
    'FAC/2023/1164',
    'FAC/2023/1333',
    'FAC02934',
    'FAC230099',
    'FACBA23-01373',
    'FACT-2023/000131',
    'FACT-2023/000169',
    'FACT-2023/000170',
    'FACT-2023/000188',
    'FC220328/22',
    'FC232199',
    'FC4  008',
    'FC4 009',
    'FCC44088',
    'FCC44089',
    'FCC44090',
    'FCC45499',
    'FCC45500',
    'FCC45501',
    'FCC50047',
    'FCC50049',
    'FCC50050',
    'FCC50051',
    'FCC50052',
    'FCC50055',
    'FCC50056',
    'FCC50579',
    'FCC50580',
    'FCC50581',
    'FCC50662',
    'FCC51587',
    'FCC52497',
    'FCC53444',
    'FCC53544',
    'FCC53619',
    'FCC53623',
    'FCC53654',
    'FCC53655',
    'FCC53656',
    'FCC53739',
    'FCC53984',
    'FCC53985',
    'FCC54006',
    'FCC54141',
    'FCC54142',
    'FCC69565',
    'FCV2300174',
    'FCV2300661',
    'FEVRIER 2023',
    'FT/00024/2023',
    'FT/00107/2023',
    'FT/00192/2023',
    'FT/00546/2023',
    'FT/00641/2023',
    'FT/00685/2022',
    'FT/00748/2022 3/1',
    'FT/00748/2022 3/2',
    'FT/00748/2022 3/3',
    'FT000349',
    'FT000372',
    'FT000388',
    'FT000449',
    'FT000460',
    'FT000461',
    'FT000462',
    'FT23/02477',
    'FT23/02663',
    'FT2300437',
    'FT2300597',
    'FT230386',
    'FTN 000631/23',
    'FTN000173/22',
    'FTN000194/23',
    'FTN000480/23',
    'FTN000635/23',
    'FV/2300409',
    'FV1972023',
    'FV210413',
    'FV22/00308',
    'FV22/00319',
    'FV220867',
    'FV220893',
    'FV220912',
    'FV220927',
    'FV220939',
    'FV23/00003',
    'FV23/00004',
    'FV23/00005',
    'FV23/00011',
    'FV23/00013',
    'FV23/00034',
    'FV23/00060',
    'FV23/00106',
    'FV23/00166',
    'FV23/00191',
    'FV23/00192',
    'FV23/00193',
    'FV23/00207',
    'FV23/00216',
    'FV23/00221',
    'FV23/00228',
    'FV23/00267',
    'FV23/00280',
    'FV23/00281',
    'FV23/00325',
    'FV23/00327',
    'FV23/00332',
    'FV23/00333',
    'FV230012',
    'FV230022',
    'FV230035',
    'FV230050',
    'FV230085',
    'FV230100',
    'FV230113',
    'FV230231',
    'FV230237',
    'FV230275',
    'FV230350',
    'FV230357',
    'FV230411',
    'FV230420',
    'FV230457',
    'FV230459',
    'FV230560',
    'FV230564',
    'FV230589',
    'FV230652',
    'FV230665',
    'FV230674',
    'FV230703',
    'FV230730',
    'FV230762',
    'FV230778',
    'FV230779',
    'FV230780',
    'FV230800',
    'FV230818',
    'FV230824',
    'FV230828',
    'FV230847',
    'FVAV378695',
    'FVG013597',
    'FVG013598',
    'FVG013599',
    'FVG01360 2/2',
    'FVG013600',
    'FVG013600 (2/2)',
    'FVG013609',
    'FVG013661',
    'FVG013662',
    'FVG013710',
    'FVG013710 (2/2)',
    'FVG013711',
    'FVG013712',
    'FVG014776',
    'FVG014789',
    'FVG014858',
    'FVG014968',
    'FVG014969',
    'FVG014970',
    'FVG015243',
    'FVG015365',
    'FVG015366',
    'FVG015367',
    'FVGS000236',
    'FVGS000255',
    'FVGS000554',
    'FVGS000702',
    'FVGS001211',
    'FVGS001383',
    'FVGS001592',
    'FVGS001597',
    'FVGS001598',
    'FVGS007704',
    'FVGS007716',
    'FVGS007925',
    'FVGS00886',
    'FVPR000063',
    'LD04/2023',
    'LD05/2023',
    'LD1005/2022',
    'LD1007/2022',
    'LD1008/2023',
    'LD1015/2023',
    'LD1017/2022',
    'LD1020/2022',
    'LD1021/2023',
    'LD1025/2023',
    'LD1027/2023',
    'LD1029/2022',
    'LD1030/2022',
    'LD1033/2023',
    'LD1037',
    'LD1040/2022',
    'LD1044/2023',
    'LD1050/2023',
    'LD1052/2022',
    'LD1064/2022',
    'LD1083/2022',
    'LD1114/2022',
    'LD1119/2022',
    'LD112/2023',
    'LD1120/2022',
    'LD1129/2022',
    'LD1139/2022',
    'LD1153/2022',
    'LD1154/2022',
    'LD116/2023',
    'LD1170/2022',
    'LD1172/2022',
    'LD119/2023',
    'LD12/2023',
    'LD122/2023',
    'LD123/2023',
    'LD125/2023',
    'LD13/2023',
    'LD142/2023',
    'LD16/2023',
    'LD170/2023',
    'LD176/2023',
    'LD182/2023',
    'LD187/2023',
    'LD197/2023',
    'LD206/2023',
    'LD216/2023',
    'LD233/2023',
    'LD256/2023',
    'LD270/2023',
    'LD280/2023',
    'LD283/2023',
    'LD294/2023',
    'LD30/2023',
    'LD301/2023',
    'LD313/2023',
    'LD331/2023',
    'LD341/2023',
    'LD342/2023',
    'LD345/2023',
    'LD357/2023',
    'LD375/2023',
    'LD376/2023',
    'LD397/2023',
    'LD399/2023',
    'LD40/2023',
    'LD414/2023',
    'LD420/2023',
    'LD43/2023',
    'LD433/2023',
    'LD44/2023',
    'LD441/2023',
    'LD450/2023',
    'LD451/2023',
    'LD459/2023',
    'LD47/2023',
    'LD475/2023',
    'LD483/2023',
    'LD486/2023',
    'LD488/2023',
    'LD489/2023',
    'LD497/2023',
    'LD504/2023',
    'LD525/2023',
    'LD53/2023',
    'LD542/2023',
    'LD544/2023',
    'LD547/2023',
    'LD548/2023',
    'LD55/2023',
    'LD579/2023',
    'LD58/2023',
    'LD607/2023',
    'LD640/2023',
    'LD678/2023',
    'LD683/2023',
    'LD688/2023',
    'LD71/2023',
    'LD714/2023',
    'LD716/2023',
    'LD727/2023',
    'LD737/2023',
    'LD752/2023',
    'LD771/2023',
    'LD830/2023',
    'LD862/2023',
    'LD868/2023',
    'LD871/2023',
    'LD887/2023',
    'LD896/2023',
    'LD903/2023',
    'LD941/2023',
    'LD966/2023',
    'LD969/2023',
    'LD985/2023',
    'LD987/2023',
    'LD998/2023',
    'lLD750/2023',
    'MAIS 2023',
    'MB-23+FVGS000487',
    'MB-23+FVGS003871',
    'MB-23+FVGS005176',
    'MB-23+FVGS005585',
    'MB-23+FVGS006480²',
    'MB-23+FVGS006844',
    'MB-23+FVGS006845',
    'ME/17/8576 1/3',
    'ME/17/8576 2/3',
    'ME/17/8576 3/3',
    'ME/18/0098 2/1',
    'ME/18/0098 2/2',
    'ME/18/0345 1/2',
    'ME/18/0345 2/2',
    'ME/18/0649',
    'ME/18/0892',
    'ME/18/1206',
    'ME/18/2395',
    'ME/18/2477',
    'MOIS DE MARS',
    'NA-23+FVGSAV00719',
    'NOTE DE DEBIT N°03/2022',
    "NOTE D'HONORAIRES MOIS DECEMBRE 2022",
    "NOTE D'HONORAIRES MOIS JANVIER 2023",
    "NOTE D'HONORAIRES MOIS NOVEMBRE 2022",
    'REL',
    'SF230007',
    'SF230063',
    'SF230752',
    'SF230851',
    'SF230981',
    'SMFAC+22/3683',
    'SMFAC+22/3774',
    'SMFAC+22/3776',
    'SMFAC+22/3869',
    'SMFAC+22/3870',
    'SMFAC+22/3948',
    'SMFAC+22/3961',
    'SMFAC+22/4026',
    'SMFAC+22/4027',
    'SMFAC+22/4157',
    'SMFAC+22/4188',
    'SMFAC+22/4191',
    'SMFAC+22/4752',
    'SMFAC+22/4838',
    'SMFAC+22/4900',
    'SMFAC+22/4901',
    'SMFAC+22/4902',
    'SMFAC+22/4933',
    'SMFAC+22/4934',
    'SMFAC+22/4935',
    'SMFAC+22/4936',
    'SMFAC+22/4961',
    'SMFAC+22/5046',
    'SMFAC+22/5058',
    'SMFAC+22/5093',
    'SMFAC+23/0115',
    'SMFAC+23/0202',
    'SMFAC+23/0211',
    'SMFAC+23/0322',
    'SMFAC+23/0325',
    'SMFAC+23/0488',
    'SMFAC+23/0591',
    'SMFAC+23/0592',
    'SMFAC+23/2734',
    'SMFAC+23/2828',
    'SMFAC+23/3363',
    'SMFAC+23/3530',
    'SMFAC+23/3632',
    'SYS-2023',
    'USP-23-FCC55167',
    'V+FACT22/0440',
    'V+FACT22/0441',
]
types_factures = [
    'des cartes et systèmes électroniques',
    'agence de communication',
    'agence de voyage',
    'assurance',
    'Assurance/Consulting',
    'automobile',
    'avocat',
    'banque/assurance',
    'bureautique',
    'centre dappele',
    'consulting',
    'decoration',
    'domaine electricite',
    'equipement',
    'equipement Electriques',
    'équipement pour le bâtiment',
    'expertise',
    'formattion',
    'industrie',
    'informatique',
    'kiosque',
    'laboratoire',
    'mecanique',
    'medical',
    'meubles',
    'société',
    'societe de livraison',
    'societe de vetements',
    'transit',
    'vente different produit',
]

