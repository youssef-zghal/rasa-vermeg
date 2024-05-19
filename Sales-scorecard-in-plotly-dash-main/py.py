from langchain_community.llms import GPT4All

# try:
#     # Charger le modèle avec les paramètres personnalisés
#     llm = GPT4All(
#         model="C:/Users/ADMIN/AppData/Local/nomic.ai/GPT4All/mistral-7b-instruct-v0.1.Q4_0.gguf",
#         max_tokens=500,  # Réduisez ce nombre pour obtenir des réponses plus courtes
#         n_batch=15,  # Vous pouvez ajuster ce nombre selon vos besoins
#         temp=0.9,  # Réduisez cette valeur pour des réponses plus déterministes
#         top_k=10,  # Augmentez ce nombre pour des réponses plus déterministes
#         top_p=0.8  # Réduisez cette valeur pour des réponses plus déterministes
#     )

#     # Définir le contexte système
# # Corrected examples with proper invoice names
#     few_shot_examples = [
#     "<s>[INST]Input: facture NOTE D\'HONORAIRES MOIS DECEMBRE 2022 [/INST] Output: NOTE D\'HONORAIRES MOIS DECEMBRE 2022 </s> ",
#     "<s>[INST]Input: donne moi facture num ME/18/0345 2/2[/INST] Output: ME/18/0345 2/2 </s>",
#     "<s>[INST]Input: details sur la facture FVG013600 (2/2)[/INST] Output: FVG013600 (2/2) </s>",  # Corrected output
#     "<s>[INST]Input: que contient la facture MB-23+FVGS000487 [/INST]Output: MB-23+FVGS000487 </s>",
# ]

# # Combined system context and prompt with template
#     prompt = """[INST]You are an invoice name extractor who understands french and invoice names can include parenthesis, slashes and spaces and they are always in uppercase.
#             \nDon't add any notes just extract invoice name and nothing else\n 
#             Here are some examples to help you understand the format: \n [/INST]"""

#     for example in few_shot_examples:
#         prompt += f"{example}\n"

#     prompt += """[INST]Input: donne moi les details de la facture 04/2022 du 01/12/2022 [/INST]"""

# # Call the llm.invoke method with formatted string
#     response = llm.invoke(prompt)

#     # Afficher la réponse
#     print(response)

# except Exception as e:
#     # Gérer les exceptions et afficher un message approprié
#     print("Une erreur s'est produite:", e)


# from langchain_community.llms import GPT4All

# try:
#     # Charger le modèle avec les paramètres personnalisés
#     llm = GPT4All(
#         model="C:/Users/ADMIN/AppData/Local/nomic.ai/GPT4All/Nous-Hermes-2-Mistral-7B-DPO.Q4_0.gguf",
#         max_tokens=80,  # Réduisez ce nombre pour obtenir des réponses plus courtes
#         n_batch=15,  # Vous pouvez ajuster ce nombre selon vos besoins
#         temp=0.1,  # Réduisez cette valeur pour des réponses plus déterministes
#         top_k=30,  # Augmentez ce nombre pour des réponses plus déterministes
#         top_p=0.8  # Réduisez cette valeur pour des réponses plus déterministes
#     )

#     # Définir le contexte système
# # Corrected examples with proper invoice names
#     few_shot_examples = [
#     "Input: facture NOTE D\'HONORAIRES MOIS DECEMBRE 2022 Output: NOTE D\'HONORAIRES MOIS DECEMBRE 2022",
#     "Input: donne moi facture num ME/18/0345 2/2 Output: ME/18/0345 2/2",
#     "Input: details sur la facture FVG013600 (2/2) Output: FVG013600 (2/2)",  # Corrected output
#     "Input: que contient la facture MB-23+FVGS000487 Output: MB-23+FVGS000487",
# ]

# # Combined system context and prompt with template
#     prompt = """You are an invoice name extractor who understands french and invoice names can include parenthesis, slashes and spaces and they are always in uppercase.
#             \nDon't add any notes just extract invoice name and nothing else\n 
#             Here are some examples to help you understand the format: \n"""

#     for example in few_shot_examples:
#         prompt += f"{example}\n"

#     prompt += """Input: donne moi les details de la facture \nOutput:"""

# # Call the llm.invoke method with formatted string
#     response = llm.invoke(prompt)

#     # Afficher la réponse
#     print(response)

# except Exception as e:
#     # Gérer les exceptions et afficher un message approprié
#     print("Une erreur s'est produite:", e)


# from langchain_community.llms import GPT4All

# try:
#     # Charger le modèle avec les paramètres personnalisés
#     llm = GPT4All(
#         model="C:/Users/ADMIN/AppData/Local/nomic.ai/GPT4All/Nous-Hermes-2-Mistral-7B-DPO.Q4_0.gguf",
#         max_tokens=30,  # Réduisez ce nombre pour obtenir des réponses plus courtes
#         n_batch=15,  # Vous pouvez ajuster ce nombre selon vos besoins
#         temp=0.5,  # Réduisez cette valeur pour des réponses plus déterministes
#         top_k=10,  # Augmentez ce nombre pour des réponses plus déterministes
#         top_p=0.8  # Réduisez cette valeur pour des réponses plus déterministes
#     )

    # # Appeler la méthode invoke avec le prompt et le contexte système
    # response = llm.invoke("""Classify the user's input to the right intent either top5Supplier or top5Types\n
    #                       take care that the user's input is in french\n
    #                       answer just by giving the right intent and nothing else\n
    #                       Input: les top 3 fournisseur qu'on a fait des achats avec eux?""")


#     # Afficher la réponse
#     print(response)

# except Exception as e:
#     # Gérer les exceptions et afficher un message approprié
#     print("Une erreur s'est produite:", e)





# from langchain_community.llms import GPT4All

# try:
#     # Charger le modèle avec les paramètres personnalisés
#     llm = GPT4All(
#         model="C:/Users/ADMIN/AppData/Local/nomic.ai/GPT4All/Nous-Hermes-2-Mistral-7B-DPO.Q4_0.gguf",
#         max_tokens=10,  # Augmenter le nombre de tokens pour des réponses plus détaillées
#         n_batch=10,
#         temp=0.3,  # Ajuster la température selon vos besoins
#         top_k=10,  # Ajuster top_k pour la diversité des réponses
#         top_p=0.5  # Ajuster top_p pour la diversité des réponses
#     )

#     # Appeler la méthode invoke avec le prompt et le contexte système
#     response = llm.invoke("""Please provide information about Football \n
#                           Don't translate in English.
#                           take care that the user's input is in french\n
#                           Input: tu connais le joueur messi?""")
    
#     answer_start = response.find("Output: ")+7
#     answer_end = len(response) - 1  # Assuming the answer ends with a newline
#     answer = response[answer_start:answer_end].strip()

#     # Afficher la réponse
#     print(response)

# except Exception as e:
#     # Gérer les exceptions et afficher un message approprié
#     print("Une erreur s'est produite:", e)

# from langchain_community.llms import GPT4All

# try:
#   # Model parameters (adjust as needed)
#   max_tokens = 200  # Increase for more detailed responses
#   n_batch = 10
#   temp = 0.8  # Controls creativity (lower = more conservative)
#   top_k = 10  # Controls diversity of responses (higher = more diverse)
#   top_p = 0.5  # Controls diversity of responses (higher = more diverse)

#   # Load the model
#   llm = GPT4All(
#       model="C:/Users/ADMIN/AppData/Local/nomic.ai/GPT4All/Nous-Hermes-2-Mistral-7B-DPO.Q4_0.gguf",
#       max_tokens=max_tokens,
#       n_batch=n_batch,
#       temp=temp,
#       top_k=top_k,
#       top_p=top_p
#   )

#   # Define prompt with clear instructions and separate input
#   prompt = """<s>[INST] You are a large language model trained for financial tasks. Your name is InvoiceBot and you are designed to provide concise and polite responses in French. Provide brief responses to user queries related to finance. [/INST]</s>"""
#   prompt += "Input: bonjour c'est qui la meilleure firme de consulting au monde et qui sont les BIG four"  # User input as separate prompt

#   # Call the model with the prompt and extract the answer
#   response = llm.invoke(prompt)
#   answer_start = response.find("Output: ") + 7
#   answer_end = len(response) - 1
#   answer = response[answer_start:answer_end].strip()

#   # Print the response
#   print(answer)

# except Exception as e:
#   # Handle specific exceptions (e.g., ConnectionError, TimeoutError)
#   print(f"An error occurred: {e}")

# llm = GPT4All(
#         model="C:/Users/ADMIN/AppData/Local/nomic.ai/GPT4All/mistral-7b-instruct-v0.1.Q4_0.gguf",
#         max_tokens=10,  # Réduisez ce nombre pour obtenir des réponses plus courtes
#         n_batch=50,  # Vous pouvez ajuster ce nombre selon vos besoins
#         temp=0.1,  # Réduisez cette valeur pour des réponses plus déterministes
#         top_k=50,  # Augmentez ce nombre pour des réponses plus déterministes
#         top_p=0.95,
#         )
# prompt = """<s>[INST] 
#         context: Your task is to Extract only the Invoice name and nothing else from the French text.
#         the Invoice name could contain numbers, letters, spaces, parenthesis, slashes.
#         No additional information or instructions should be provided.
#         Here are two examples first example: Donne moi la facture  "FT/00748/2022 3/1" output :  Invoice name: FT/00748/2022 3/1.
#         Second example: Les details sur la facture "36/2022 (2/2)" output :  Invoice name: 36/2022 (2/2)
#         You need to do the output exactly like this don't add anything: Invoice name:
#         Here is the text you need to work on:"""
#         # Combined system context and prompt with template
# prompt +=   """ les details sur la facture 'MB-23+FVGS000487 [/INST]"""
# response = llm.invoke(prompt)
# print(response)

