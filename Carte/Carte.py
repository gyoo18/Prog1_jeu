from __future__ import annotations
from Maths.Vec2 import Vec2
from Entités.Paysan import *
from Entités.Golem import *
from Entités.Personnages import *
from Carte.Tuile import Tuile
from TFX import *
from InclusionsCirculaires.Entité_Carte import *

class Plan:
    def __init__(self):
        self.estAnimation = False
        self.personnages : list[list[str]] = []
        self.personnages_positions : list[list[Vec2]] = []
        self.dialogues : list[str] = []
        self.titres : list[str] = []
        self.temps : list[float] = []

class Séquence:
    DÉBUT = "Début"
    JEU = "Jeu"
    SUCCÈS = "Succès"
    ÉCHEC = "Échec"

    def __init__(self):
        self.position : str = Séquence.DÉBUT
        self.plans : list[Plan] = []

class Carte:
    
    def __init__(self,estScène : bool, lignes : int ,colonnes :int, matrice : list[list[Tuile]], entités_préchargement : list[tuple[str,Vec2|None,str|None]], joueur_pos_init : Vec2, séquences : Séquence|list[Séquence], prochaine : str):
        self.lignes : int = lignes
        self.colonnes : int = colonnes
        self.matrice : list[list[Tuile]] = matrice
        self.entités : list[Entité] = []
        self.entités_préchargement : list[tuple[str,Vec2|None,str|None]] = entités_préchargement
        self.prochaine : str = prochaine
        self.joueur_pos_init : Vec2 = joueur_pos_init

        self.estScène : bool = estScène
        self.séquences : Séquence|list[Séquence] = séquences
            
    def peutAller(self, entite: Entité, pos: Vec2):
        if pos.x<0 or pos.x>len(self.matrice)-1 or pos.y<0 or pos.y>len(self.matrice[0])-1:
            return False
        for e in self.entités:
            if e.pos == pos:
                return False
        tuiles = self.matrice[int(pos.x)][int(pos.y)]
        if tuiles.type == Tuile.TYPE_MUR:
            return False
        elif tuiles.type == Tuile.TYPE_EAU and type(entite) != GolemEau:
            return False
        elif tuiles.type == Tuile.TYPE_FEUX and type(entite) != GolemFeu:
            return False
        else:
            return True

    def position(self):
        dict_position = {}
        for ligne in range(self.lignes):
            for colonne in range(self.colonnes):
                dict_position[ligne,colonne] = "0"
        return dict_position
    
    def dessiner(self):
        dessin = ""
        for y in range(self.lignes):
            ligne = ""
            for x in range(self.colonnes):
                
                en = "  "
                for e in self.entités:
                    if e.pos.x == x and e.pos.y == y:
                        if e.camp == Entité.CAMP_PAYSANS:
                            match e:
                                case Gosse():
                                    en = gras(coul(" ç",ROUGE))
                                    break
                                case Mineur():
                                    en = gras(coul("/>",ROUGE))
                                    break
                                case Prêtre():
                                    en = gras(coul("Ot",ROUGE))
                                    break
                                case Arbalettier():
                                    en = gras(coul("G>",ROUGE))
                                    break
                                case Chevalier():
                                    en = gras(coul("M←",ROUGE))
                                    break
                                case Paysan():
                                    en = gras(coul("P¬",ROUGE))
                                    break
                                case _:
                                    raise TypeError("Entité " + str(e) + " n'est pas un paysan valide.")
                        
                        elif e.camp == Entité.CAMP_GOLEMS:
                            match e:
                                case GolemTerre():
                                    en = gras(coul("(u",BRUN))
                                    break
                                case GolemEau():
                                    en = gras(coul("}{",BLEU))
                                    break
                                case GolemFeu():
                                    en = gras(coul("MM",ORANGE))
                                    break
                                case GolemDoré():
                                    en = gras(coul("$$",JAUNE))
                                    break
                                case Golem():
                                    en = gras(coul("GG",GRIS))
                                    break
                                case _:
                                    raise TypeError("Entité " + str(e) + " n'est pas un golem valide.")
                        
                        elif e.camp == Entité.CAMP_JOUEUR:
                            match e:
                                case Joueur():
                                    en = gras(coul("/\\",BLEU))
                                case _:
                                    raise TypeError("Joueur " + str(e) + " n'est pas un joueur de type valide.")

                        elif e.camp == Entité.CAMP_PERSONNAGES:
                            en = e.avoir_caractère_dessin()

                    # if en == "  " and len(e.chemin) > 0:
                    #     for pos in e.chemin:
                    #         if pos.x == x and pos.y == y:
                    #             if e.camp == "Paysans":
                    #                 en = gras(coul("++",ROUGE))
                    #             if e.camp == "Golems":
                    #                 en = gras(coul("••",NOIR))
                    #             if e.camp == "Personnages":
                    #                 en = gras(coul("--",BLEU))
                    #             break
                
                match self.matrice[x][y].type:
                    case Tuile.TYPE_EAU:
                        ligne += surl(en,CYAN_FONCÉ)
                    case Tuile.TYPE_TERRE:
                        ligne += surl(en,VERT)
                    case Tuile.TYPE_FEUX:
                        ligne += surl(en,ORANGE_FONCÉ)
                    case Tuile.TYPE_MUR:
                        ligne += surl(en,GRIS_FONCÉ)
                    case Tuile.TYPE_OR:
                        ligne += surl(en,OR)
                    case _:
                        raise TypeError("Tuile " + str(self.matrice[x][y]) + " de type " + str(self.matrice[x][y].type) + " n'a pas de type valide.")
            dessin += ligne + '\n'
        return dessin