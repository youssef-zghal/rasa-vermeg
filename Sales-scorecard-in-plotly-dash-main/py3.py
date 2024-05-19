


[ salutation,
bye,
connaitre_montant_a_partir_reference,montant,reference
Montant_egal,montant,egal
Montant_inferieur,inferieur,montant
Montant_superieur,superieur,montant
Montant_total_fournisseur,fournisseur,achat,montant,total
montant_total_etats,etat,montant,total
montant_etat_cree,cree,facture,montant,total
montant_etat_prêt_pour_paiement,pret pour paiement,montant,total,facture
montant_etat_valide,montant,total,facture,valide
montant_total_type,total,montant,type
obtenir_montant_total_facture,montant,total,facture
achats_total_mois_annees,montant,total,achat,mois,annee
obtenir_montant_total_par_annees,montant,total,achat,annee
montant_total_Jusquau_mois_annee,montant,total,achat,mois,annee
                                
nombre_fournisseur,nombre,fournisseur,combien
nombre_fournisseur_par_mois,nombre,fournisseur,mois,par,combien
nombre_fournisseur_par_annee,nombre,fournisseur,annee,par,combien
demande_montant_fournisseur,fournisseur,consulter,voir,details,montant,total
nombre_type,combien,nombre,type
nombre_facture,combien,nombre,facture
nombre_facture_par_mois,combien,nombre,facture,mois,par
nombre_facture_par_annee,combien,nombre,facture,annee,par
                                
demande_top_Type,top,meuilleur,type,plus,type
demande_top_fournisseurs,top,meuilleur,plus,fournisseur
demande_Less_fournisseurs,moins,fournisseur

montant_total_entre_deux_mois_pour_une_annee,montant,total,achat,mois,annee                       
afficher_montants_des_factures_etat_valides_par_mois_annee,montant,total,achat,mois,annee,facture,valide
afficher_montants_des_factures_etat_cree_par_mois_annee,montant,total,achat,mois,annee,facture,cree
afficher_montants_des_factures_etat_prets_pour_paiement_par_mois_annee,montant,total,achat,mois,annee,facture,pret pour paiement
demander_montant_total_entre_mois_annee_et_mois_annee,montant,total,achat,mois,annee
demander_montant_total_fournisseur_mois_annee ,montant,total,achat,mois,annee,fournisseur


demande_details_sur_Facture,consulter,details,facture,montant
demande_montant_type,montant,consulter,voir,type



        # Here are some examples: 
        # first example: Quel est le montant des factures entre décembre 2022 et avril 2023. output: class: demander_montant_total_entre_mois_annee_et_mois_annee
        # Second example: Quel est le fournisseur pour cette facture 000126-23 output: class: demande_details_sur_Facture.
        # Third example: Pouvez-vous me montrer les détails du type des cartes et systèmes électroniques output: class: demande_montant_type
        # fourth example: Quels sont les montants valides output: class: montant_etat_valide
        # fiveth example: Factures créées output: class: montant_etat_cree
        # sixth example: Quels sont les paiements prêts pour paiement output: class: montant_etat_prêt_pour_paiement
        # seventh example: 4 principaux secteurs output: class: demande_top_Type  
        # eighth example: Les 2 fournisseurs les moins significatifs: class: demande_Less_fournisseurs  
        # ninth example: Quel est le montant total pour le mois d'août 2023: class: achats_total_mois_annees 
        # tenth example: Quels sont les montants valides pour février 2022: class: afficher_montants_des_factures_etat_valides_par_mois_annee       
        # eleventh example: Quels sont les montants prêts pour le paiement en février 2022: class: afficher_montants_des_factures_etat_prets_pour_paiement_par_mois_annee    
        # twelfth example: Combien avons-nous dépensé entre janvier et février en 2023: class: montant_total_entre_deux_mois_pour_une_annee   
        # thirteenth example: Quel est le montant des factures entre janvier 2022 et février 2023: class: demander_montant_total_entre_mois_annee_et_mois_annee 
        # fourteenth example: Quel est le total des dépenses pour ADHECOM SARL pour le mois d'août 2022: class: demander_montant_total_fournisseur_mois_annee