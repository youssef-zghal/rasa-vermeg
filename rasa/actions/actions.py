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

class FirstAction(Action):
    def name(self) -> Text:
        return "first_action"
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # user_input = tracker.events[-3].get("value")
        user_input = tracker.latest_message.get("text")

        print('user: ',user_input)
        client = InferenceClient(model = 'mistralai/Mixtral-8x7B-Instruct-v0.1', token = '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')
        result = client.text_generation("""<s>[INST] 
        Vous êtes un système de classification d'actions et tu dois être très précis. 
        Nous vous fournissons les actions et leurs descriptions:
                                        
        action: action_llm_general
        Description: si l'utilisateur posent des questions en général ou bien veux s'informer d'autres sujets de la vie ou autres et qui peuvent ne pas avoir une liaison avec les factures etc..

        action: action_salutation  
        Description: quand l'utilisateur demande un salut 
                                        
        action: utter_bye  
        Description: quand l'utilisateur demande l'au revoir
                                        
        action: Action_Obtenir_Information_Par_Reference  
        Description: quand l'utilisateur demande les informations d'une facture à partir de sa référence
                                        
        action: action_obtenir_montant_sup  
        Description: quand l'utilisateur demande les montants des factures qui sont supérieurs à des montants donnés 
        
        action: action_obtenir_montant_inf  
        Description: quand l'utilisateur demande les montants des factures qui sont inférieurs à des montants donnés 
        
        action: action_obtenir_montant_egal  
        Description: quand l'utilisateur demande les montants des factures qui sont égaux à des montants donnés 
        
        action: action_montant_total_fournisseurs  
        Description: Cette action permet à l'utilisateur de récupérer le montant total des fournisseurs,le montant total de chaque fournisseur
                                        
        action: Montant_Total_Par_Etat  
        Description: Cette action permet à l'utilisateur de récupérer le montant total des transactions pour chaque etat spécifique
                                        
        action: action_afficher_montants_etat_validees  
        Description: Cette action permet à l'utilisateur de consulter le montant total des factures valides,en se concentrant uniquement sur les factures qui ont été valide
                                        
        action: action_afficher_montants_etat_crees  
        Description: Cette action permet à l'utilisateur de consulter le montant total des factures créées, en se concentrant uniquement sur les factures qui ont été cree
                                        
        action: action_afficher_montants_etat_prets  
        Description: quand l'utilisateur demande à consulter le montant total pour les factures prêtes pour le paiement, en se concentrant uniquement sur les factures qui ont été pret pour paiement
                                          
        action: Montant_Total_Par_Type  
        Description: quand l'utilisateur demande le montant total de chaque type et le montant total de tous les types
                                        
        action: action_count_Fournisseur  
        Description: quand l'utilisateur demande de connaître le nombre de fournisseurs dans la base de données 
                                        
        action: action_count_Fournisseur_par_mois  
        Description: quand l'utilisateur demande de connaître le nombre de fournisseurs par mois, il affiche chaque mois combien de fournisseurs il y a et on peut aussi spécifier un mois
                                        
        action: action_count_Fournisseur_par_annee  
        Description: quand l'utilisateur demande de connaître le nombre de fournisseurs par une année particulère
                                        
        action: action_count_Type  
        Description: quand l'utilisateur demande de connaître le nombre de types dans la base et combien de type en travail avec eux
                                        
        action: action_count_Facture_par_fournisseur  
        Description: si l'utilisateur demande de savoir chaque fournisseur possède combien de facture  
                                        
        action: action_count_Facture_par_mois  
        Description: quand l'utilisateur demande de connaître le nombre de factures par mois, il affiche chaque mois combien de factures il y a et on peut aussi spécifier un mois
                                        
        action: action_count_Facture_par_annee  
        Description: quand l'utilisateur demande de connaître le nombre de factures par année, il affiche chaque année combien de factures il y a et on peut aussi spécifier une année
                                        
        action: action_top_fournisseurs  
        Description: si l'utilisateur aurait besoin de savoir qui sont les n meilleurs fournisseurs
                                        
        action: action_top_Type  
        Description: si l'utilisateur aurait besoin de savoir qui sont les n meilleurs types de fournisseurs
                                        
        action: action_Less_fournisseurs  
        Description: si l'utilisateur aurait besoin de savoir qui sont les n moins fournisseurs existants dans la base
                                        
        action: action_montant_total_facture  
        Description: pour savoir combien vaut le montant total de toutes les factures dans la base de données
                                        
        action: action_get_Facture_mois  
        Description: quand l'utilisateur demande le montant d'achat en indiquant le mois et pouvant indiquer l'année ou même ne pas l'indiquer 
                                        
        action: action_montant_total_pluriannuel  
        Description: demander le montant total des achats par année en mentionnant une année ou plusieurs
                                        
        action: action_total_Deux_mois  
        Description: lorsque l'utilisateur demande les montants entre un intervalle de mois pour une année donnée
                                        
        action: action_get_Facture_Jusquau_Mois  
        Description: demander le montant total jusqu'à un mois et une année donnée ou même on peut ne pas fournir l'année
                                        
        action: action_afficher_montants_etat_validees_Date  
        Description: demande d'affichage des montants des factures qui ont un état validé pour un mois et une année donnés
                                        
        action: action_afficher_montants_etat_cree_Date  
        Description: demande d'affichage des montants des factures qui ont un état créé pour un mois et une année donnés
                                        
        action: action_afficher_montants_etat_Prêt_pour_paiement_Date  
        Description: demande d'affichage des montants des factures qui ont un état prêt pour le paiement pour un mois et une année donnés
                                        
        action: action_get_Facture_deux_mois_deux_annee  
        Description: quand l'utilisateur demande les montants des factures figurant entre un intervalle en mentionnant le mois et l'année de début et le mois et l'année de fin
                                        
        action: action_obtenir_Facture_montant  
        Description: si l'utilisateur voudrait savoir les détails d'une facture donnée
                                        
        action: Montant_Par_Type  
        Description: quand l'utilisateur voudrait savoir les montants des factures pour un type de fournisseur donné et leur montant total
                                        
        action: Montant_Par_Fournisseur  
        Description: quand l'utilisateur voudrait savoir les montants des factures pour un fournisseur donné et le montant total pour le fournisseur donné
                                        
        action: action_get_Fournisseur_Mois_Annee  
        Description: demander les montants total des fournisseur pour un mois et une année donnée
                                        
        action: action_count_Facture_Par_Etat  
        Description: demander nombre de facture pour chaque etats  

        action: action_count_Facture
        Description: si l'utilisateur demande de savoir combien de facture en possède dans la base, le nombre total des factures 
                                                                                                         
                Vous avez une expression et vous devez la classifier selon l'action. 
                Répondez uniquement avec l'action. 
                Si l'expression ne correspond à aucune des descriptions d'action, renvoyez "None".
                Vous devez produire la sortie exactement comme suit, ne rien ajouter : L'action est : .
                Voici le message à classer: """ + user_input + """ [/INST]""",
                                max_new_tokens=2048,
                                # do_sample=True,
                                temperature=0.1,
                                # n_batch=50,
                                top_p=0.95,
                                top_k=50,
                                # repetition_penalty=1.1
                            )
        print(result.replace('\\', '').replace(" L'action est :",'').strip().replace('```diff',''))
        next_action=result.replace('\\', '').replace(" L'action est :",'').replace('```diff','').strip()
        print("debut",next_action)
        print("fin")
        # write_variable_to_file(user_input)
        return [SlotSet("last_user_message", user_input),UserUtteranceReverted(), FollowupAction(next_action)]

class ActionSayHello(Action):
    def name(self) -> Text:
        return "action_salutation"
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        user_input = tracker.events[-3].get("value")
        try:
            # Charger le modèle avec les paramètres personnalisés
            llm = InferenceClient(model = 'mistralai/Mixtral-8x7B-Instruct-v0.1', token = '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')
            prompt = "<s> [INST] Vous vous appelez InvoiceBot et vous êtes conçu pour fournir des réponses polies en français, repondre a ce text: [lang] fr [/lang]"
            prompt += user_input +" [/INST]"
            # Call the model with the prompt and extract the answer
            result = llm.text_generation(prompt,max_new_tokens=1000,temperature=0.8,top_p=0.7,top_k=50,)
            print(result)
            answer_start=0
            answer_end = len(result) 
            answer = result[answer_start:answer_end].strip()
            # Display the answer
            dispatcher.utter_message(text=answer)
        except Exception as e:
            # Gérer les exceptions et afficher un message approprié
            print("Une erreur s'est produite:", e)

        return []
# ////////////////////////////////////////////////////////-------------------MOCHKLA
#mochkla
class ActionObtenirInformationParReference(Action):
    def name(self) -> Text:
        return "Action_Obtenir_Information_Par_Reference"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        user_input = tracker.events[-3].get("value")
        llm = InferenceClient(model='mistralai/Mixtral-8x7B-Instruct-v0.1', token='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')
                # Générer une réponse en utilisant le modèle
        prompt = f"""<s> [INST] Vous êtes un chatbot conçu pour detecter lq référence d'une facture dans une phrase souhaitée par l'utilisateur.
                Votre réponse doit être un seul nombre, sans ajout d'informations supplémentaires.
                Lorsque l'utilisateur fournit un texte, vous devez indiquer le numéro de référence demandé.
                Exemple:
                Input: "Donne moi les détails de la facture référence 62673 ?"
                Output: 62673
                Input: "référence 20200 ?"
                Output: 20200
                Voici les message duquel tu dois extraire le nombre: """ + user_input + "[/INST]"

        ref = llm.text_generation(prompt, max_new_tokens=100, temperature=0.1, top_p=0.95, top_k=50)
        ref = ref.replace("Output: ", '').strip()
        print("Réponse du modèle :", ref)
        # Récupérer l'entité montant du tracker
        if ref:
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
        
        return []

# ////////////////////////////////////////////--------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------   
class ActionObtenirMontantInf(Action):
    def name(self) -> Text:
        return "action_obtenir_montant_inf"
    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        # user_input = tracker.latest_message.get("text")
        user_input = tracker.events[-3].get("value")

        # # Initialisation de la facture détectée et de sa longueur
        # for f in factures:
        #     if f.lower() in user_input.lower():
        #             return [UserUtteranceReverted(), FollowupAction("action_obtenir_Facture_montant")]
        # Récupérer l'entité montant du tracker 

        llm = InferenceClient(model='mistralai/Mixtral-8x7B-Instruct-v0.1', token='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')
                # Générer une réponse en utilisant le modèle
        prompt = f"""<s> [INST] Vous êtes un chatbot conçu pour detecter un nombre dans une phrase souhaitée par l'utilisateur.
                Votre réponse doit être un seul nombre, sans ajout d'informations supplémentaires.
                Lorsque l'utilisateur fournit un texte, vous devez indiquer le nombre demandé.
                Exemple:
                Input: "Quel est le montant superieur à 1000DT ?"
                Output: 1000
                Voici les message duquel tu dois extraire le nombre: """ + user_input + "[/INST]"

        result = llm.text_generation(prompt, max_new_tokens=100, temperature=0.1, top_p=0.95, top_k=50)
        result = result.replace("Output: ", '').strip()
        print("Réponse du modèle :", result)


        ref_entity = result
        # ref_entity = tracker.get_slot("Montant")
        if ref_entity:
            montant = int(ref_entity)
            # Se connecter à la base de données
            conn = se_connecter_a_ssms()  # Vous devez implémenter ces fonctions
            if conn:
                # Exécuter la requête SQL pour obtenir les détails des factures avec un montant supérieur
                query = f"""
                    SELECT Fournisseur.Fournisseur ,Facture.Facture , Date.Date , f.Montant , Facture.Etat , Fournisseur.type
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
                        fournisseur, facture, date, montant, etat, type_facture = result
                        date_str = date.strftime("%Y-%m-%d")
                        montant_formatte = "{:,.2f}".format(montant) 
                        dispatcher.utter_message(template="utter_inf",
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

        return []


 
# ------------------------------------------------------------------------------------------------------------------

class ActionObtenirMontantSup(Action):
    def name(self) -> Text:
        return "action_obtenir_montant_sup"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        # user_input = tracker.latest_message.get("text")
        user_input = tracker.events[-3].get("value")

        # # Initialisation de la facture détectée et de sa longueur
        # for f in factures:
        #     if f.lower() in user_input.lower():
        #             return [UserUtteranceReverted(), FollowupAction("action_obtenir_Facture_montant")]
        # Récupérer l'entité montant du tracker 

        llm = InferenceClient(model='mistralai/Mixtral-8x7B-Instruct-v0.1', token='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')
                # Générer une réponse en utilisant le modèle
        prompt = f"""<s> [INST] Vous êtes un chatbot conçu pour detecter un nombre dans une phrase souhaitée par l'utilisateur.
                Votre réponse doit être un seul nombre, sans ajout d'informations supplémentaires.
                Lorsque l'utilisateur fournit un texte, vous devez indiquer le nombre demandé.
                Exemple:
                Input: "Quel est le montant inferieur à 1000DT ?"
                Output: 1000
                Voici les message duquel tu dois extraire le nombre: """ + user_input + "[/INST]"

        result = llm.text_generation(prompt, max_new_tokens=100, temperature=0.1, top_p=0.95, top_k=50)
        result = result.replace("Output: ", '').strip()
        print("Réponse du modèle :", result)

        ref_entity = result
        # ref_entity = tracker.get_slot("Montant")
        if ref_entity:
            montant = int(ref_entity)
            # Se connecter à la base de données
            conn = se_connecter_a_ssms()  # Vous devez implémenter ces fonctions

            if conn:
                # Exécuter la requête SQL pour obtenir les détails des factures avec un montant supérieur
                query = f"""
                    SELECT Fournisseur.Fournisseur , Facture.Facture , Date.Date , f.Montant , Facture.Etat , Fournisseur.type
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
                        fournisseur, facture, date, montant, etat, type_facture = result
                        date_str = date.strftime("%Y-%m-%d")
                        montant_formatte = "{:,.2f}".format(montant)
                        dispatcher.utter_message(template="utter_sup", 
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
        
        return []


# ------------------------------------------------------------------------------------------------------------------

class ActionObtenirMontantegal(Action):
    def name(self) -> Text:
        return "action_obtenir_montant_egal"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        # user_input = tracker.latest_message.get("text")
        user_input = tracker.events[-3].get("value")

        # # Initialisation de la facture détectée et de sa longueur
        # for f in factures:
        #     if f.lower() in user_input.lower():
        #             return [UserUtteranceReverted(), FollowupAction("action_obtenir_Facture_montant")]
        # Récupérer l'entité montant du tracker 

        llm = InferenceClient(model='mistralai/Mixtral-8x7B-Instruct-v0.1', token='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')
                # Générer une réponse en utilisant le modèle
        prompt = f"""<s> [INST] Vous êtes un chatbot conçu pour detecter un nombre dans une phrase souhaitée par l'utilisateur.
                Votre réponse doit être un seul nombre, sans ajout d'informations supplémentaires.
                Lorsque l'utilisateur fournit un texte, vous devez indiquer le nombre demandé.
                Exemple:
                Input: "Quel est le montant egal à 1000DT ?"
                Output: 1000
                Voici les message duquel tu dois extraire le nombre: """ + user_input + "[/INST]"

        result = llm.text_generation(prompt, max_new_tokens=100, temperature=0.1, top_p=0.95, top_k=50)
        result = result.replace("Output: ", '').strip()
        print("Réponse du modèle :", result)


        ref_entity = result
        # ref_entity = tracker.get_slot("Montant")
        if ref_entity:
            montant = int(ref_entity)
            # Se connecter à la base de données
            conn = se_connecter_a_ssms()  # Vous devez implémenter ces fonctions

            if conn:
                # Exécuter la requête SQL pour obtenir les détails des factures avec un montant supérieur
                query = f"""
                    SELECT Fournisseur.Fournisseur , Facture.Facture , Date.Date , f.Montant , Facture.Etat , Fournisseur.type
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
                        fournisseur, facture, date, montant, etat, type_facture = result
                        date_str = date.strftime("%Y-%m-%d")
                        montant_formatte = "{:,.2f}".format(montant)
                        dispatcher.utter_message(template="utter_egal", 
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
        
        return []

    
# -----------------------------------------------------------------------------------------------------------------
# ///mochkla
# class ActionMontantTotalFournisseurs(Action):
#     def name(self) -> Text:
#         return "action_montant_total_fournisseurs"

#     async def run(
#         self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
#     ) -> List[Dict[Text, Any]]:
#         # Obtention de user_input
#         user_input = tracker.events[-3].get("value")

#         # Se connecter à la base de données
#         conn = se_connecter_a_ssms()  # Assurez-vous d'avoir cette fonction implémentée

#         if conn:
#             # Exécuter la requête SQL pour obtenir les montants dus par fournisseur
#             query = f"""
#             SELECT Fournisseur.Fournisseur, SUM(f.Montant) AS MontantTotalFournisseur
#             FROM dbo.fait f 
#             JOIN dbo.[Dimension fournisseur] Fournisseur ON f.FK_Fournisseur = Fournisseur.Pk_fournisseur
#             WHERE {user_input} 
#             GROUP BY Fournisseur.Fournisseur
#             """  
#             results = executer_requete(conn, query)  # Assurez-vous d'avoir cette fonction implémentée

#             if results:
#                 montants_fournisseurs = []
#                 for row in results:
#                     fournisseur = row[0]
#                     montant_total = row[1]
#                     montant_formatte = "{:,.2f}".format(montant_total)  # Formatage du montant
#                     dispatcher.utter_message(
#                         text=f"Le fournisseur {fournisseur} doit un montant total de {montant_formatte}."
#                     )
#                     montants_fournisseurs.append(montant_total)

#                 somme_total_montants = sum(montants_fournisseurs)
#                 somme_total_formattee = "{:,.2f}".format(somme_total_montants)  # Formatage de la somme totale
#                 dispatcher.utter_message(
#                     text=f"La somme totale des montants dus par les fournisseurs est {somme_total_formattee}."
#                 )
                
#             else:
#                 dispatcher.utter_message(text="Désolé, je n'ai pas pu trouver les informations sur les montants dus par fournisseur.")
#         else:
#             dispatcher.utter_message(text="Désolé, je n'ai pas pu me connecter à la base de données.")

#         return []


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

        return []
# -----------------------------------------------------------------------------------------------------------------
# mochkla

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

        return []


# -----------------------------------------------------------------------------------------------------------------
# mochkla

class ActionCountFactureParEtat(Action):
    def name(self):
        return "action_count_Facture_Par_Etat"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:            
            # Exécutez la requête pour compter les Facture par état
            conn = se_connecter_a_ssms() 
            cursor = conn.cursor()
            cursor.execute("SELECT facture.Etat, COUNT(Facture) AS NombreFactures FROM dbo.fait f JOIN dbo.[Dimensions facture] facture ON f.FK_facture = facture.PK_facture GROUP BY facture.Etat")
            counts = cursor.fetchall()  # Obtenez le nombre de factures par état

            # Créez un message avec les résultats pour chaque état
            message = "Nombre de factures par état : \n"
            for etat, count in counts:
                message += f"{etat}: {count} factures\n"

            # Envoyez la réponse au dispatcher pour la réponse de l'assistant
            dispatcher.utter_message(text=message)
        except Exception as e:
            # En cas d'erreur, affichez un message d'erreur
            dispatcher.utter_message(text="Une erreur s'est produite lors de la connexion à la base de données.")

        return []

# -----------------------------------------------------------------------------------------------------------------
#   mochkla   
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

        return [ ]

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

        return [ ]

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

        return []

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

        return []

# -----------------------------------------------------------------------------------------------------------------
class ActionCountFournisseurParAnnee(Action):
    def name(self) -> Text:
        return "action_count_Fournisseur_par_annee"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:


            # user_input = tracker.latest_message.get("text")
            user_input = tracker.events[-3].get("value")

            llm = InferenceClient(model='mistralai/Mixtral-8x7B-Instruct-v0.1', token='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')
                    # Générer une réponse en utilisant le modèle
            prompt = f"""<s> [INST] Vous êtes un chatbot conçu pour detecter les années dans une phrase souhaitée par l'utilisateur.
                    Votre réponse doit être une année ou plusieurs, sans ajout d'informations supplémentaires.
                    Lorsque l'utilisateur fournit un texte, vous devez indiquer l'année demandé.
                    si aucune année n'est fournie return None
                    Exemple:
                    Input: "Quel est le nombre de fournisseur pour année 2002?"
                    Output: 2002
                    Input: "Quel est le nombre de fournisseur par année?"
                    Output: None
                    Voici les message duquel tu dois extraire le nombre: """ + user_input + "[/INST]"

            result = llm.text_generation(prompt, max_new_tokens=100, temperature=0.1, top_p=0.95, top_k=50)
            result = result.replace("Output: ", '').strip()
            print("Réponse du modèle :", result)


            ref_entity = result
            if ref_entity and ref_entity!='None':
                # Exécuter la requête pour compter les fournisseurs pour l'année spécifiée
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(DISTINCT Fournisseur) FROM dbo.fait f JOIN dbo.[Dimension_dates] date ON f.FK_Date = Date.DateKey JOIN dbo.[Dimension Fournisseur] fournisseur ON f.FK_Fournisseur = fournisseur.PK_Fournisseur WHERE YEAR(date.date) = ?", (ref_entity,))
                count = cursor.fetchone()[0]  # Obtenir le nombre de fournisseurs pour l'année spécifiée

                # Envoyer la réponse avec le nombre de fournisseurs pour l'année spécifiée
                dispatcher.utter_message(text=f"Nombre de fournisseurs pour l'année {ref_entity} : {count}")
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

            return []


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

        user_input = tracker.events[-3].get("value")

        llm = InferenceClient(model='mistralai/Mixtral-8x7B-Instruct-v0.1', token='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')
                    # Générer une réponse en utilisant le modèle
        prompt = f"""<s> [INST] Vous êtes un chatbot conçu pour detecter les mois dans une phrase souhaitée par l'utilisateur.
                    Votre réponse doit être un mois ou plusieurs, sans ajout d'informations supplémentaires.
                    Lorsque l'utilisateur fournit un texte, vous devez indiquer mois demandé.
                    si aucune mois n'est fournie return None
                    Exemple:
                    Input: "Quel est le nombre de fournisseur pour mois fevrier?"
                    Output: fevrier
                    Input: "Quel est le nombre de fournisseur par mois?"
                    Output: None
                    Voici les message duquel tu dois extraire le nombre: """ + user_input + "[/INST]"

        result = llm.text_generation(prompt, max_new_tokens=100, temperature=0.1, top_p=0.95, top_k=50)
        result = result.replace("Output: ", '').strip()
        print("Réponse du modèle :", result)

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
                response_text_specified_month = f"Nombre de fournisseurs pour {specified_month.capitalize()} : {count_specified_month}"
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
                response_text_by_month = "Nombre de fournisseurs par mois :\n"
                for month, count in counts_by_month.items():
                    response_text_by_month += f"{month.capitalize()} : {count}\n"

                # Envoyer la réponse avec le texte formaté pour chaque mois
                dispatcher.utter_message(text=response_text_by_month)

        except Exception as e:
            # En cas d'erreur, affichez un message d'erreur
            dispatcher.utter_message(text="Une erreur s'est produite lors de la connexion à la base de données.")

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

class ActionCountFacture(Action):
    def name(self):
        return "action_count_Facture_par_fournisseur"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:            
            # Exécutez la requête pour compter les Facture par fournisseur
            cursor = conn.cursor()
            cursor.execute("SELECT Fournisseur.Fournisseur, COUNT(Facture) AS NombreFactures FROM dbo.fait f JOIN dbo.[Dimension fournisseur] fournisseur ON f.FK_Fournisseur = fournisseur.Pk_fournisseur JOIN dbo.[Dimensions facture] facture ON f.FK_facture = facture.PK_facture GROUP BY Fournisseur.Fournisseur")            
            counts = cursor.fetchall()  # Obtenez le nombre de factures par fournisseur

            # Créez un message avec les résultats pour chaque fournisseur
            for fournisseur, count in counts:
                message = f"{fournisseur} : {count} factures"
                dispatcher.utter_message(text=message)
        except Exception as e:
            # En cas d'erreur, affichez un message d'erreur
            dispatcher.utter_message(text="Une erreur s'est produite lors de la connexion à la base de données.")

        return []


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
            "août": "08",
            "septembre": "09",
            "octobre": "10",
            "novembre": "11",
            "décembre": "12"
        }
        preprocessed_month = month.lower()
        # preprocessed_month = preprocessed_month.replace('é', 'e').replace('ê', 'e').replace('û', 'u').replace('û', 'u').replace('ô', 'o').replace('î', 'i').replace('è', 'e')
        return month_map.get(preprocessed_month, None)

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

            user_input = tracker.events[-3].get("value")

            llm = InferenceClient(model='mistralai/Mixtral-8x7B-Instruct-v0.1', token='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')
                        # Générer une réponse en utilisant le modèle
            prompt = f"""<s> [INST] Vous êtes un chatbot conçu pour detecter le mois dans une phrase souhaitée par l'utilisateur.
                        Votre réponse doit être un nom pour un mois , sans ajout d'informations supplémentaires.
                        Lorsque l'utilisateur fournit un texte, vous devez indiquer mois demandé.
                        si aucune mois n'est fournie return None
                        Exemple:
                        Input: "Quel est le nombre de facture pour mois fevrier?"
                        Output: fevrier
                        Input: "Quel est le nombre de facture par mois?"
                        Output: None
                        Voici les message duquel tu dois extraire le nombre: """ + user_input + "[/INST]"

            result = llm.text_generation(prompt, max_new_tokens=100, temperature=0.1, top_p=0.95, top_k=50)
            result = result.replace("Output: ", '').strip()
            print("Réponse du modèle :", result)
            month_entity=result
            if month_entity and  month_entity !='None':
                # Prétraiter le mois pour correspondre au format dans la base de données
                month_num = self.preprocess_month(month_entity)

                if month_num:
                    # Exécuter la requête pour compter les factures et calculer le montant total pour le mois spécifié
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(Facture), SUM(Montant) FROM dbo.fait f JOIN dbo.[Dimension_dates] date ON f.FK_Date = Date.DateKey JOIN dbo.[Dimensions facture] facture ON f.FK_facture = facture.PK_facture WHERE MONTH(date) = ?", (month_num,))
                    result = cursor.fetchone()  # Obtenir le nombre de factures et le montant total pour le mois spécifié
                    count = result[0]
                    total_amount = result[1]

                    # Envoyer la réponse avec le nombre de factures et le montant total pour le mois spécifié
                    dispatcher.utter_message(text=f"Pour {month_entity.capitalize()} :\nNombre de factures : {count}\nMontant total : {total_amount} ")
                else:
                    dispatcher.utter_message(text="Mois non valide.")

            else:
                # Liste des mois
                mois_list = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]

                # Boucle à travers tous les mois
                for month in mois_list:
                    month_num = self.preprocess_month(month)

                    # Exécuter la requête pour compter les factures et calculer le montant total pour le mois donné
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(Facture), SUM(Montant) FROM dbo.fait f JOIN dbo.[Dimension_dates] date ON f.FK_Date = Date.DateKey JOIN dbo.[Dimensions facture] facture ON f.FK_facture = facture.PK_facture WHERE MONTH(date) = ?", (month_num,))
                    result = cursor.fetchone()  # Obtenir le nombre de factures et le montant total pour le mois donné
                    count = result[0]
                    total_amount = result[1]

                    # Envoyez un message pour chaque mois avec le nombre de factures et le montant total
                    message = f"Pour {month.capitalize()} :\nNombre de factures : {count}\nMontant total : {total_amount} "
                    dispatcher.utter_message(text=message)

            return []

# -------------------------------------------------------------------------------------------

class ActionCountFactureParAnnee(Action):
    def name(self) -> Text:
        return "action_count_Facture_par_annee"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

            user_input = tracker.events[-3].get("value")

            llm = InferenceClient(model='mistralai/Mixtral-8x7B-Instruct-v0.1', token='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')
                    # Générer une réponse en utilisant le modèle
            prompt = f"""<s> [INST] Vous êtes un chatbot conçu pour detecter les années dans une phrase souhaitée par l'utilisateur.
                    Votre réponse doit être une année ou plusieurs, sans ajout d'informations supplémentaires.
                    Lorsque l'utilisateur fournit un texte, vous devez indiquer l'année demandé.
                    si aucune année n'est fournie return None
                    Exemple:
                    Input: "Quel est le nombre de facture pour année 2002?"
                    Output: 2002
                    Input: "Quel est le nombre de facture par année?"
                    Output: None
                    Voici les message duquel tu dois extraire le nombre: """ + user_input + "[/INST]"

            result = llm.text_generation(prompt, max_new_tokens=100, temperature=0.1, top_p=0.95, top_k=50)
            result = result.replace("Output: ", '').replace('```','').strip()
            print("Réponse du modèle :", result)
            year_entity=result
            if year_entity and year_entity !='None':  
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



            return []

# -------------------------------------------------------------------------------------------
class TopFournisseurs(Action):
    def name(self) -> Text:
        return "action_top_fournisseurs"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_input = tracker.events[-3].get("value")
        llm = InferenceClient(model='mistralai/Mixtral-8x7B-Instruct-v0.1', token='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')

        prompt = """<s> [INST] Vous êtes un chatbot conçu pour répondre à des requêtes sur le nombre de fournisseurs souhaités par l'utilisateur.
        Votre réponse doit être un seul nombre, sans ajout d'informations supplémentaires.
        Lorsque l'utilisateur fournit un texte, vous devez indiquer le nombre de fournisseurs demandés.
        Exemple:
        Input: "Quel est le meilleur fournisseur ?"
        Output: Nombre: 1
        Veuillez saisir votre question:""" + user_input + "[/INST]"

        result = llm.text_generation(prompt, max_new_tokens=100, temperature=0.1, top_p=0.95, top_k=50)
        result = result.replace("Nombre: ", '').strip()
        print(result)

        # Connexion à la base de données (assurez-vous que "conn" est correctement défini)
        conn = se_connecter_a_ssms()

        # Requête SQL pour obtenir les top fournisseurs par montant
        query = f"""SELECT TOP {result} Fournisseur.Fournisseur, SUM(f.Montant) as Total_Montant
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

        return []

# -----------------------------------------------------------------------------
# mistralai/Mixtral-8x7B-Instruct-v0.1'
class TopType(Action):
    def name(self) -> Text:
        return "action_top_Type"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_input = tracker.events[-3].get("value")
        llm = InferenceClient(model='mistralai/Mixtral-8x7B-Instruct-v0.1', token='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')

        prompt = """<s> [INST] Vous êtes un chatbot conçu pour répondre à des requêtes sur le nombre de type souhaités par l'utilisateur.
        Votre réponse doit être un seul nombre, sans ajout d'informations supplémentaires.
        Lorsque l'utilisateur fournit un texte, vous devez indiquer le nombre de type demandés seulement n'ajoute rien de plus.
        Exemple:
        Input: "Quel est le meilleur type ?"
        Output: Nombre: 1
        Input: "Quel sont les cinq meilleurs types ?"
        Output: Nombre: 5
        Veuillez saisir votre question:""" + user_input + "[/INST]"

        result = llm.text_generation(prompt, max_new_tokens=20, temperature=0.1, top_p=0.95, top_k=50)
        result = result.replace("Nombre: ", '').replace("Output:",'').strip()
        print('res:',result)

        # Connexion à la base de données (assurez-vous que "conn" est correctement défini)
        conn = se_connecter_a_ssms()

        # Requête SQL pour obtenir les top fournisseurs par montant
        query = f"""SELECT TOP {result} Fournisseur.Type, SUM(f.Montant) as Total_Montant
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

        return []

# -----------------------------------------------------------------------------
    
class LessFournisseurs(Action):
    def name(self) -> Text:
        return "action_Less_fournisseurs"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_input = tracker.events[-3].get("value")
        llm = InferenceClient(model='mistralai/Mixtral-8x7B-Instruct-v0.1', token='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')

        prompt = """<s> [INST] Vous êtes un chatbot conçu pour répondre à des requêtes sur le nombre de fournisseurs souhaités par l'utilisateur.
        Votre réponse doit être un seul nombre, sans ajout d'informations supplémentaires.
        Lorsque l'utilisateur fournit un texte, vous devez indiquer le nombre de fournisseurs demandés.
        Exemple:
        Input: "Quel est le moins fournisseur ?"
        Output: Nombre: 1
        Veuillez saisir votre question:""" + user_input + "[/INST]"

        result = llm.text_generation(prompt, max_new_tokens=100, temperature=0.1, top_p=0.95, top_k=50)
        result = result.replace("Nombre: ", '').strip()
        print(result)

        # Connexion à la base de données (assurez-vous que "conn" est correctement défini)
        conn = se_connecter_a_ssms()

        # Requête SQL pour obtenir les top fournisseurs par montant (en excluant les montants nuls)
        query = f"""SELECT TOP {result} Fournisseur.Fournisseur, SUM(f.Montant) as Total_Montant
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

        return []

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

#         return []
    
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

        return []



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

            llm = InferenceClient(model='mistralai/Mixtral-8x7B-Instruct-v0.1', token='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')
            last_input = tracker.events[-3].get("value")
            prompt = """<s> [INST] Vous êtes un chatbot conçu pour detecter l'année dans une phrase souhaitée par l'utilisateur. 
                            Votre réponse doit être nombre pour une année ou plusieurs année, sans ajout d'informations supplémentaires.
                            Lorsque l'utilisateur fournit un texte, vous devez indiquer année demandé.
                            Input: "je veux avoir le montant total pour année 2022 et 2023"
                            Output: {2022,2023}
                            Input: "je veux avoir le montant total pour année 2022?"
                            Output: {2022}
                            Voici les message duquel tu dois extraire le nombre: """ + last_input + "[/INST]"
            result = llm.text_generation(prompt, max_new_tokens=100, temperature=0.1, top_p=0.7, top_k=50)
            result=result.replace("Output:","").strip()
            annees=result
            print(result)
            print(annees)
            if len(annees) >= 1:
                montant_total_pluriannuel = 0
                for annee in annees.strip('{}').split(','):
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

                annees_formattees = ', '.join(annees.strip('{}').split(','))
                montant_total_pluriannuel_formatte = "{:,.2f}".format(montant_total_pluriannuel)  # Formatage du montant total
                dispatcher.utter_message(
                    text=f"Le montant total des factures pour les Annees {annees_formattees} est de {montant_total_pluriannuel_formatte}."
                )

            else:
                dispatcher.utter_message(text="Je n'ai pas compris pour quelles Annees vous voulez obtenir le montant total des factures.")
        return []
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
        user_input = tracker.events[-3].get("value")
        llm = InferenceClient(model='mistralai/Mixtral-8x7B-Instruct-v0.1', token='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')
        prompt = """<s> [INST] You are a date interval extractor, your task is to parse French messages containing actions between two month and one year and output them in numeric format. 
        Your output should be structured as follows: month1,month2,year and don't add anything else. 
        Here is an example: je veux avoir les factures entre juin et juillet en 2027 Output: 06,07,2027.
        Here's the french message: consulter les achats des factures entre janvier et mars en 2023[/INST]"""
        result = llm.text_generation(prompt, max_new_tokens=1300, temperature=0.1, top_p=0.7, top_k=50)
        result = result.replace("type name: ", "").rstrip('.')
        if result.startswith(" "):
            result = result[1:]
        print(result)

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

        return []
#---------------------------------------------------------------------------------------------------------------------------------------------------
  
#---------------------------------------------------------------------------------------------------------------------------------------------------


class ActionAfficherMontantsEtatValideesDate(Action):
    def name(self) -> Text:
        return "action_afficher_montants_etat_validees_Date"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        llm = InferenceClient(model='mistralai/Mixtral-8x7B-Instruct-v0.1', token='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')
        last_input = tracker.events[-3].get("value")

        # Récupérer le mois et l'Annee spécifiés, avec des valeurs par défaut si non spécifiés
        prompt = f"""<s> [INST] Vous êtes un chatbot conçu pour detecter le mois dans une phrase souhaitée par l'utilisateur.
                        Votre réponse doit être le numéro du mois seulement, sans ajout d'informations supplémentaires.
                        Exemple:
                        Input: "je veux avoir le montant total pour mois mars 2022"
                        Output: 03
                        Voici les message duquel tu dois extraire le nombre: """ + last_input + "[/INST]"
        mois = llm.text_generation(prompt, max_new_tokens=100, temperature=0.1, top_p=0.95, top_k=50)
        mois = mois.replace("Output: ", '').strip()
        
        print("Mois :", mois)
        prompt = f"""<s> [INST] Vous êtes un chatbot conçu pour detecter l'année dans une phrase souhaitée par l'utilisateur.
                        Votre réponse doit être le numéro de l'année seulement, sans ajout d'informations supplémentaires.
                        Si l'utilisateur n'a pas fourni d'année donne moi en output None
                        Exemple:
                        Input: "je veux avoir le montant total pour le fournisseur AIRCO en mars 2022"
                        Output: 2022
                        Input: "je veux avoir le montant total pour le fournisseur AIRCO en mars"
                        Output: None
                        Voici les message duquel tu dois extraire le nombre: """ + last_input + "[/INST]"
        année = llm.text_generation(prompt, max_new_tokens=100, temperature=0.1, top_p=0.95, top_k=50)
        année = année.replace("Output: ", '').strip()
        print("Année :", année)
        if ('None' in année):
            année=2023

        
        # Connexion à la base de données (assurez-vous que "conn" est correctement défini)
        conn = se_connecter_a_ssms() 
        
        # Obtenir le nombre de jours dans le mois spécifié pour la requête
        
        # Requête SQL pour obtenir tous les montants correspondant à l'état Validé pour le mois et l'Annee spécifiés
        query = f"""SELECT Fournisseur.Fournisseur , Facture.Facture , Date.Date , SUM(f.Montant) AS MontantTotal
                    FROM dbo.fait f 
                    JOIN dbo.[Dimension fournisseur] fournisseur ON f.FK_Fournisseur = fournisseur.Pk_fournisseur
                    JOIN dbo.[Dimensions facture] facture ON f.FK_facture = facture.PK_facture
                    JOIN dbo.[Dimension_dates] date ON f.FK_Date = Date.DateKey 
                    WHERE facture.etat = 'Validé' AND MONTH(Date.Date) = {mois} AND YEAR(Date.Date) = {année}
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
                text=f"Le montant total des factures validées pour le mois {mois} de l'{année} est de {total_amount}."
            )
        else:
            # Aucun montant trouvé pour l'état Validé ce mois-ci
            dispatcher.utter_message(text=f"Aucun montant trouvé pour l'état 'Validé' pour le mois {calendar.month_name[mois]} {année}.")

        return []


#----------------------------------------créé-------------------------------------------


class ActionAfficherMontantsEtatCrééDate(Action):
    def name(self) -> Text:
        return "action_afficher_montants_etat_cree_Date"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        llm = InferenceClient(model='mistralai/Mixtral-8x7B-Instruct-v0.1', token='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')
        last_input = tracker.events[-3].get("value")

        # Récupérer le mois et l'Annee spécifiés, avec des valeurs par défaut si non spécifiés
        prompt = f"""<s> [INST] Vous êtes un chatbot conçu pour detecter le mois dans une phrase souhaitée par l'utilisateur.
                        Votre réponse doit être le numéro du mois seulement, sans ajout d'informations supplémentaires.
                        Exemple:
                        Input: "je veux avoir le montant total pour mois mars 2022"
                        Output: 03
                        Voici les message duquel tu dois extraire le nombre: """ + last_input + "[/INST]"
        mois = llm.text_generation(prompt, max_new_tokens=100, temperature=0.1, top_p=0.95, top_k=50)
        mois = mois.replace("Output: ", '').strip()
        
        print("Mois :", mois)
        prompt = f"""<s> [INST] Vous êtes un chatbot conçu pour detecter l'année dans une phrase souhaitée par l'utilisateur.
                        Votre réponse doit être le numéro de l'année seulement, sans ajout d'informations supplémentaires.
                        Si l'utilisateur n'a pas fourni d'année donne moi en output None
                        Exemple:
                        Input: "je veux avoir le montant total pour le fournisseur AIRCO en mars 2022"
                        Output: 2022
                        Input: "je veux avoir le montant total pour le fournisseur AIRCO en mars"
                        Output: None
                        Voici les message duquel tu dois extraire le nombre: """ + last_input + "[/INST]"
        année = llm.text_generation(prompt, max_new_tokens=100, temperature=0.1, top_p=0.95, top_k=50)
        année = année.replace("Output: ", '').strip()
        print("Année :", année)
        if ('None' in année):
            année=2023
        
        # Connexion à la base de données (assurez-vous que "conn" est correctement défini)
        conn = se_connecter_a_ssms() 
        
        # Requête SQL pour obtenir tous les montants correspondant à l'état Validé pour le mois et l'Annee spécifiés
        query = f"""SELECT Fournisseur.Fournisseur , Facture.Facture , Date.Date , SUM(f.Montant) AS MontantTotal
                    FROM dbo.fait f 
                    JOIN dbo.[Dimension fournisseur] fournisseur ON f.FK_Fournisseur = fournisseur.Pk_fournisseur
                    JOIN dbo.[Dimensions facture] facture ON f.FK_facture = facture.PK_facture
                    JOIN dbo.[Dimension_dates] date ON f.FK_Date = Date.DateKey 
                    WHERE facture.etat = 'créé' AND MONTH(Date.Date) = {mois} AND YEAR(Date.Date) = {année}
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
                text=f"Le montant total des factures créé pour le mois {mois} de l'{année} est de {total_amount}."
            )
        else:
            # Aucun montant trouvé pour l'état Validé ce mois-ci
            dispatcher.utter_message(text=f"Aucun montant trouvé pour l'état 'créé' pour le mois {calendar.month_name[mois]} {année}.")

        return []

#---------------------------------------------pret pour paiement------------------------------------------------------

class ActionAfficherMontantsEtatPrêtPourPaiementDate(Action):
    def name(self) -> Text:
        return "action_afficher_montants_etat_Prêt_pour_paiement_Date"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        llm = InferenceClient(model='mistralai/Mixtral-8x7B-Instruct-v0.1', token='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')
        last_input = tracker.events[-3].get("value")

        # Récupérer le mois et l'Annee spécifiés, avec des valeurs par défaut si non spécifiés
        prompt = f"""<s> [INST] Vous êtes un chatbot conçu pour detecter le mois dans une phrase souhaitée par l'utilisateur.
                        Votre réponse doit être le numéro du mois seulement, sans ajout d'informations supplémentaires.
                        Exemple:
                        Input: "je veux avoir le montant total pour mois mars 2022"
                        Output: 03
                        Voici les message duquel tu dois extraire le nombre: """ + last_input + "[/INST]"
        mois = llm.text_generation(prompt, max_new_tokens=100, temperature=0.1, top_p=0.95, top_k=50)
        mois = mois.replace("Output: ", '').strip()
        
        print("Mois :", mois)
        prompt = f"""<s> [INST] Vous êtes un chatbot conçu pour detecter l'année dans une phrase souhaitée par l'utilisateur.
                        Votre réponse doit être le numéro de l'année seulement, sans ajout d'informations supplémentaires.
                        Si l'utilisateur n'a pas fourni d'année donne moi en output None
                        Exemple:
                        Input: "je veux avoir le montant total pour le fournisseur AIRCO en mars 2022"
                        Output: 2022
                        Input: "je veux avoir le montant total pour le fournisseur AIRCO en mars"
                        Output: None
                        Voici les message duquel tu dois extraire le nombre: """ + last_input + "[/INST]"
        année = llm.text_generation(prompt, max_new_tokens=100, temperature=0.1, top_p=0.95, top_k=50)
        année = année.replace("Output: ", '').strip()
        print("Année :", année)
        if ('None' in année):
            année=2023
        
        # Connexion à la base de données (assurez-vous que "conn" est correctement défini)
        conn = se_connecter_a_ssms() 
        
        
        # Requête SQL pour obtenir tous les montants correspondant à l'état Validé pour le mois et l'Annee spécifiés
        query = f"""SELECT Fournisseur.Fournisseur , Facture.Facture , Date.Date , SUM(f.Montant) AS MontantTotal
                    FROM dbo.fait f 
                    JOIN dbo.[Dimension fournisseur] fournisseur ON f.FK_Fournisseur = fournisseur.Pk_fournisseur
                    JOIN dbo.[Dimensions facture] facture ON f.FK_facture = facture.PK_facture
                    JOIN dbo.[Dimension_dates] date ON f.FK_Date = Date.DateKey 
                    WHERE facture.etat = 'Prét pour paiement' AND MONTH(Date.Date) = {mois} AND YEAR(Date.Date) = {année}
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
                text=f"Le montant total des factures pret pour paiement pour le mois {mois} de l'{année} est de {total_amount}."
            )
        else:
            # Aucun montant trouvé pour l'état Validé ce mois-ci
            dispatcher.utter_message(text=f"Aucun montant trouvé pour l'état 'Prêt pour paiement' pour le mois {calendar.month_name[mois]} {année}.")

        return []


#----------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------

class ActionGetFactureDeuxMoisDeuxAnnee(Action):  
    def name(self) -> Text:
        return "action_get_Facture_deux_mois_deux_annee"
 

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        


        llm = InferenceClient(model='mistralai/Mixtral-8x7B-Instruct-v0.1', token='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')
        prompt = """<s> [INST] You are a date interval extractor, your task is to parse French messages containing actions between two dates and output them in numeric format. 
        Your output should be structured as follows: month1,year1,month2,year2 and don't add anything else. 
        Here is an example: je veux avoir les factures entre juin 2025 ET juillet 2027 Output: 06,2025,07,2027.
        Here's the french message: """+tracker.events[-3].get("value")+"""[/INST]"""
        result = llm.text_generation(prompt, max_new_tokens=1300, temperature=0.1, top_p=0.7, top_k=50)
        print(result)


        chiffres = result.split(',')

# Convertir chaque sous-chaîne en entiera
        month_entity1 = int(chiffres[0])
        year_entity1 = int(chiffres[1])
        month_entity2 = int(chiffres[2])
        year_entity2 = int(chiffres[3].rstrip('.'))

        # Afficher les chiffres extraits
        print("a =", month_entity1)
        print("b =", year_entity1)
        print("c =", month_entity2)
        print("d =", year_entity2)

        print("monthD ",month_entity1, "yearD ",year_entity1 )
        print("monthF" ,month_entity2 ,"yearF ",year_entity2 )

        if month_entity1 and month_entity2 and year_entity1 and year_entity2:
            if month_entity1 and month_entity2:
                # Conversion des dates en objets datetime
                date1 = datetime(int(year_entity1), int(month_entity1), 1)
                date2 = datetime(int(year_entity2), int(month_entity2), 1)
                
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

        return []



#   ------------------------------------------------------------------------------------------------------------
# from dictionnaire_Fournisseur import fournisseurs  
# Import des bibliothèques nécessaires
import requests
from datetime import datetime
# Fonction pour envoyer les données du fournisseur à l'API Plotly
import requests

def update_plotly_filter(fournisseur):
    url = 'http://localhost:8053/'  # Ensure this matches your Flask app's URL
    data = {'fournisseur': fournisseur}
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()  # Checks for HTTP request errors
        print("Response from Flask:", response.json())  # Log response to verify
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
        return False

class ActionGetFournisseurMoisAnnee(Action):
    def name(self):
        return "action_get_Fournisseur_Mois_Annee"
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        # Récupérer l'input complet de l'utilisateur
        last_input = tracker.events[-3].get("value")
        llm = InferenceClient(model='mistralai/Mixtral-8x7B-Instruct-v0.1', token='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')
        prompt = """<s>[INST] 
        context: Your task is to Extract only the supplier name and nothing else from the French text.
        the supplier name could contain letters, spaces, parenthesis, slashes.
        No additional information or instructions should be provided.
        Here are three examples first example: Donne moi details sur fournisseur  "ELECTROCNIC DESIGN SERVICE *EDS" output :  supplier name: ELECTROCNIC DESIGN SERVICE *EDS.
        Second example: consulter le fournisseur "GENERAL TRANSPORT INTERNATIONAL (GTI)" output :  supplier name: GENERAL TRANSPORT INTERNATIONAL (GTI).
        Third example: voir le montant fournisseur "LA PRECISION T.M.T" output :  supplier name: LA PRECISION T.M.T
        You need to do the output exactly like this don't add anything: supplier name:
        Here is the text you need to work on:"""
        # Combined system context and prompt with template
        prompt += last_input + """  [/INST]"""
        fournisseur = llm.text_generation(prompt, max_new_tokens=1000, temperature=0.1, top_p=0.95, top_k=50, )
        fournisseur = fournisseur.replace("supplier name: ", "").rstrip('.')
        if fournisseur.startswith(" "):
            fournisseur = fournisseur[1:]
        print("Fournisseur :", fournisseur)
                        # Générer une réponse en utilisant le modèle
        prompt = f"""<s> [INST] Vous êtes un chatbot conçu pour detecter le mois dans une phrase souhaitée par l'utilisateur.
                        Votre réponse doit être le numéro du mois seulement, sans ajout d'informations supplémentaires.
                        Exemple:
                        Input: "je veux avoir le montant total pour mois mars 2022"
                        Output: 03
                        Voici les message duquel tu dois extraire le nombre: """ + last_input + "[/INST]"
        mois = llm.text_generation(prompt, max_new_tokens=100, temperature=0.1, top_p=0.95, top_k=50)
        mois = mois.replace("Output: ", '').strip()
        print("Mois :", mois)

        prompt = f"""<s> [INST] Vous êtes un chatbot conçu pour detecter l'année dans une phrase souhaitée par l'utilisateur.
                        Votre réponse doit être le numéro de l'année seulement, sans ajout d'informations supplémentaires.
                        Exemple:
                        Input: "je veux avoir le montant total pour le fournisseur AIRCO en mars 2022"
                        Output: 2022
                        Voici les message duquel tu dois extraire le nombre: """ + last_input + "[/INST]"
        année = llm.text_generation(prompt, max_new_tokens=100, temperature=0.1, top_p=0.95, top_k=50)
        année = année.replace("Output: ", '').strip()
        print("Année :", année)
        if not année:
            année = datetime.now().year
        # Si aucun mois n'est détecté, envoyer un message à l'utilisateur et retourner
        if not mois or not année:
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
            # Envoi des données du fournisseur à l'API Plotly
            response = update_plotly_filter(fournisseur)
            # if response:
            #     dispatcher.utter_message(text="Données envoyées à l'API Plotly avec succès.")
            # else:
            #     dispatcher.utter_message(text="Erreur lors de l'envoi des données à l'API Plotly.")
            return []
        # Connexion à la base de données
        conn = se_connecter_a_ssms()
        # Exécuter la requête SQL pour obtenir le montant total
        cursor = conn.cursor()
        query = f"SELECT SUM(f.montant) FROM dbo.fait f JOIN dbo.[Dimension fournisseur] fournisseur ON f.FK_Fournisseur = fournisseur.Pk_fournisseur JOIN dbo.[Dimension_dates] date ON f.FK_Date = date.DateKey WHERE fournisseur.Fournisseur = ? AND MONTH(date.date) = ? AND YEAR(date.date) = ?"
        cursor.execute(query, (fournisseur, mois, année))
        total_amount = cursor.fetchone()[0]
        # Envoyer la réponse au dispatcher
        if total_amount:
            dispatcher.utter_message(f"Le montant total pour {fournisseur} pour le mois {mois} de l'année {année} est {total_amount}.")
        else:
            dispatcher.utter_message(f"Aucun montant trouvé pour {fournisseur} pour le mois {mois} de l'année {année}.")
        return []

# -----------------------------------------------------------------------------------------------------------------
import requests

class MontantParFournisseur(Action):
    def name(self) -> Text:
        return "Montant_Par_Fournisseur"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Votre code LLM
        last_input = tracker.events[-3].get("value")
        print('ll1 ', last_input)
        if type(last_input) == type(None):
            last_input = tracker.latest_message.get("text")
            print("here2")
        print('ll2 ', last_input)
        llm = InferenceClient(model='mistralai/Mixtral-8x7B-Instruct-v0.1', token='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')
        prompt = """<s>[INST] 
        context: Your task is to Extract only the supplier name and nothing else from the French text.
        the supplier name could contain letters, spaces, parenthesis, slashes.
        No additional information or instructions should be provided.
        Here are three examples first example: Donne moi details sur fournisseur  "ELECTROCNIC DESIGN SERVICE *EDS" output :  supplier name: ELECTROCNIC DESIGN SERVICE *EDS.
        Second example: consulter le fournisseur "GENERAL TRANSPORT INTERNATIONAL (GTI)" output :  supplier name: GENERAL TRANSPORT INTERNATIONAL (GTI).
        Third example: voir le montant fournisseur "LA PRECISION T.M.T" output :  supplier name: LA PRECISION T.M.T
        You need to do the output exactly like this don't add anything: supplier name:
        Here is the text you need to work on:"""
        # Combined system context and prompt with template
        prompt += last_input + """  [/INST]"""
        result = llm.text_generation(prompt, max_new_tokens=1000, temperature=0.1, top_p=0.95, top_k=50, )
        print(result)
        result = result.replace("supplier name: ", "").replace("Supplier name: ", "").rstrip('.')
        if result.startswith(" "):
            result = result[1:]
        print(result)

        if result:
            conn = se_connecter_a_ssms()  # Vous devez implémenter cette fonction
            if conn:
                # Requête SQL pour obtenir les montants correspondant à un fournisseur donné
                cursor = conn.cursor()
                query = """SELECT Fournisseur.Fournisseur, f.Montant, facture.etat , facture.Facture
                            FROM dbo.Fait f 
                            JOIN dbo.[Dimensions facture] facture ON f.FK_facture = facture.PK_facture
                            JOIN dbo.[Dimension Fournisseur] Fournisseur ON f.FK_Fournisseur = Fournisseur.Pk_Fournisseur
                            WHERE Fournisseur.Fournisseur = ?"""
                # Exécuter la requête SQL avec le fournisseur en tant que paramètre sécurisé
                cursor.execute(query, (result,))
                results = cursor.fetchall()

                total_montant = 0  # Initialise le montant total

                if results:
                    for result in results:
                        # Récupérer les détails de chaque facture
                        fournisseur, montant, etat, facture = result
                        dispatcher.utter_message(
                            text=f"Le fournisseur {fournisseur} pour la facture {facture} a un montant de {montant} pour l'état {etat}."
                        )
                        total_montant += montant  # Ajoute le montant au total

                    # Affiche le montant total à la fin
                    dispatcher.utter_message(
                        text=f"Le montant total des factures pour le fournisseur {fournisseur} est de : {total_montant}.")

                    # Envoi des données du fournisseur à l'API Plotly
                    response = update_plotly_filter(fournisseur)
                    # if response:
                    #     dispatcher.utter_message(text="Données envoyées à l'API Plotly avec succès.")
                    # else:
                    #     dispatcher.utter_message(text="Erreur lors de l'envoi des données à l'API Plotly.")
                else:
                    # Aucun montant trouvé pour le fournisseur demandé
                    dispatcher.utter_message(
                        text=f"Aucun montant trouvé pour le fournisseur demandé pour {result} .")

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

# ----------------------------------------------------------------------------------------
class MontantParType(Action):
    def name(self) -> Text:
        return "Montant_Par_Type"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Connexion à la base de données (assurez-vous que "conn" est correctement défini)
        conn = se_connecter_a_ssms()

        # Récupérer le dernier input de l'utilisateur
        last_input = tracker.events[-3].get("value")
        if last_input is None:
            last_input = tracker.latest_message.get("text")

        # Appel du modèle LLM
        llm = InferenceClient(model='mistralai/Mixtral-8x7B-Instruct-v0.1', token='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')
        prompt = """<s>[INST] 
        context: Your task is to Extract only the type name and nothing else from the French text.
        the type name could contain letters, spaces, parenthesis, slashes.
        No additional information or instructions should be provided.
        Here are three examples first example: Donne moi le type  "Assurance/Consulting" output :  type name: Assurance/Consulting.
        Second example: Les details sur le type " des cartes et systèmes électroniques" output :  type name:  des cartes et systèmes électroniques.
        Third example: consulter type "vente different produit" output :  type name: vente different produit
        You need to do the output exactly like this don't add anything: type name:
        Here is the text you need to work on:"""
        prompt += last_input + """  [/INST]"""
        result = llm.text_generation(prompt, max_new_tokens=1000, temperature=0.1, top_p=0.95, top_k=50)

        # Extraction du type
        result = result.replace("type name: ", "").rstrip('.').strip()

        if result:
            if conn:
                cursor = conn.cursor()
                query = """SELECT Fournisseur.Fournisseur, f.Montant, Fournisseur.type, facture.Facture
                        FROM dbo.fait f 
                        JOIN dbo.[Dimension fournisseur] fournisseur ON f.FK_Fournisseur = fournisseur.Pk_fournisseur
                        JOIN dbo.[Dimensions facture] facture ON f.FK_facture = facture.PK_facture
                        WHERE Fournisseur.type = ?"""
                cursor.execute(query, (result,))
                results = cursor.fetchall()

                total_amount = 0  # Variable pour stocker le montant total

                if results:
                    fournisseurs = []  # Liste pour stocker les noms des fournisseurs
                    for row in results:
                        fournisseur, montant, type_fournisseur, facture = row
                        try:
                            montant = float(montant)  # S'assurer que le montant est un nombre
                        except ValueError:
                            dispatcher.utter_message(
                                text=f"Le montant pour la facture {facture} du fournisseur {fournisseur} n'est pas un nombre valide: {montant}."
                            )
                            continue

                        total_amount += montant  # Ajouter le montant à la somme totale
                        fournisseurs.append(fournisseur)  # Ajouter le nom du fournisseur à la liste
                        dispatcher.utter_message(
                            text=f"Le fournisseur {fournisseur} pour la facture {facture} a un montant de {montant} pour le type {type_fournisseur}."
                        )

                    # Afficher le montant total pour le type spécifié
                    dispatcher.utter_message(
                        text=f"Le montant total pour le type {result} est : {total_amount}."
                    )
                else:
                    # Aucun montant trouvé pour le type demandé
                    dispatcher.utter_message(text=f"Aucun montant trouvé pour le type demandé.")

        return []

# --------------------------------------------------------------------------------------------------------------------------------

class ActionGetFactureJusquauMois(Action):
    def name(self) -> Text:
        return "action_get_Facture_Jusquau_Mois"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_input = tracker.events[-3].get("value")
        llm = InferenceClient(model='mistralai/Mixtral-8x7B-Instruct-v0.1', token='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')

        prompt = f"""<s> [INST] Vous êtes un chatbot conçu pour detecter le mois dans une phrase souhaitée par l'utilisateur.
                        Votre réponse doit être le numéro du mois seulement, sans ajout d'informations supplémentaires.
                        Exemple:
                        Input: "je veux avoir le montant total pour mois mars 2022"
                        Output: 03
                        Voici les message duquel tu dois extraire le nombre: """ + user_input + "[/INST]"
        mois = llm.text_generation(prompt, max_new_tokens=100, temperature=0.1, top_p=0.95, top_k=50)
        mois = mois.replace("Output: ", '').strip()
        print("Mois :", mois)

        prompt = f"""<s> [INST] Vous êtes un chatbot conçu pour detecter l'année dans une phrase souhaitée par l'utilisateur.
                        Votre réponse doit être le numéro de l'année seulement, sans ajout d'informations supplémentaires.
                        Si l'utilisateur n'a pas fourni d'année donne moi en output None
                        Exemple:
                        Input: "je veux avoir le montant total pour le fournisseur AIRCO en mars 2022"
                        Output: 2022
                        Input: "je veux avoir le montant total pour le fournisseur AIRCO en mars"
                        Output: None
                        Voici les message duquel tu dois extraire le nombre: """ + user_input + "[/INST]"
        année = llm.text_generation(prompt, max_new_tokens=100, temperature=0.1, top_p=0.95, top_k=50)
        année = année.replace("Output: ", '').strip()
        print("Année :", année)
        if ('None' in année):
            année=2023
        mois = int(mois)
        année = int (année)
        if (année<=2023):
            conn = se_connecter_a_ssms()
            cursor = conn.cursor()
            cursor.execute("SELECT SUM(f.montant) FROM dbo.fait f JOIN dbo.[Dimension_dates] date ON f.FK_Date = date.DateKey WHERE YEAR(date.date) = ? AND MONTH(date.date) <= ? ", (année, mois,))
            total_montant = cursor.fetchone()[0]

            if total_montant:
                dispatcher.utter_message(f"Le montant total des factures jusqu'au mois  {mois} de l'année {année} est de {total_montant}.")
            else:
                dispatcher.utter_message(f"Aucune donnée disponible jusqu'au mois  {mois} de l'année {année}.")
        else:
            conn = se_connecter_a_ssms()
            cursor = conn.cursor()
            cursor.execute("SELECT SUM(f.montant) FROM dbo.fait f JOIN dbo.[Dimension_dates] date ON f.FK_Date = date.DateKey")
            total_montant = cursor.fetchone()[0]

            if total_montant:
                dispatcher.utter_message(f"Le montant total des factures jusqu'au mois  {mois} de l'année {année} est de {total_montant}.")
            else:
                dispatcher.utter_message(f"Aucune donnée disponible jusqu'au mois  {mois} de l'année {année}.")

        return []
# -------------------------------------------------------------------------------------------------------------------------

class ActionGetFactureParMois(Action):
    def name(self) -> Text:
        return "action_get_Facture_mois"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:



        user_input = tracker.events[-3].get("value")

        llm = InferenceClient(model='mistralai/Mixtral-8x7B-Instruct-v0.1', token='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')
        prompt = f"""<s> [INST] Vous êtes un chatbot conçu pour detecter le mois dans une phrase souhaitée par l'utilisateur.
                        Votre réponse doit être le numéro du mois seulement, sans ajout d'informations supplémentaires.
                        Exemple:
                        Input: "je veux avoir le montant total pour mois mars 2022"
                        Output: 03
                        Voici les message duquel tu dois extraire le nombre: """ + user_input + "[/INST]"
        mois = llm.text_generation(prompt, max_new_tokens=100, temperature=0.1, top_p=0.95, top_k=50)
        mois = mois.replace("Output: ", '').strip()
        print("Mois :", mois)

        prompt = f"""<s> [INST] Vous êtes un chatbot conçu pour detecter l'année dans une phrase souhaitée par l'utilisateur.
                        Votre réponse doit être le numéro de l'année seulement, sans ajout d'informations supplémentaires.
                        Si l'utilisateur n'a pas fourni d'année donne moi en output None.
                        Exemple:
                        Input: "je veux avoir le montant total pour le fournisseur AIRCO en mars 2022"
                        Output: 2022
                        Input: "total des achats pour le mois juin"
                        Output: None
                        Voici les message duquel tu dois extraire le nombre: """ + user_input + "[/INST]"
        année = llm.text_generation(prompt, max_new_tokens=100, temperature=0.1, top_p=0.95, top_k=50)
        année = année.replace("Output: ", '').strip()
        mois = int(mois)
        print("Année :", année)
        if ('None' in année):
            conn = se_connecter_a_ssms()
            cursor = conn.cursor()
            cursor.execute("SELECT SUM(f.montant) FROM dbo.fait f JOIN dbo.[Dimension_dates] date ON f.FK_Date = date.DateKey WHERE MONTH(date) = ?", (mois,))
            total_montant = cursor.fetchone()[0]
            if total_montant:
                dispatcher.utter_message(f"Le montant total des factures pour les mois {mois} est {total_montant}.")
        
        else:
            année = int (année)
            conn = se_connecter_a_ssms()
            cursor = conn.cursor()
            cursor.execute("SELECT SUM(f.montant) FROM dbo.fait f JOIN dbo.[Dimension_dates] date ON f.FK_Date = date.DateKey WHERE MONTH(date) = ? AND YEAR(date.date) = ?", (mois, année,))
            total_montant = cursor.fetchone()[0]
            if total_montant:
                dispatcher.utter_message(f"Le montant total des factures pour le mois de {mois} de l'année {année} est {total_montant}.")

        return []
# --------------------------------------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------------------------------------

class ActionObtenirFactureMontant(Action):
    def name(self) -> Text:
        return "action_obtenir_Facture_montant"
    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:

        # Récupérer l'input complet de l'utilisateur
        last_input=tracker.events[-3].get("value")
        print('ll1 ',last_input)
        if type(last_input) == type(None):
            last_input=tracker.latest_message.get("text")
            print("here2")
        print('ll2 ',last_input)
        llm = InferenceClient(model = 'mistralai/Mixtral-8x7B-Instruct-v0.1', token = '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')
        prompt = """<s>[INST] 
        context: Your task is to Extract only the Invoice name and nothing else from the French text.
        the Invoice name could contain numbers, letters, spaces, parenthesis, slashes.
        No additional information or instructions should be provided.
        Here are four examples first example: Donne moi la facture  "FT/00748/2022 3/1" output :  Invoice name: FT/00748/2022 3/1.
        Second example: Les details sur la facture "36/2022 (2/2)" output :  Invoice name: 36/2022 (2/2).
        Third example: consulter facture "-1" output :  Invoice name: -1
        fourth example: voir facture "ME/17/8576 1/3" output :  Invoice name: ME/17/8576 1/3
        You need to do the output exactly like this don't add anything: Invoice name:
        Here is the text you need to work on:"""
        prompt +=   last_input+"""  [/INST]"""
        result = llm.text_generation(prompt,max_new_tokens=1000,temperature=0.1,top_p=0.95,top_k=50,)
        print(result)
        result = result.replace("Invoice name: ", "").rstrip('.')
        if result.startswith(" "):
            result = result[1:]
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

# ------------------------------------------------------------------------------------------------------

class LLMGeneral(Action):
    def name(self) -> Text:
        return "action_llm_general"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Récupérer l'input complet de l'utilisateur
        # last_input = tracker.get_slot("last_user_message")
        last_input=tracker.events[-3].get("value")
        # Initialize your LLM inference client
        llm = InferenceClient(model='mistralai/Mixtral-8x7B-Instruct-v0.1', token='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')
        # Get user input
        prompt = """<s> [INST] Vous êtes un chatbot qui sympathique et compétent en finances capable de répondre à une variété de questions en finances ou autres sujets. 
        Répondez aux questions en français et des faits intéressants et pertinents. 
        Voici la question a répondre: """ + last_input +"""  [/INST]"""
        # Generate response from LLM
        result = llm.text_generation(prompt, max_new_tokens=1000, temperature=0.7, top_p=0.7, top_k=50)
        
        # Send the LLM response to the user
        dispatcher.utter_message(result)

        return []

# --------------------------------------------------------------------------------------------------------------------


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
        return [SlotSet("last_user_message", user_input), UserUtteranceReverted(), FollowupAction("first_action")]

# -----------------------------------------------------------------------------------------------------------------

 
