from Entités.Entité import *
from Entités.Golem import *
from Entités.Attaque import *
from Maths.Vec2 import *
from math import acos, sqrt

class Paysan(Entité):

    def __init__(self):
        self.camp = "Paysans"
        self.campsEnnemis = ["Golems"]
        super().__init__()

    def _AttaquerEnnemi(self):
        match self.étatCombat.v:
            case ÉtatCombat.CHARGER:
                self.chargement += 1
                if self.chargement >= self.TEMP_CHARGEMENT:
                    self._exécuterAttaque()
                    self.chargement = 0
                    self.étatCombat.v = ÉtatCombat.LIBRE

            case ÉtatCombat.DÉFENSE:
                if self.cible.étatCombat.v != ÉtatCombat.CHARGER:
                    self.étatCombat.v = ÉtatCombat.LIBRE

            case ÉtatCombat.LIBRE:
                match self.cible.étatCombat.v:
                    case ÉtatCombat.LIBRE:
                        attaque = Attaque()
                        attaque.dégats = self.attaque_normale_dégats
                        self.cible.Attaquer(attaque)

                    case ÉtatCombat.DÉFENSE:
                        self.étatCombat = ÉtatCombat.CHARGER

                    case ÉtatCombat.CHARGER:
                        self.étatCombat = ÉtatCombat.DÉFENSE
    
    def _exécuterAttaque(self):
        attaque = Attaque(self)
        attaque.dégats = self.attaque_normale_dégats + self.chargement*self.attaque_chargée
        self.cible.Attaquer(attaque)
        self.chargement = 0

class Gosse(Paysan):

    def __init__(self):
        super().__init__()
    
    def _exécuterAttaque(self):
        attaque = Attaque(self)
        attaque.dégats = self.attaque_normale_dégats + self.chargement*self.attaque_chargée
        self.cible.Attaquer(attaque)
        self.chargement = 0

class Mineur(Paysan):
    bonus_terre : int = 2 # Bonus contre les golems de terre

    def __init__(self):
        super().__init__()

    def _exécuterAttaque(self):
        attaque = Attaque(self)
        attaque.dégats = self.attaque_normale_dégats + self.chargement*self.attaque_chargée
        if type(self.cible) == GolemTerre:
            attaque.dégats += self.bonus_terre
        self.cible.Attaquer(attaque)
        self.chargement = 0
    
class Prêtre(Paysan):
    vieAddition : int   # Nombre de points de vie à ajouter à un allié par tour de guérison

    def __init__(self):
        super().__init__()

    def _modeRecherche(self):
        ennemiPlusPrès = None
        alliéPlusPrès = None
        distanceMinimaleEnnemi = sys.float_info.max
        distanceMinimaleAllié = sys.float_info.max
        for entité in self.carte.entités:
            if distance(entité.pos,self.pos) < distanceMinimaleEnnemi and self._estEnnemi(entité):
                ennemiPlusPrès = entité
                distanceMinimaleEnnemi = distance(entité.pos,self.pos)
            elif distance(entité.pos,self.pos) < distanceMinimaleAllié and entité.camp == self.camp:
                alliéPlusPrès = entité
                distanceMinimaleAllié = distance(entité.pos,self.pos)
        if ennemiPlusPrès != None and alliéPlusPrès == None:
            self.état.v = ÉtatIA.DÉPLACEMENT
            self.destination = ennemiPlusPrès.pos
        elif ennemiPlusPrès == None and alliéPlusPrès != None:
            self.état.v = ÉtatIA.DÉPLACEMENT
            self.destination = alliéPlusPrès.pos
        elif ennemiPlusPrès != None and alliéPlusPrès != None:
            if ennemiPlusPrès.vie/ennemiPlusPrès.vieMax < alliéPlusPrès.vie/alliéPlusPrès.vieMax:
                self.destination = ennemiPlusPrès.pos
            else :
                self.destination = alliéPlusPrès.pos
        
    def _modeDéplacement(self):
        faire_pathfinding = True
        if len(self.chemin) > 0:
            if self.carte.peutAller(self.chemin[0].pos):
                self.direction = self.chemin[0].pos - self.pos
                self.pos = self.chemin[0].pos.copie()
                faire_pathfinding = False

                for ennemi in self.carte.entités:
                    if distance(ennemi.pos, self.pos) <= 1 and self.cible.camp in self.campsEnnemis:
                        self.état.v = ÉtatIA.COMBAT
                        self.cible = ennemi
                        break
                    elif distance(ennemi.pos, self.pos) <= 1 and self.cible.camp == self.camp:
                        self.état.v = ÉtatIA.GUÉRISON
                        break
                if self.cible == None and self.pos == self.destination and self.état.v == ÉtatIA.DÉPLACEMENT:
                    self.état.v = ÉtatIA.RECHERCHE
                elif self.cible == None and self.pos == self.destination and self.état.v == ÉtatIA.DÉPLACEMENT_IMMOBILE:
                    self.état.v = ÉtatIA.IMMOBILE
            else:
                self.chemin = []
                faire_pathfinding = True

        if faire_pathfinding:
            self.chemin = self._A_étoile(self.carte, self.pos, self.destination)
    
    def _exécuterAttaque(self):
        attaque = Attaque(self)
        attaque.dégats = self.attaque_normale_dégats + self.chargement*self.attaque_chargée
        self.cible.Attaquer(attaque)
    
    def _modeGuérison(self):
        if self.cible.vie < self.cible.vieMax and distance(self.cible.pos, self.pos) <= 1:
            self.cible.vie += self.vie
        else:
            self.état.v = ÉtatIA.RECHERCHE
            self.cible = None
    
class Chevalier(Paysan):
    def __init__(self):
        super().__init__()
    
    def _exécuterAttaque(self):
        attaque = Attaque(self)
        attaque.dégats = self.attaque_normale_dégats + self.chargement*self.attaque_chargée
        if self.chargement > 0:
            for entité in self.carte.entités:
                angle = acos(self.direction.norm() @ norm(entité.pos - self.pos))   # Le @ est un produit scalaire (a•b)
                """
                #   Les trois cases en face du chevaliere se trouvent à un angle d'au plus 45° de la direction vers laquelle il fait face
                #   et à une distance d'au plus √2. Pour s'assurer que les entitées prises dans l'attaque soient détectée, on augmente
                #   légèrement la zone d'effet (47° au lieu de 45° et √2.1 au lieu de √2 )
                # 
                #                 +-----+-----+-----+         +-----+-----+-----+
                #                 |\    |     |     |         |     |     |     |
                #              47°->\X  |  X  |  X  |         |  X  |  X  |  O  |
                #                 |   \\|  |  |/ <---√2       √2-> \|  |  |     |
                #                 +-----+-----+-----+         +-----+--|--+-----+
                #                 |     |\ |^/| <- 45°       45°-> ( \ |  |     |
                #                 |  O  |  C  |  O  |         |  X-----C  |  O  |
                #                 |     |     |     |         |     |     |     |
                #                 +-----+-----+-----+         +-----+-----+-----+
                #                 |     |     |     |         |     |     |     |
                #                 |  O  |  O  |  O  |         |  O  |  O  |  O  |
                #                 |     |     |     |         |     |     |     |
                #                 +-----+-----+-----+         +-----+-----+-----+
                #                            
                """
                if angle <= 47 and distance(self.pos, entité.pos) <= sqrt(2.1):
                    entité.Attaquer(attaque)
        else:
            self.cible.Attaquer(attaque)
    
class Arbaletier(Paysan):
    max_distance_attaque : float = 3.0
    min_distance_ennemi : float = 1.5

    def __init__(self):
        super().__init__()
    
    def _modeRecherche(self):
        ennemiPlusPrès = None
        alliéPlusPrès = None
        distanceMinimaleEnnemi = sys.float_info.max
        distanceMinimaleAllié = sys.float_info.max
        for entité in self.carte.entités:
            if distance(entité.pos,self.pos) < distanceMinimaleEnnemi and self._estEnnemi(entité):
                ennemiPlusPrès = entité
                distanceMinimaleEnnemi = distance(entité.pos,self.pos)
            elif distance(entité.pos,self.pos) < distanceMinimaleAllié and entité.camp == self.camp:
                alliéPlusPrès = entité
                distanceMinimaleAllié = distance(entité.pos,self.pos)
        if ennemiPlusPrès != None and alliéPlusPrès == None:
            self.état.v = ÉtatIA.DÉPLACEMENT
            self.destination = ennemiPlusPrès.pos
        elif ennemiPlusPrès == None and alliéPlusPrès != None:
            self.état.v = ÉtatIA.DÉPLACEMENT
            self.destination = alliéPlusPrès.pos
        elif ennemiPlusPrès != None and alliéPlusPrès != None:
            if ennemiPlusPrès.vie/ennemiPlusPrès.vieMax < alliéPlusPrès.vie/alliéPlusPrès.vieMax:
                self.destination = ennemiPlusPrès.pos
            else :
                self.destination = alliéPlusPrès.pos
    
    def _modeDéplacement(self):
        faire_pathfinding = True
        if len(self.chemin) > 0:
            if self.carte.peutAller(self.chemin[0].pos):
                self.direction = self.chemin[0].pos - self.pos
                self.pos = self.chemin[0].pos.copie()
                faire_pathfinding = False

                for entité in self.carte.entités:
                    if distance(entité.pos, self.pos) <= self.min_distance_ennemi and entité.camp in self.campsEnnemis:
                        faire_pathfinding = True
                        break
                if not faire_pathfinding:
                    for ennemi in self.carte.entités:
                        if distance(ennemi.pos, self.pos) <= self.max_distance_attaque:
                            self.état.v = ÉtatIA.COMBAT
                            self.cible = ennemi
                            break

                if self.cible == None and self.pos == self.destination and self.état.v == ÉtatIA.DÉPLACEMENT:
                    self.état.v = ÉtatIA.RECHERCHE
                elif self.cible == None and self.pos == self.destination and self.état.v == ÉtatIA.DÉPLACEMENT_IMMOBILE:
                    self.état.v = ÉtatIA.IMMOBILE
            else:
                self.chemin = []
                faire_pathfinding = True

        if faire_pathfinding:
            self.chemin = self._A_étoile(self.carte, self.pos, self.destination)
    
    def _modeCombat(self):
        for entité in self.carte.entités:
            if distance(self.pos, entité.pos) <= self.min_distance_ennemi:
                self.état.v = ÉtatIA.DÉPLACEMENT
                direction = norm(self.pos - entité.pos)

                xp = direction @ Vec2(1.0,0.0)
                yp = direction @ Vec2(0.0,1.0)
                xn = direction @ Vec2(-1.0,0.0)
                yn = direction @ Vec2(0.0,-1.0)

                maxd = max(max(max(xp,xn),yp),yn)
                if maxd == xp:
                    self.destination = self.pos + Vec2(1.0,0.0)
                elif maxd == xn:
                    self.destination = self.pos + Vec2(-1.0,0.0)
                elif maxd == yp:
                    self.destination = self.pos + Vec2(0.0,1.0)
                elif maxd == yn:
                    self.destination = self.pos + Vec2(0.0,-1.0)
                
                self.cible = None
                break
        if self.cible.estVivant and distance(self.cible.pos, self.pos) <= 1:
            self._AttaquerEnnemi()
        else:
            self.état.v = ÉtatIA.RECHERCHE
            self.estAttaqué = False
            self.cible = None
    

