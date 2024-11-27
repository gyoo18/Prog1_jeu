from Ressources import Ressources
from Jeu import Jeu, ÉtatJeu
import dialogue
import message

def miseÀJour(jeu : Jeu):
    res = Ressources.avoirRessources()
    i = input("Continuer? [O/N] : ").capitalize()

    if i == "N":
        print("Sortie du jeu.")
        jeu.état.v = ÉtatJeu.TERMINÉ

    match jeu.état.v:
        case ÉtatJeu.INTRODUCTION:
            message.script("Introduction",None,jeu)
        case ÉtatJeu.ZONE1:
            # dialogue.jeu_principal(jeu)
            message.script("Prairie","Debut",jeu)
            if input("Tapez G").capitalize() == 'G':
                message.script("Prairie","Success",jeu)
            else:
                message.script("Prairie","Failure",jeu)
            if jeu.état.v != ÉtatJeu.TERMINÉ:
                jeu.état.v = ÉtatJeu.ZONE2
        case ÉtatJeu.ZONE2:
            # dialogue.jeu_principal(jeu)
            message.script("Cite","Debut",jeu)
            if input("Tapez G").capitalize() == 'G':
                message.script("Cite","Success",jeu)
            else:
                message.script("Cite","Failure",jeu)
            if jeu.état.v != ÉtatJeu.TERMINÉ:
                jeu.état.v = ÉtatJeu.ZONE3
        case ÉtatJeu.ZONE3:
            # dialogue.jeu_principal(jeu)
            message.script("Chateau","Debut",jeu)
            if input("Tapez G").capitalize() == 'G':
                message.script("Chateau","Success",jeu)
            else:
                message.script("Chateau","Failure",jeu)
            if jeu.état.v != ÉtatJeu.TERMINÉ:
                jeu.état.v = ÉtatJeu.TERMINÉ
        case ÉtatJeu.MENU:
            i = input("Voici le menu.\n Quitter : [Q]\n Poursuivre : [P]\n").capitalize()
            if i == "Q":
                jeu.état.v = ÉtatJeu.TERMINÉ
            if i == "P":
                jeu.état.v = ÉtatJeu.ZONE1
        case ÉtatJeu.TERMINÉ:
            return

    if i == "O":
        print("Mise à jour des entitées.")
        for i in range(len(res.entités)):
            res.entités[i]._MiseÀJourIA()
        print("Entitées mises à jours.")
        res.cartes[0].dessiner()