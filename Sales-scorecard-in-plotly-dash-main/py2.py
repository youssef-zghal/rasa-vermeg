from huggingface_hub import InferenceClient



# chaine = "Ceci est une chaîne de caractères à analyser"

# liste_de_mots1 = ["reference","montant","egal","inferieur","superieur","fournisseur","achat","total","etat","cree","facture","pret pour paiement","valide","type","mois","annee","jusquau"]

# liste_de_mots2 = ["nombre","fournisseur","combien","mois","par","annee","consulter","voir","details","montant","total","type","facture"]

# liste_de_mots3 = ["top","meuilleur","type","plus","fournisseur","moins"]

# liste_de_mots4 = ["montant","total","achat","mois","annee","facture","valide","pret pour paiement","cree","fournisseur"]

# liste_de_mots5 = ["consulter","details","facture","montant","voir","type"]

# # Chaîne dans laquelle vous voulez vérifier la présence du mot

# # Diviser la chaîne en mots en utilisant l'espace comme séparateur
# mots_dans_la_chaine = chaine.split()

# # Vérifier si un mot de la liste se trouve dans la chaîne
# for mot in mots_dans_la_chaine:
#     if mot in liste_de_mots1:
#         print(f"Le mot '{mot}' se trouve dans la liste de mots1.")
# for mot in mots_dans_la_chaine:
#     if mot in liste_de_mots2:
#         print(f"Le mot '{mot}' se trouve dans la liste de mots2.")
# for mot in mots_dans_la_chaine:
#     if mot in liste_de_mots3:
#         print(f"Le mot '{mot}' se trouve dans la liste de mots3.")
# for mot in mots_dans_la_chaine:
#     if mot in liste_de_mots4:
#         print(f"Le mot '{mot}' se trouve dans la liste de mots4.")
# for mot in mots_dans_la_chaine:
#     if mot in liste_de_mots5:
#         print(f"Le mot '{mot}' se trouve dans la liste de mots5.")


# salutation =['bonne', 'allo', 'invoicebot', 'toi', 'hey', 'coucou', 'faire', 'es', 'alo', 'ce', 'qui', 'sais', 'roule', 'tu', 'à', 'cc', 'bjr', 'journee', 'slt', 'salutations', 'comment', 'cava', 'bonj', 'salut', 'que', 'bonjour', 'bonsoir']

# bye =['de', 'bonne', 'à', 'la', 'soin', 'tard', 'au', 'prenez', 'journee', 'prochaine', 'revoir', 'soiree', 'plus', 'toute', 'vous', 'bye', 'nuit']

# connaitre_montant_a_partir_reference= ['payer', 'faut', 'montant', 'total', 'combien', 'qui', 'la', 'une', '7559854598', '2365894561', '9874562159', 'facture', 'pour', 'il', 'cette', 'reference', 'coût', 'number']

# Montant_superieur= ['superieur', 'excedant', 'un', 'avec', 'montant', 'quels', 'les', 'montants', 'qui', 'paiements', 'des', '15233853548', '7559854598', '39490', 'à', 'paiement', 'factures', 'achats', 'sup', 'sont', 'number']

# Montant_inferieur= ['de', '2939223', 'est', 'dessous', 'un', 'cout', 'avec', 'montant', 'inf', '100', 'le', 'les', 'moins', 'paiements', 'quel', 'inferieur', '37779555', '7559854598', '39490', 'à', 'depenses', 'factures', 'achats', 'eleve', 'en', 'que', 'inferieurs', 'number']

# Montant_egal= ['recentes', 'de', 'est', 'egal', 'un', 'avec', 'montant', '49420', 'dans', 'le', 'les', 'paiements', 'quel', '0', '7559854598', '39490', 'transactions', 'à', 'exact', 'factures', 'achats', 'quelles', 'egaux', 'identique', 'sont', 'number']

# Montant_total_fournisseur= ['est', 'total', 'montant', 'creances', 'le', 'les', 'montants', 'nos', 'sommes', 'quel', 'des', 'dus', 'nous', 'achat', 'à', 'pour', 'fournisseur', 'fournisseurs', 'global', 'par', 'dues', 'chiffre', 'tous', 'devons', 'que', 'du']

# montant_total_etats =['chaque', 'de', 'voir', 'veux', 'est', 'attribues', 'total', 'montant', 'le', 'les', 'quelle', 'montants', 'quel', 'des', 'etats', 'etat', 'je', 'à', 'situation', 'pour', 'sont', 'financière']

# montant_etat_valide= ['validees', 'total', 'montant', 'quels', 'quelle', 'les', 'le', 'montants', 'valide', 'paiements', 'valides', 'etat', 'pour', 'payee', 'factures', 'sont']

# montant_etat_cree= ['crees', 'etat', 'facture', 'total', 'ajoute', 'montant', 'cree', 'factures', 'ont', 'quels', 'quelle', 'les', 'quelles', 'montants', 'ete', 'sont']

# montant_etat_prêt_pour_paiement= ['prete', 'non', 'total', 'quels', 'montant', 'quelle', 'les', 'le', 'montants', 'qui', 'paiements', 'pret', 'payes', 'etats', 'etat', 'facture', 'pour', 'paiement', 'ne', 'payee', 'factures', 'pas', 'prets', 'sont']

# montant_total_type =['chaque', 'type', 'attribues', 'total', 'montant', 'les', 'montants', 'nos', 'des', 'achat', 'à', 'pour', 'types', 'categorie', 'paiement', 'secteurs', 'par', 'liste', 'tous']

# nombre_fournisseur =['de', 'nombre', 'exact', 'donnees', 'total', 'notre', 'fournisseurs', 'dans', 'le', 'combien', 'base', 'enregistres']

# nombre_fournisseur_par_mois= ['de', 'mois', 'nombre', 'pour', 'fournisseur', 'nb', 'avril', 'par', 'mars', 'le', 'month', 'combien']

# nombre_fournisseur_par_annee= ['de', 'nombre', 'pour', 'fournisseur', '2022', '2023', 'nb', 'annee', 'par', 'combien']

# nombre_type =['de', 'nombre', 'donnees', 'types', 'total', 'secteurs', 'notre', 'dans', 'combien', 'base', 'enregistres']

# nombre_facture= ['de', 'nombre', 'donnees', 'facture', 'factures', 'dans', 'combien', 'base', 'la']

# nombre_facture_par_mois= ['de', 'mois', 'nombre', 'facture', 'pour', 'fevrier', 'nb', 'par', 'month', 'combien', 'janvier']

# nombre_facture_par_annee= ['chaque', 'de', 'nombre', 'facture', 'pour', '2022', '2023', 'nb', 'par', 'annee', 'combien']

# demande_top_fournisseurs =['10', '2', '8', 'premiers', 'montant', 'quels', 'avec', 'en', 'meilleurs', 'le', 'les', 'effectue', '13', 'qui', 'eux', 'avons', 'nous', 'principaux', 'fournisseur', 'fournisseurs', 'par', '20', 'top', 'plus', 'travail', 'sont', 'number']

# demande_top_Type= ['de', 'travaille', 'type', '4', 'secteur', 'avec', 'montant', 'quels', '9', '5', 'le', 'les', 'montants', 'principaux', '12', '1', 'fournisseur', 'secteurs', 'grand', 'meilleur', 'top', 'plus', 'eleves', 'number']

# demande_Less_fournisseurs =['de', 'bas', '2', 'avec', 'quels', 'importants', 'moins', 'les', 'combien', 'montants', 'qui', 'fournisseurs', 'plus', 'significatifs', 'sont', 'number']

# obtenir_montant_total_facture =['de', 'est', 'toutes', 'total', 'montant', 'pour', 'factures', 'au', 'mes', 'le', 'les', 'combien', 'paiements', 'quel', 'des']

# achats_total_mois_annees= ['de', 'novembre', 'total', 'montant', '2022', '2023', 'fevrier', 'le', 'mai', 'septembre', 'achat', 'depenses', 'aout', 'juin', 'est', 'fournir', 'month', 'les', 'montants', 'quel', 'janvier', 'des', 'entity', '2025', 'mois', 'donner', 'pour', 'juillet', 'factures', 'annee', 'octobre', '2024']

# obtenir_montant_total_par_annees= ['est', 'vue', '2021', 'total', 'cumule', 'montant', '2023', '2022', 'le', 'les', 'quel', 'des', 'une', 'donner', '2026', 'pour', 'factures', 'annee', 'et', 'achats', '2024', 'financière']

# montant_total_entre_deux_mois_pour_une_annee =['de', 'novembre', 'total', '2022', 'montant', 'quels', '2023', 'le', 'mai', 'combien', 'septembre', 'achat', 'depenses', 'monthf', 'monthd', 'aout', 'juin', 'sont', 'depense', 'est', '2021', 'mars', 'les', 'montants', 'quel', 'janvier', 'des', 'juillet', 'factures', 'decembre', 'avril', 'annee', 'et', 'en', 'entre']

# montant_total_Jusquau_mois_annee= ['de', 'novembre', 'total', 'montant', '2022', '2023', 'quels', 'fevrier', 'le', 'combien', 'septembre', 'depenses', 'sont', 'juin', 'depense', 'est', 'present', 'fournir', 'month', 'les', 'quel', 'entity', 'des', 'mois', 'à', 'pour', 'coûts', 'cumules', 'juillet', 'factures', 'decembre', 'accumulees', 'annee', 'achats', 'quelles', 'jusquau', 'octobre', '2024', 'jusqu']

# afficher_montants_des_factures_etat_valides_par_mois_annee= ['total', 'fevrier', '2022', 'quels', 'validees', '2023', 'montant', 'le', 'mai', 'valide', 'valides', 'septembre', 'depenses', 'facture', 'payee', 'sont', 'est', 'mars', 'month', 'les', 'montants', 'quel', 'des', 'mois', 'montrer', 'pour', 'factures', 'avril', 'annee', 'quelles', 'en', '2024']

# afficher_montants_des_factures_etat_cree_par_mois_annee= ['de', 'total', 'fevrier', 'montant', '2023', 'quels', '2022', 'le', 'mai', 'combien', 'crees', 'sont', 'depense', 'est', 'cree', 'mars', 'month', 'les', 'montants', 'quel', 'janvier', 'des', 'mois', 'pour', 'factures', 'decembre', 'avril', 'annee', 'facturs', 'en', '2027']

# afficher_montants_des_factures_etat_prets_pour_paiement_par_mois_annee= ['total', '2022', 'montant', 'quels', '2023', 'fevrier', 'non', '2029', 'le', 'dettes', 'avons', 'septembre', 'depenses', 'facture', 'ne', 'payee', 'pas', 'aout', 'sont', 'juin', 'prêts', 'prêtes', 'month', 'les', 'montants', 'qui', 'pret', 'des', 'janvier', 'nous', 'mois', 'montrer', 'pour', 'paiement', 'juillet', 'factures', 'decembre', 'annee', 'quelles', 'en', 'octobre', 'que', '2024']

# demander_montant_total_entre_mois_annee_et_mois_annee= ['de', 'novembre', 'total', 'montant', '2022', '2023', 'fevrier', '2029', 'le', 'quelle', 'mai', 'combien', 'nos', 'la', 'septembre', 'achat', 'depenses', 'anneed', 'somme', 'monthf', '2030', 'monthd', 'aout', 'totalite', 'juin', 'sont', 'depense', 'anneef', 'est', '2021', 'les', 'montants', 'quel', 'janvier', 'des', 'mois', 'octobre', 'montrer', 'deux', 'pour', 'factures', 'decembre', 'avril', 'et', 'achats', 'quelles', 'entre', '2024']

# demande_details_sur_Facture= ['informations', 'consulter', 'voir', 'est', 'sur', 'fournir', 'le', 'les', 'quel', 'des', 'la', 'donner', 'facture', 'pour', 'fournisseur', 'fournisseurs', 'cette', 'quelles', 'fv230847']

# demande_montant_type= ['de', 'société', 'systèmes', 'type', 'montant', 'quels', 'sur', 'afficher', 'le', 'les', 'communication', 'voyage', 'electroniques', 'montants', 'des', 'details', 'avocat', 'une', 'donner', 'montrer', 'depenses', 'pour', 'automobile', 'idee', 'expertise', 'avoir', 'et', 'quelles', 'agence', 'cartes', 'sont', 'du']

# demande_montant_fournisseur =['station', 'consulter', 'de', 'chiffon', 'veux', 'design', 'total', 'montant', 'technique', 'sur', 'choucha', 'le', 'combien', 'international', 'tunisienne', 'sarl', 'general', 'fournisseur', 'cabinet', 'henda', 'spc', 'ben', 'edt', 'airco', 'depense', 'deloitte', 'est', 'electrocnic', 'carry', 'services', 'avec', 'gti', 'pneu', 'les', 'quel', 'cheikh', 'des', 'details', 'montrer', 'je', 'adhecom', 'pour', 'cash', 'eds', 'transport', 'service', 'et', 'achats', 'connaitre']

# demander_montant_total_fournisseur_mois_annee= ['chiffon', 'de', 'station', 'novembre', 'design', 'total', '2022', 'fevrier', '2023', 'montant', 'sur', 'technique', 'choucha', 'le', 'energy', 'mai', 'combien', 'international', 'tunisienne', 'sarl', 'diesel', 'septembre', 'general', 'depenses', 'fournisseur', 'maaden', 'spc', 'aout', 'edt', 'juin', 'jamel', 'airco', 'depense', 'est', '2021', 'electrocnic', 'services', 'al', 'avec', 'gti', 'decmbre', 'mars', 'pneu', 'month', 'les', 'montants', 'quel', 'des', 'details', 'darragi', 'mois', 'donner', 'adhecom', 'pour', '2028', 'juillet', 'eds', 'avril', 'annee', 'service', 'et', 'transport', 'achats', 'en', 'octobre']

# def comparer_mots(chaine, listes, noms_listes):
#     mots_chaine = chaine.split()  # Sépare la chaîne en mots

#     listes_communes = []

#     for i, liste in enumerate(listes):
#         liste_minuscule = [mot.lower() for mot in liste]
#         mots_communs = [mot for mot in mots_chaine if mot.lower() in liste_minuscule]
#         if mots_communs:
#             listes_communes.append(noms_listes[i])

#     return ', '.join(listes_communes)

# # Exemple d'utilisation
# chaine = "Le ciel est bleu et le soleil brille."
# listes = [salutation,bye,connaitre_montant_a_partir_reference,Montant_inferieur,Montant_egal,Montant_superieur,Montant_total_fournisseur,montant_total_etats,montant_etat_valide,montant_etat_cree,montant_etat_prêt_pour_paiement,montant_total_type,nombre_fournisseur,nombre_fournisseur_par_mois,nombre_fournisseur_par_annee,nombre_type,nombre_facture,nombre_facture_par_mois,nombre_facture_par_annee,demande_top_fournisseurs,demande_top_Type,demande_Less_fournisseurs,obtenir_montant_total_facture,achats_total_mois_annees,obtenir_montant_total_par_annees,montant_total_entre_deux_mois_pour_une_annee,montant_total_Jusquau_mois_annee,afficher_montants_des_factures_etat_valides_par_mois_annee,afficher_montants_des_factures_etat_cree_par_mois_annee,afficher_montants_des_factures_etat_prets_pour_paiement_par_mois_annee,demander_montant_total_entre_mois_annee_et_mois_annee,demande_details_sur_Facture,demande_montant_type,demande_montant_fournisseur,demander_montant_total_fournisseur_mois_annee,]
# noms_listes = ["salutation", "bye", "connaitre_montant_a_partir_reference", "Montant_superieur", "Montant_inferieur", "Montant_egal", "Montant_total_fournisseur", "montant_total_etats", "montant_etat_valide", "montant_etat_cree", "montant_etat_prêt_pour_paiement", "montant_total_type", "nombre_fournisseur", "nombre_fournisseur_par_mois", "nombre_fournisseur_par_annee", "nombre_type", "nombre_facture", "nombre_facture_par_mois", "nombre_facture_par_annee", "demande_top_fournisseurs", "demande_top_Type", "demande_Less_fournisseurs", "obtenir_montant_total_facture", "achats_total_mois_annees", "obtenir_montant_total_par_annees", "montant_total_entre_deux_mois_pour_une_annee", "montant_total_Jusquau_mois_annee", "afficher_montants_des_factures_etat_valides_par_mois_annee", "afficher_montants_des_factures_etat_cree_par_mois_annee", "afficher_montants_des_factures_etat_prets_pour_paiement_par_mois_annee", "demander_montant_total_entre_mois_annee_et_mois_annee", "demande_details_sur_Facture", "demande_montant_type", "demande_montant_fournisseur", "demander_montant_total_fournisseur_mois_annee"]

# resultat = comparer_mots(chaine, listes, noms_listes)

# print(resultat)



# listes = [salutation,bye,connaitre_montant_a_partir_reference,Montant_inferieur,Montant_egal,Montant_superieur,Montant_total_fournisseur,montant_total_etats,montant_etat_valide,montant_etat_cree,montant_etat_prêt_pour_paiement,montant_total_type,nombre_fournisseur,nombre_fournisseur_par_mois,nombre_fournisseur_par_annee,nombre_type,nombre_facture,nombre_facture_par_mois,nombre_facture_par_annee,demande_top_fournisseurs,demande_top_Type,demande_Less_fournisseurs,obtenir_montant_total_facture,achats_total_mois_annees,obtenir_montant_total_par_annees,montant_total_entre_deux_mois_pour_une_annee,montant_total_Jusquau_mois_annee,afficher_montants_des_factures_etat_valides_par_mois_annee,afficher_montants_des_factures_etat_cree_par_mois_annee,afficher_montants_des_factures_etat_prets_pour_paiement_par_mois_annee,demander_montant_total_entre_mois_annee_et_mois_annee,demande_details_sur_Facture,demande_montant_type,demande_montant_fournisseur,demander_montant_total_fournisseur_mois_annee,]

# intents = comparer_mots(text, listes, noms_listes)
# noms_listes = ["salutation", "bye", "connaitre_montant_a_partir_reference", "Montant_superieur", "Montant_inferieur", "Montant_egal", "Montant_total_fournisseur", "montant_total_etats", "montant_etat_valide", "montant_etat_cree", "montant_etat_prêt_pour_paiement", "montant_total_type", "nombre_fournisseur", "nombre_fournisseur_par_mois", "nombre_fournisseur_par_annee", "nombre_type", "nombre_facture", "nombre_facture_par_mois", "nombre_facture_par_annee", "demande_top_fournisseurs", "demande_top_Type", "demande_Less_fournisseurs", "obtenir_montant_total_facture", "achats_total_mois_annees", "obtenir_montant_total_par_annees", "montant_total_entre_deux_mois_pour_une_annee", "montant_total_Jusquau_mois_annee", "afficher_montants_des_factures_etat_valides_par_mois_annee", "afficher_montants_des_factures_etat_cree_par_mois_annee", "afficher_montants_des_factures_etat_prets_pour_paiement_par_mois_annee", "demander_montant_total_entre_mois_annee_et_mois_annee", "demande_details_sur_Facture", "demande_montant_type", "demande_montant_fournisseur", "demander_montant_total_fournisseur_mois_annee"]

# # print(intents)


# client = InferenceClient(model = 'mistralai/Mixtral-8x7B-Instruct-v0.1', token = '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')
# text= input()

# result = client.text_generation("""<s>[INST] 
# Vous êtes un système de classification d'intentions et tu dois être très précis. 
# Nous vous fournissons les intentions et leurs descriptions:
# Intent: salutation  
# Description: quand l'utilisateur demande un salut
# Intent: bye  
# Description: quand l'utilisateur demande l'au revoir
# Intent: connaitre_montant_a_partir_reference  
# Description: quand l'utilisateur demande le montant par référence de facture
# Intent: Montant_superieur  
# Description: quand l'utilisateur demande les montants des factures qui sont supérieurs à des montants donnés 
# Intent: Montant_inferieur  
# Description: quand l'utilisateur demande les montants des factures qui sont inférieurs à des montants donnés 
# Intent: Montant_egal  
# Description: quand l'utilisateur demande les montants des factures qui sont égaux à des montants donnés 
# Intent: Montant_total_fournisseur  
# Description: quand l'utilisateur demande le montant total de chaque fournisseur et le montant total de tous les fournisseurs
# Intent: montant_total_etats  
# Description: quand l'utilisateur demande le montant total des états, chaque état donne son montant total
# Intent: montant_etat_valide  
# Description: quand l'utilisateur demande à consulter le montant total pour les factures valides
# Intent: montant_etat_cree  
# Description: quand l'utilisateur demande à consulter le montant total pour les factures créées
# Intent: montant_etat_prêt_pour_paiement  
# Description: quand l'utilisateur demande à consulter le montant total pour les factures prêtes pour le paiement
# Intent: montant_total_type  
# Description: quand l'utilisateur demande le montant total de chaque type et le montant total de tous les types
# Intent: nombre_fournisseur  
# Description: quand l'utilisateur demande de connaître le nombre de fournisseurs dans la base de données 
# Intent: nombre_fournisseur_par_mois  
# Description: quand l'utilisateur demande de connaître le nombre de fournisseurs par mois, il affiche chaque mois combien de fournisseurs il y a et on peut aussi spécifier un mois
# Intent: nombre_fournisseur_par_annee  
# Description: quand l'utilisateur demande de connaître le nombre de fournisseurs par mois, il affiche chaque année combien de fournisseurs il y a et on peut aussi spécifier une année
# Intent: nombre_type  
# Description: quand l'utilisateur demande de connaître le nombre de types dans la base 
# Intent: nombre_facture  
# Description: quand l'utilisateur demande de connaître le nombre de factures dans la base 
# Intent: nombre_facture_par_mois  
# Description: quand l'utilisateur demande de connaître le nombre de factures par mois, il affiche chaque mois combien de factures il y a et on peut aussi spécifier un mois
# Intent: nombre_facture_par_annee  
# Description: quand l'utilisateur demande de connaître le nombre de factures par année, il affiche chaque année combien de factures il y a et on peut aussi spécifier une année
# Intent: demande_top_fournisseurs  
# Description: si l'utilisateur aurait besoin de savoir qui sont les n meilleurs fournisseurs
# Intent: demande_top_Type  
# Description: si l'utilisateur aurait besoin de savoir qui sont les n meilleurs types de fournisseurs
# Intent: demande_Less_fournisseurs  
# Description: si l'utilisateur aurait besoin de savoir qui sont les n moins fournisseurs existants dans la base
# Intent: obtenir_montant_total_facture  
# Description: pour savoir combien vaut le montant total de toutes les factures dans la base de données
# Intent: montant_total_mois_annees  
# Description: quand l'utilisateur demande le montant d'achat en indiquant le mois et pouvant indiquer l'année ou même ne pas l'indiquer 
# Intent: obtenir_montant_total_par_annees  
# Description: demander le montant total des achats par année en mentionnant une année ou plusieurs
# Intent: montant_total_entre_deux_mois_pour_une_annee  
# Description: lorsque l'utilisateur demande les montants entre un intervalle de mois pour une année donnée
# Intent: montant_total_Jusquau_mois_annee  
# Description: demander le montant total jusqu'à un mois et une année donnée ou même on peut ne pas fournir l'année
# Intent: afficher_montants_des_factures_etat_valides_par_mois_annee  
# Description: demande d'affichage des montants des factures qui ont un état validé pour un mois et une année donnés
# Intent: afficher_montants_des_factures_etat_cree_par_mois_annee  
# Description: demande d'affichage des montants des factures qui ont un état créé pour un mois et une année donnés
# Intent: afficher_montants_des_factures_etat_prets_pour_paiement_par_mois_annee  
# Description: demande d'affichage des montants des factures qui ont un état prêt pour le paiement pour un mois et une année donnés
# Intent: demander_montant_total_entre_mois_annee_et_mois_annee  
# Description: quand l'utilisateur demande les montants des factures figurant entre un intervalle en mentionnant le mois et l'année de début et le mois et l'année de fin
# Intent: demande_details_sur_Facture  
# Description: si l'utilisateur voudrait savoir les détails d'une facture donnée
# Intent: demande_montant_type  
# Description: quand l'utilisateur voudrait savoir les montants des factures pour un type de fournisseur donné
# Intent: demande_montant_fournisseur  
# Description: quand l'utilisateur voudrait savoir les montants des factures pour un fournisseur donné
# Intent: demander_montant_total_fournisseur_mois_annee  
# Description: demander les montants total des factures pour un mois et une année donnée
                                                            
#         Vous avez une expression et vous devez la classifier selon l'intention. 
#         Répondez uniquement avec l'intent. 
#         Si l'expression ne correspond à aucune des descriptions d'action, renvoyez "None".
#         Vous devez produire la sortie exactement comme suit, ne rien ajouter : L'intent est : .
#         Voici le message à classer: """ + text + """ [/INST]""",
#                         max_new_tokens=2048,
#                         # do_sample=True,
#                         temperature=0.1,
#                         # n_batch=50,
#                         top_p=0.95,
#                         top_k=50,
#                         # repetition_penalty=1.1
#                     )

# print(result.replace('\\', '').replace(" L'intent est :",'').strip())







# -------------------------------------------------------llm general----------------------------------------------------------------------------------------

# llm = InferenceClient(model='mistralai/Mixtral-8x7B-Instruct-v0.1', token='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')
# print("Bienvenue ! Posez votre question en français :")
# user_question = input()
# prompt = f"<s> [INST] Vous êtes un chatbot sympathique et compétent capable de répondre à une variété de questions. Répondez aux questions en français et des faits intéressants et pertinents. </s>{user_question} [/INST]"
# result = llm.text_generation(prompt, max_new_tokens=1300, temperature=0.7, top_p=0.7, top_k=50)
# print(result)

# --------------------------------------------------------------deux mois et deux annee-----------------------------------------------------------

# llm = InferenceClient(model='mistralai/Mistral-7B-Instruct-v0.2', token='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')
# prompt = """<s> [INST] You are a date interval extractor, your task is to parse French messages containing actions between two dates and output them in numeric format. 
# Your output should be structured as follows: month1,year1,month2,year2 and don't add anything else. 
# Here is an example: je veux avoir les factures entre juin 2025 ET juillet 2027 Output: 06,2025,07,2027.
# Here's the french message: consulter les achats des factures entre janvier 2022 et 01 2023[/INST]"""
# result = llm.text_generation(prompt, max_new_tokens=1300, temperature=0.1, top_p=0.7, top_k=50)
# print(result)

# ------------------------------------------------------par Mois et annee-------------------------------------------------------------------------------------

# llm = InferenceClient(model='mistralai/Mistral-7B-Instruct-v0.2', token='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')
# prompt = """<s> [INST] You are a date interval extractor, your task is to parse French messages containing actions between two dates and output them in numeric format. 
#                         Your output should be structured as follows: month,year and don't add anything else. 
#                         Here is an example: je veux avoir le montant total pour mois mars 2022 Output: 03,2022
#                         Here's the french message: les achats pour le mois janvier [/INST]"""
# result = llm.text_generation(prompt, max_new_tokens=1300, temperature=0.1, top_p=0.7, top_k=50)
# print(result)

# ------------------------------------------------------Top-------------------------------------------------------------------------------------
# llm = InferenceClient(model='mistralai/Mixtral-8x7B-Instruct-v0.1', token='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')

# user_question = input()

# prompt = """<s> [INST] Vous êtes un chatbot conçu pour répondre à des requêtes sur le nombre de fournisseurs souhaités par l'utilisateur.
# Votre réponse doit être un seul nombre, sans ajout d'informations supplémentaires.
# Lorsque l'utilisateur fournit un texte, vous devez indiquer le nombre de fournisseurs demandés.
# Exemple:
# Input: "Quel est le meilleur fournisseur ?"
# Output: Nombre: 1
# Veuillez saisir votre question:""" + user_question + "[/INST]"

# result = llm.text_generation(prompt, max_new_tokens=100, temperature=0.1, top_p=0.95, top_k=50)

# print(result)
# -----------------------------------------------------------------detceter la facture------------------------------------------------------------------------

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


# --------------------------------------------------------------autre code pour detecter les factures--------------------------------------

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

# ------------------------------------------------les montant superieur et inferieur et egal--------------------------------------------------------------------------------------------


# import re
# from huggingface_hub import InferenceClient


# user_question = input("Entrez une phrase : ")

# llm = InferenceClient(model='mistralai/Mixtral-8x7B-Instruct-v0.1', token='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')
#         # Générer une réponse en utilisant le modèle
# prompt = f"""<s> [INST] Vous êtes un chatbot conçu pour detecter un nombre dans une phrase souhaitée par l'utilisateur.
#         Votre réponse doit être un seul nombre, sans ajout d'informations supplémentaires.
#         Lorsque l'utilisateur fournit un texte, vous devez indiquer le nombre demandé.
#         Exemple:
#         Input: "Quel est le montant superieur à 1000DT ?"
#         Output: 1000
#         Voici les message duquel tu dois extraire le nombre: """ + user_question + "[/INST]"

# result = llm.text_generation(prompt, max_new_tokens=100, temperature=0.1, top_p=0.95, top_k=50)
# result = result.replace("Output: ", '').strip()
# print("Réponse du modèle :", result)



# --------------------------------------------------année ou plusieurs année--------------------------------------------------

# llm = InferenceClient(model='mistralai/Mistral-7B-Instruct-v0.2', token='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')
# user_input = input("Entrez une phrase : ")
# prompt = """<s> [INST] Vous êtes un chatbot conçu pour detecter l'année dans une phrase souhaitée par l'utilisateur. 
#                         Votre réponse doit être nombre pour une année ou plusieurs année, sans ajout d'informations supplémentaires.
#                         Lorsque l'utilisateur fournit un texte, vous devez indiquer année demandé.
#                         Input: "je veux avoir le montant total pour année 2022 et 2023"
#                         Output: {2022,2023}
#                         Input: "je veux avoir le montant total pour année 2022?"
#                         Output: {2022}
#                         Voici les message duquel tu dois extraire le nombre: """ + user_input + "[/INST]"
# result = llm.text_generation(prompt, max_new_tokens=100, temperature=0.1, top_p=0.7, top_k=50)
# print(result)


# --------------------------------------------------------------------deux mois et une année---------------------------------------------------------------------------

# llm = InferenceClient(model='mistralai/Mistral-7B-Instruct-v0.2', token='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')
# prompt = """<s> [INST] You are a date interval extractor, your task is to parse French messages containing actions between two month and one year and output them in numeric format. 
# Your output should be structured as follows: month1,month2,year and don't add anything else. 
# Here is an example: je veux avoir les factures entre juin et juillet en 2027 Output: 06,07,2027.
# Here's the french message: consulter les achats des factures entre janvier et mars en 2023[/INST]"""
# result = result.replace("type name: ", "").rstrip('.')
# if result.startswith(" "):
#     result = result[1:]
# print(result)
         
# ------------------------------------------------------montant par etat cree ou valide ou pret pour paiement---------------------------------------------------

# user_input = input("Entrez une phrase : ")

# llm = InferenceClient(model='mistralai/Mistral-7B-Instruct-v0.2', token='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')
# prompt = f"""<s> [INST] Vous êtes un chatbot conçu pour detecter les etats dans une phrase souhaitée par l'utilisateur.
#                         Votre réponse doit être le nom de l'etat se sont cree ou valide ou pret pour paiement seulement, sans ajout d'informations supplémentaires.
#                         Exemple:
#                         Input: "je veux consulter le montant total des factures cree"
#                         Output: cree
#                         Input: "voir les factures valide"
#                         Output: valide
#                         Input: "je veux montant total des factures pret pour paiement"
#                         Output: pret pour paiement
#                         Voici les message duquel tu dois extraire le nombre: """ + user_input + "[/INST]"
# result = llm.text_generation(prompt, max_new_tokens=1300, temperature=0.1, top_p=0.7, top_k=50)
# print(result)


# -------------------------------------------------------------------------------------------------------

# class ActionAfficherMontantsEtat(Action):
#     def name(self) -> Text:
#         return "action_afficher_montants_etat"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

#         user_input = tracker.events[-3].get("value")

#         llm = InferenceClient(model='mistralai/Mistral-7B-Instruct-v0.2', token='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')
#         prompt = f"""<s> [INST] Vous êtes un chatbot conçu pour detecter les etats dans une phrase souhaitée par l'utilisateur.
#                                 Votre réponse doit être le nom de l'etat se sont cree ou valide ou pret pour paiement seulement, sans ajout d'informations supplémentaires.
#                                 Exemple:
#                                 Input: "je veux consulter le montant total des factures cree"
#                                 Output: cree
#                                 Input: "voir les factures valide"
#                                 Output: valide
#                                 Input: "je veux montant total des factures pret pour paiement"
#                                 Output: pret pour paiement
#                                 Voici les message duquel tu dois extraire le nombre: """ + user_input + "[/INST]"

#         result = llm.text_generation(prompt, max_new_tokens=100, temperature=0.1, top_p=0.95, top_k=50)
#         result = result.replace("Output: ", '').strip()
#         print("Réponse du modèle :", result)
#         etat_demande=result
#         if etat_demande not in ["Créé", "Validé", "Prêt pour paiement"]:
#             dispatcher.utter_message(text="L'état demandé n'est pas valide.")
#             return []

#         # Connexion à la base de données (assurez-vous que "conn" est correctement défini)
#         cursor = conn.cursor()
#         # Requête SQL pour obtenir tous les montants correspondant à l'état demandé
#         query = f"""SELECT Fournisseur.Fournisseur , Facture.Référence , Facture.Facture , Date.Date , f.Montant , Facture.Etat , Fournisseur.type
#                     FROM dbo.fait f 
#                     JOIN dbo.[Dimension fournisseur] fournisseur ON f.FK_Fournisseur = fournisseur.Pk_fournisseur
#                     JOIN dbo.[Dimensions facture] facture ON f.FK_facture = facture.PK_facture
#                     JOIN dbo.[Dimension_dates] date ON f.FK_Date = Date.DateKey WHERE facture.etat = '{etat_demande}'"""
#         results = executer_requete(conn, query)  # Vous devez implémenter cette fonction

#         total_montant = 0  # Initialise le montant total

#         if results:
#             for result in results:
#                 # Récupérer les détails de chaque facture
#                 fournisseur, reference, facture, date, montant, etat, type = result
#                 date_str = date.strftime("%Y-%m-%d")
#                 montant_formatte = "{:,.2f}".format(montant)  # Formatage du montant
#                 dispatcher.utter_message(
#                         text=f"Le fournisseur {fournisseur} a une facture {facture} d'un montant de {montant_formatte} avec un état {etat}."
#                     )
#                 total_montant += montant  # Ajoute le montant au total

#             # Formatage du montant total
#             total_montant_formatte = "{:,.2f}".format(total_montant)
#             # Affiche le montant total à la fin
#             dispatcher.utter_message(text=f"Le montant total des factures à l'état '{etat_demande}' est de : {total_montant_formatte}.")
#         else:
#             # Aucun montant trouvé pour l'état demandé
#             dispatcher.utter_message(text=f"Aucun montant trouvé pour l'état '{etat_demande}'.")

#         return []

# from transformers import AutoModelForCausalLM, AutoTokenizer

# model_id = "mistral-community/Mixtral-8x22B-v0.1"
# tokenizer = AutoTokenizer.from_pretrained(model_id)

# model = AutoModelForCausalLM.from_pretrained(model_id)

# text = "Hello my name is"
# inputs = tokenizer(text, return_tensors="pt")

# outputs = model.generate(**inputs, max_new_tokens=20)
# print(tokenizer.decode(outputs[0], skip_special_tokens=True))

