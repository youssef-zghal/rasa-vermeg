# import torch
# from transformers import AutoTokenizer, AutoModelForCausalLM
# from transformers import TrainingArguments, Trainer
# from datasets import Dataset
# import pandas as pd

# # Charger votre ensemble de données à partir du fichier Excel
# dataset = pd.read_excel("intents_and_examples.xlsx")

# # Renommer les colonnes si nécessaire
# dataset = dataset.rename(columns={"Intent": "label", "Exemples": "text"})

# # Créer un objet Dataset à partir de votre DataFrame
# dataset = Dataset.from_pandas(dataset)

# # Charger le tokenizer associé à votre modèle
# tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-Instruct-v0.2", token = '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')

# # Définir le jeton de fin de séquence comme jeton de padding
# tokenizer.pad_token = tokenizer.eos_token

# # Fonction de tokenization pour votre ensemble de données
# def tokenize_function(examples):
#     return tokenizer(examples["text"], padding=True, truncation=True)

# # Appliquer la tokenization à votre ensemble de données
# tokenized_dataset = dataset.map(tokenize_function, batched=True)

# # Charger votre modèle LLM
# model = AutoModelForCausalLM.from_pretrained("mistralai/Mistral-7B-Instruct-v0.2",token = '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')

# # Spécifier les paramètres d'entraînement
# training_args = TrainingArguments(
#     per_device_train_batch_size=4,
#     num_train_epochs=3,
#     logging_dir='./logs',
# )

# # Initialiser le Trainer
# trainer = Trainer(
#     model=model,
#     args=training_args,
#     train_dataset=tokenized_dataset["train"],
# )

# # Entraîner le modèle
# trainer.train()

# # Sauvegarder le modèle finetuné
# model.save_pretrained("modele_finetune")


# Assurez-vous d'avoir téléchargé les mots vides pour nltk
import pandas as pd
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# Charger le jeu de données à partir du fichier Excel
dataset = pd.read_excel("/Users/ADMIN/Desktop/STAGE VERMEG/Rasa/rasa-vermeg/rasa/data/intents_and_examples.xlsx")

# Initialiser un ensemble de mots vides
stop_words = set(stopwords.words('french')) 

# Initialiser un dictionnaire pour stocker les exemples par intention
intent_examples = {}

# Parcourir chaque ligne du jeu de données
for intent, example in zip(dataset['Intent'], dataset['Exemples']):
    # Tokenization de l'exemple et suppression des mots vides
    tokens = word_tokenize(example.lower())  
    tokens = {token for token in tokens if token.isalnum() and token not in stop_words}  
    # Vérifier si l'intention existe déjà dans le dictionnaire
    if intent in intent_examples:
        # Mettre à jour les exemples existants
        intent_examples[intent].update(tokens)
    else:
        # Ajouter de nouveaux exemples
        intent_examples[intent] = tokens

# Afficher les résultats
for intent, examples in intent_examples.items():
    print(f"Intent: ")
    print(intent, examples)
    print()

