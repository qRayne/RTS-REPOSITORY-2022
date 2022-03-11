## -*- Encoding: UTF-8 -*-

import urllib.request
import urllib.parse
import urllib.error
import json
import random
import pickle
from helper import Helper
from RTS_divers import *
from RTS_vue import *
from RTS_modele import *
import time
import threading

"""
Application client RTS, base sur le modele approximatif d'Age of Empire I

module principal (main), essentiellement le controleur, dans l'architecture M-V-C
"""


class Controleur():
    def __init__(self):
        self.monnom = self.generer_nom()  # nom de joueur, sert d'identifiant dans le jeu - ici, avec auto-generation

        self.joueur_createur = 0  # 1 quand un joueur "Créer une partie", peut Demarrer la partie
        self.cadrejeu = 0  # compte les tours dans la boucle de jeu (bouclersurjeu)
        self.actionsrequises = []  # les actions envoyées au serveur
        self.joueurs = []  # liste des noms de joueurs pour le lobby

        self.prochainsplash = None  # requis pour sortir de cette boucle et passer au lobby du jeu
        self.onjoue = 1  # indicateur que le jeu se poursuive - sinon on attend qu'un autre joueur nous rattrape
        self.maindelai = 40  # delai en ms de la boucle de jeu
        self.moduloappeler_serveur = 5  # frequence des appel au serveur, evite de passer son temps a communiquer avec le serveur
        self.urlserveur = "http://127.0.0.1:8000"  # 127.0.0.1 pour tests,"http://votreidentifiant.pythonanywhere.com" pour web

        self.modele = None  # la variable contenant la partie, après initialiserpartie()
        self.vue = Vue(self, self.urlserveur, self.monnom,
                       "Non connecté")  # la vue pour l'affichage et les controles du jeu

        self.vue.root.mainloop()  # la boucle des evenements (souris, click, clavier)

    def connecter_serveur(self, url_serveur):
        self.urlserveur = url_serveur  # le dernier avant le clic
        self.boucler_sur_splash()

    # a partir du splash
    def creer_partie(self, nom):
        if self.prochainsplash:  # si on est dans boucler_sur_splash, on doit supprimer le prochain appel
            self.vue.root.after_cancel(self.prochainsplash)
            self.prochainsplash = None
        if nom:  # si c'est pas None c'est un nouveau nom
            self.monnom = nom
        # on avertit le serveur qu'on cree une partie
        url = self.urlserveur + "/creer_partie"
        params = {"nom": self.monnom}
        reptext = self.appeler_serveur(url, params)

        self.joueur_createur = 1  # on est le createur
        self.vue.root.title("je suis " + self.monnom)
        # on passe au lobby pour attendre les autres joueurs
        self.vue.changer_cadre("lobby")
        self.boucler_sur_lobby()

    # un joueur s'inscrit à la partie, similaire à creer_partie
    def inscrire_joueur(self, nom, urljeu):
        # on quitte le splash et sa boucle
        if self.prochainsplash:
            self.vue.root.after_cancel(self.prochainsplash)
            self.prochainsplash = None
        if nom:
            self.monnom = nom
        # on s'inscrit sur le serveur
        url = self.urlserveur + "/inscrire_joueur"
        params = {"nom": self.monnom}
        reptext = self.appeler_serveur(url, params)

        self.vue.root.title("je suis " + self.monnom)
        self.vue.changer_cadre("lobby")
        self.boucler_sur_lobby()

    # a partir du lobby, le createur avertit le serveur de changer l'etat pour courant
    def lancer_partie(self):
        url = self.urlserveur + "/lancer_partie"
        params = {"nom": self.monnom}
        reptext = self.appeler_serveur(url, params)

    # Apres que le createur de la partie ait lancer_partie
    # boucler_sur_lobby a reçu code ('courant') et appel cette fonction pour tous
    def initialiser_partie(self, mondict):
        initaleatoire = mondict[1][0][0]
        #random.seed(12471)  # random FIXE pour test ou ...
        random.seed(int(initaleatoire))   # qui prend la valeur generer par le serveur

        # on recoit la derniere liste des joueurs pour la partie
        listejoueurs = []
        for i in self.joueurs:
            listejoueurs.append(i[0])

        self.modele = Partie(self,listejoueurs)  # on cree une partie pour les joueurs listes, qu'on conserve comme modele
        self.vue.initialiser_avec_modele(self.modele)  # on fournit le modele et mets la vue à jour
        self.vue.changer_cadre("jeu")  # on change le cadre la fenetre pour passer dans l'interface de jeu
        self.vue.centrer_maison()

        self.boucler_sur_jeu()  # on lance la boucle de jeu

    ##########   BOUCLES: SPLASH, LOBBY ET JEU    #################
    # boucle de communication intiale avec le serveur pour creer ou s'inscrire a la partie
    def boucler_sur_splash(self):
        url = self.urlserveur + "/tester_jeu"
        params = {"nom": self.monnom}
        mondict = self.appeler_serveur(url, params)
        if mondict:
            self.vue.update_splash(mondict[0])
        self.prochainsplash = self.vue.root.after(50, self.boucler_sur_splash)

    # on boucle sur le lobby en attendant le demarrage
    def boucler_sur_lobby(self):
        url = self.urlserveur + "/boucler_sur_lobby"
        params = {"nom": self.monnom}
        mondict = self.appeler_serveur(url, params)

        if "courante" in mondict[0]:  # courante, la partie doit etre initialiser
            self.initialiser_partie(mondict)
        else:
            self.joueurs = mondict
            self.vue.update_lobby(mondict)
            self.vue.root.after(50, self.boucler_sur_lobby)

    # BOUCLE PRINCIPALE
    def boucler_sur_jeu(self):
        self.cadrejeu += 1  # increment du compteur de boucle de jeu

        if self.cadrejeu % self.moduloappeler_serveur == 0:  # appel périodique au serveur
            if self.actionsrequises:
                actions = self.actionsrequises
            else:
                actions = None
            self.actionsrequises = []
            url = self.urlserveur + "/boucler_sur_jeu"
            params = {"nom": self.monnom,
                      "cadrejeu": self.cadrejeu,
                      "actionsrequises": actions}
            try:  # permet de récupérer des time-out, mais aussi des commandes de pause du serveur pour retard autre joueur
                mondict = self.appeler_serveur(url, params)
                if "ATTENTION" in mondict:  # verifie attente d'un joueur plus lent
                    print("ATTEND QUELQU'UN")
                    self.onjoue = 0
                else:  # sinon on ajoute l'action
                    self.modele.ajouter_actions_a_faire(mondict)
            except urllib.error.URLError as e:
                print("ERREUR ", self.cadrejeu, e)
                self.onjoue = 0

        # le reste du tour vers modele et vers vue, s'il y a lieu
        if self.onjoue:
            # envoyer les messages au modele et a la vue de faire leur job
            self.modele.jouer_prochain_coup(self.cadrejeu)
            self.vue.afficher_jeu()
        else:
            self.cadrejeu -= 1
            self.onjoue = 1

        self.vue.root.after(self.maindelai,
                            self.boucler_sur_jeu)  # appel ulterieur de la meme fonction jusqu'a l'arret de la partie

    ##############   FONCTIONS pour serveur #################
    # methode speciale pour remettre les parametres du serveur a leurs valeurs par defaut
    def reset_partie(self):
        leurl = self.urlserveur + "/reset_jeu"
        reptext = self.appeler_serveur(leurl, 0)
        self.vue.update_splash(reptext[0][0])
        return reptext

    #   retour de l'etat du serveur
    def tester_etat_serveur(self):
        leurl = self.urlserveur + "/tester_jeu"
        repdecode = self.appeler_serveur(leurl, None)[0]
        if "dispo" in repdecode:  # on peut creer une partie
            return ["dispo", repdecode]
        elif "attente" in repdecode:  # on peut s'inscrire a la partie
            return ["attente", repdecode]
        elif "courante" in repdecode:  # la partie est en cours
            return ["courante", repdecode]
        else:
            return "impossible"

    # fonction d'appel normalisee d'appel pendant le jeu
    def appeler_serveur(self, url, params):
        if params:
            query_string = urllib.parse.urlencode(params)
            data = query_string.encode("ascii")
        else:
            data = None
        rep = urllib.request.urlopen(url, data, timeout=None)
        reptext = rep.read()
        rep = reptext.decode('utf-8')
        rep = json.loads(rep)
        return rep

    ############            OUTILS           ###################
    # generateur de nouveau nom, peut y avoir collision
    def generer_nom(self):
        monnom = "TESTEUR_" + str(random.randrange(100, 1000))
        return monnom

    def abandonner(self):
        action = [self.monnom, "abandonner", [self.monnom + ": J'ABANDONNE !"]]
        self.actionsrequises = action
        self.vue.root.after(500, self.vue.root.destroy)

    ############        VOTRE CODE AU BESOIN      ######################
    ### Placez vos fonctions 
    def afficher_batiment(self, nom, batiment):
        self.vue.afficher_batiment(nom, batiment)

    def afficher_bio(self, bio):
        self.vue.afficher_bio(bio)

    def installer_batiment(self, nomjoueur, batiment):
        x1, y1, x2, y2 = self.vue.afficher_batiment(nomjoueur, batiment)
        return [x1, y1, x2, y2]

    def trouver_valeurs(self):
        vals = self.modele.trouver_valeurs()
        return vals

    def montrer_stats(self,evt):
        self.modele.calc_stats()

if __name__ == '__main__':
    print("Bienvenue au RTS")
    c = Controleur()
    # print("FIN DE PROGRAMME")
