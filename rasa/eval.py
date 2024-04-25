import pickle
from rasa.model_training import train
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import numpy as np
import yaml

# Charger le fichier YAML contenant les données NLU
with open("data/nlu.yml", "r") as file:
    nlu_data = yaml.safe_load(file)

# Extraire les données d'intention et les exemples
data = []
labels = []
for item in nlu_data['nlu']:
    intent = item['intent']
    examples = item['examples']
    for example in examples:
        data.append(example)
        labels.append(intent)

# Diviser les données en ensembles d'entraînement et de test
X_train, X_test, y_train, y_test = train_test_split(data, labels, test_size=0.2, random_state=42)

# Définir une plage de valeurs pour le nombre d'epochs
epochs_values = [110, 115, 120, 125, 130, 135, 140]

best_accuracy = 0
best_epochs = None

for epochs in epochs_values:
    # Entraîner le modèle avec cette valeur d'epochs
    model_output_path = f"models/model_epochs_{epochs}"
    train(config="config.yml", domain="domain.yml", training_files="data/", output=model_output_path, 
          fixed_model_name="model")

    # Charger le modèle entraîné
    model_path = f"{model_output_path}/nlu"
    with open(model_path, "rb") as file:
        interpreter = pickle.load(file)

    # Faire des prédictions sur l'ensemble de test
    predictions = [interpreter.parse(text)["intent"]["name"] for text in X_test]

    # Calculer l'exactitude des prédictions
    accuracy = accuracy_score(y_test, predictions)

    # Mettre à jour la meilleure exactitude et le meilleur nombre d'epochs si nécessaire
    if accuracy > best_accuracy:
        best_accuracy = accuracy
        best_epochs = epochs

print("Meilleur nombre d'epochs:", best_epochs)
print("Meilleure exactitude:", best_accuracy)
