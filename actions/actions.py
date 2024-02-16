# from typing import Any, Text, Dict, List
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher

# class Actionsayphone(Action):
#     def name(self) -> Text:
#         return "action_say_phone"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker, 
#             domain: Dict[Text,Any]) -> List[Dict[Text,Any]]:
        
#         phone = tracker.get_slot("phone")

#         if not phone:
#             dispatcher.utter_message(text="sorry i dont know your phone number")
#         else:
#             dispatcher.utter_message(text=f"your phone number is {phone}")

#         return []
    
#  ---------------------------------------------------------
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



from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import pyodbc

class ActionObtenirMontant(Action):
    def name(self) -> Text:
        return "action_obtenir_montant"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        
        # Récupérer l'entité montant du tracker
        ref_entity = tracker.get_slot("Montant")
        if ref_entity:
            ref = int(ref_entity)
            dispatcher.utter_message(text=f"Je recherche le montant pour la facture numéro {ref}...")
            # Se connecter à la base de données
            conn = se_connecter_a_ssms()  # Vous devez implémenter ces fonctions

            if conn:
                # Exécuter la requête SQL pour obtenir le montant de la facture
                query = f"SELECT montant FROM dbo.source WHERE Référence = '{ref}'"
                results = executer_requete(conn, query)  # Vous devez implémenter cette fonction

                if results:
                    montant = results[0][0]
                    dispatcher.utter_message(template="utter_montant", montant=montant, facture=ref)  # Assurez-vous que la valeur du slot montant est fournie
                else:
                    dispatcher.utter_message(text="Désolé, je n'ai pas pu trouver le montant pour cette facture.")
            else:
                dispatcher.utter_message(text="Désolé, je n'ai pas pu me connecter à la base de données.")
        else:
            dispatcher.utter_message(text="Désolé, je n'ai pas pu extraire le numéro de facture.")
        
        return []
