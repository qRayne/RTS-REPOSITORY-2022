## -*- Encoding: UTF-8 -*-
import random
from tkinter import *
from tkinter import ttk
from tkinter.simpledialog import *

from typing import Type

from helper import Helper
from RTS_divers import *
from chargeurdimages import *
import RTS_vuecadres

class Vue():
    def __init__(self,parent,urlserveur,monnom,testdispo):
        self.parent=parent
        self.root=Tk()
        self.root.title("Je suis "+monnom)
        self.monnom=monnom
        # attributs
        self.cadrechaton=0
        self.textchat=""
        self.infohudnourriture={}
        self.infohudbois={}
        self.infohudpierremetaux={}
        self.tailleminicarte=200
        self.btnchat = None
        self.btnaide = None
        self.btncraft = None

        self.cadreactif=None
        # # objet pour cumuler les manipulations du joueur pour generer une action de jeu
        self.action=Action(self)

        # cadre principal de l'application
        self.cadreapp=Frame(self.root,width=500,height=400,bg="snow")
        self.cadreapp.pack(expand=1,fill=BOTH)

        # # un dictionnaire pour conserver les divers cadres du jeu, creer plus bas
        self.cadres={}
        self.creer_cadres(urlserveur,monnom,testdispo)
        self.changer_cadre("splash")

        # self.root.protocol("WM_DELETE_WINDOW", self.demanderabandon)
        # # sera charge apres l'initialisation de la partie, contient les donnees pour mettre l'interface a jour
        self.modele=None
        # # variable pour suivre le trace du multiselect
        self.debut_selection=[]
        self.selecteuractif=None
        # # images des assets, definies dans le modue loadeurimages
        self.images=chargerimages()
        self.gifs=chargergifs()

####### INTERFACES GRAPHIQUES
    def changer_cadre(self,nomcadre: str):
        cadre=self.cadres[nomcadre]
        if self.cadreactif:
            self.cadreactif.pack_forget()
        self.cadreactif=cadre
        self.cadreactif.pack(expand=1,fill=BOTH)

    ###### LES CADRES ############################################################################################
    def creer_cadres(self, urlserveur: str, monnom: str, testdispo: str):
        self.cadres["splash"] = self.creer_cadre_splash(urlserveur, monnom, testdispo)
        self.cadres["lobby"] = self.creer_cadre_lobby()
        self.cadres["jeu"] = self.creer_cadre_jeu()

    # le splash (ce qui 'splash' à l'écran lors du démarrage)
    # sera le cadre visuel initial lors du lancement de l'application
    def creer_cadre_splash(self, urlserveur: str, monnom: str, testdispo: str) -> Frame:
        self.cadresplash = Frame(self.cadreapp)
        # un canvas est utilisé pour 'dessiner' les widgets de cette fenêtre voir 'create_window' plus bas
        self.canevassplash = Canvas(self.cadresplash, width=600, height=480, bg="pink")
        self.canevassplash.pack()

        # creation ds divers widgets (champ de texte 'Entry' et boutons cliquables (Button)
        self.etatdujeu = Label(text=testdispo, font=("Arial", 18), borderwidth=2, relief=RIDGE)
        self.nomsplash = Entry(font=("Arial", 14))
        self.urlsplash = Entry(font=("Arial", 14))
        self.btnurlconnect = Button(text="Connecter", font=("Arial", 12), command=self.connecter_serveur)
        # on insère les infos par défaut (nom url) et reçu au démarrage (dispo)
        self.nomsplash.insert(0, monnom)
        self.urlsplash.insert(0, urlserveur)
        # on les place sur le canevassplash
        self.canevassplash.create_window(320, 100, window=self.etatdujeu, width=400, height=30)
        self.canevassplash.create_window(320, 200, window=self.nomsplash, width=400, height=30)
        self.canevassplash.create_window(240, 250, window=self.urlsplash, width=200, height=30)
        self.canevassplash.create_window(420, 250, window=self.btnurlconnect, width=100, height=30)
        # les boutons d'actions
        self.btncreerpartie = Button(text="Creer partie", font=("Arial", 12), state=DISABLED, command=self.creer_partie)
        self.btninscrirejoueur = Button(text="Inscrire joueur", font=("Arial", 12), state=DISABLED, command=self.inscrire_joueur)
        self.btnreset = Button(text="Reinitialiser partie", font=("Arial", 9), state=DISABLED, command=self.reset_partie)

        # on place les autres boutons
        self.canevassplash.create_window(420, 350, window=self.btncreerpartie, width=200, height=30)
        self.canevassplash.create_window(420, 400, window=self.btninscrirejoueur, width=200, height=30)
        self.canevassplash.create_window(420, 450, window=self.btnreset, width=200, height=30)

        ############ ## NOTES : ceci est un exemple pour ajouter des options au cadresplash
        # ## POUR CHOIX CIVILISATION, 4 OPTIONS
        # # LA VARIABLE DONT LA VALEUR CHANGERA AU FIL DES CLICK
        # self.valciv = StringVar(self.cadresplash, "1")
        # # LES 4 BTN RADIO
        # radciv1 = Radiobutton(text="Azteque", variable=self.valciv, value="Azteque")
        # radciv2 = Radiobutton(text="Congolaise", variable=self.valciv, value="Congolaise")
        # radciv3 = Radiobutton(text="Russe", variable=self.valciv, value="Russe")
        # radciv4 = Radiobutton(text="Maya", variable=self.valciv, value="Maya")
        # radciv5 = Radiobutton(text="Magyar", variable=self.valciv, value="Magyar")
        # # LE PLACEMENTS DES BTN RADIOS
        # self.canevassplash.create_window(220, 350, window=radciv1, width=180, height=30)
        # self.canevassplash.create_window(220, 380, window=radciv2, width=180, height=30)
        # self.canevassplash.create_window(220, 410, window=radciv3, width=180, height=30)
        # self.canevassplash.create_window(220, 440, window=radciv4, width=180, height=30)
        # self.canevassplash.create_window(220, 470, window=radciv5, width=180, height=30)
        # ## ##########    FIN de l'exemple des choix de civilisations


        ############# NOTE le bouton suivant permet de générer un Frame issu d'un autre module et l'intégrer à la vue directement
        #self.btncadretest = Button(text="Cadre test", font=("Arial", 9),  command=self.montrercadretest)
        # on place les autres boutons
        # self.canevassplash.create_window(120, 450, window=self.btncadretest, width=200, height=30)
        ##############

        # on retourne ce cadre pour l'insérer dans le dictionnaires des cadres
        return self.cadresplash

    def connecter_serveur(self):
        self.btninscrirejoueur.config(state=NORMAL)
        self.btncreerpartie.config(state=NORMAL)
        self.btnreset.config(state=NORMAL)
        url_serveur=self.urlsplash.get()
        self.parent.connecter_serveur(url_serveur)

    ###########  cette fonction la creation d'un frame par un autre module - pour fin de test uniquement
    # def montrercadretest(self):
    #     self.cadretest=RTS_vuecadres.Cadre_test(self)
    #     print(self.cadretest.nom)
    #     self.cadretest.grid(in_=self.canevas,row=0,column=0)
    ########## fin fonction test pour auttre module

    ######## le lobby (où on attend les inscriptions)
    def creer_cadre_lobby(self):
        # le cadre lobby, pour isncription des autres joueurs, remplace le splash
        self.cadrelobby=Frame(self.cadreapp)
        self.canevaslobby=Canvas(self.cadrelobby,width=640,height=480,bg="lightblue")
        self.canevaslobby.pack()
        # widgets du lobby
        # un listbox pour afficher les joueurs inscrit pour la partie à lancer
        self.listelobby=Listbox(borderwidth=2,relief=GROOVE)

        # bouton pour lancer la partie, uniquement accessible à celui qui a creer la partie dans le splash
        self.btnlancerpartie=Button(text="Lancer partie",state=DISABLED,command=self.lancer_partie)
        # affichage des widgets dans le canevaslobby (similaire au splash)
        self.canevaslobby.create_window(440,240,window=self.listelobby,width=200,height=400)
        self.canevaslobby.create_window(200,400,window=self.btnlancerpartie,width=100,height=30)
        # on retourne ce cadre pour l'insérer dans le dictionnaires des cadres
        return self.cadrelobby

    ### cadre de jeu : inclus aire de jeu, le HUD, le cadre_jeu_action
    def creer_cadre_jeu(self):
        # le cadre principal du jeu, remplace le Lobby
        self.cadrepartie=Frame(self.cadreapp,bg="light gray",width=400,height=400)
        # cadre du jeu et ses scrollbars
        self.creer_aire_de_jeu()
        # cadre pour info sur les ressources du joueur en haut de l'aire de jeu
        self.creer_HUD()
        # cadre pour commandes et infos des objets de jeu, situe a droite
        self.creer_cadre_jeu_action()
        # configuration de la section qui s'etire lorsque la fenetre change de taille
        self.cadrepartie.rowconfigure(0, weight=1)
        self.cadrepartie.columnconfigure(0, weight=1)
        # on retourne ce cadre pour l'insérer dans le dictionnaires des cadres
        return self.cadrepartie

    def creer_aire_de_jeu(self):
        # definition du cadre avec le canvas de jeu et les scrollbars
        self.cadrecanevas=Frame(self.cadrepartie)
        # on crée les scrollbar AVANT le canevas de jeu car le canevas est dépendant de leur
        self.scrollV=Scrollbar(self.cadrecanevas,orient=VERTICAL)
        self.scrollH=Scrollbar(self.cadrecanevas,orient=HORIZONTAL)
        self.canevas=Canvas(self.cadrecanevas,width=400,height=400,bg="DarkOliveGreen2",
                            yscrollcommand = self.scrollV.set,
                            xscrollcommand = self.scrollH.set )
        self.scrollV.config( command = self.canevas.yview)
        self.scrollH.config( command = self.canevas.xview)
        # on visualise utilisant grid (grille)
        # le grid avec 'sticky' indique que l'objet doit s'acroitre pour coller aux 'points cardinaux' (anglais)
        self.canevas.grid(row=1,column=0,sticky=N+S+E+W)
        self.scrollV.grid(row=1,column=1,sticky=N+S)
        self.scrollH.grid(row=2,column=0,sticky=E+W)

        # visualise le cadre qui contient le canevas de jeu
        self.cadrecanevas.grid(column=0,row=0,sticky=N+S+E+W)
        # on doit preciser quelle partie de la grille (grid) va s'accroitre, colonne et rangée
        # ici on precise que c'est le canevas et non les scrollbar qui doit s'agrandir
        self.cadrecanevas.rowconfigure(1, weight=1)
        self.cadrecanevas.columnconfigure( 0, weight=1)
        self.connecter_event()

    def creer_HUD(self):
        self.cadrejeuinfo=Frame(self.cadrecanevas,bg="light gray")
        #des etiquettes d'info
        self.infohudnourriture = {"Viande": None,
                      "Framboises": None,
                      "Bleuets": None,
                      "Champignons": None}
        self.infohudbois = {"Bois": None,
                            "Bois de base": None,
                            "Bois fin": None}
        self.infohudpierremetaux = {"Cuivre": None,
                                    "Etain": None,
                                    "Fer": None,
                                    "Roche": None,
                                    "Silex": None,
                                    "charbon":None}

        # fonction interne uniquement pour reproduire chaque info de ressource
        def creer_champ_interne(listechamp, categorie_ressource):
            titre = Champ(self.cadrejeuinfo, text="   " + listechamp, bg="snow", fg="grey1")
            varstr = StringVar()
            varstr.set(0)
            donnee = Champ(self.cadrejeuinfo, bg="snow", fg="grey50", textvariable=varstr)
            titre.pack(side=LEFT)
            donnee.pack(side=LEFT)
            if categorie_ressource == "nourriture":
                self.infohudnourriture[listechamp] = [varstr, donnee]
            elif categorie_ressource == "bois":
                self.infohudbois[listechamp] = [varstr, donnee]
            elif categorie_ressource == "pierremetal":
                self.infohudpierremetaux[listechamp] = [varstr, donnee]

        ## on l'appelle pour chaque chose de self.infohud
        for i in self.infohudnourriture.keys():
            creer_champ_interne(i, "nourriture")
        for i in self.infohudpierremetaux.keys():
            creer_champ_interne(i, "pierremetal")
        for i in self.infohudbois.keys():
            creer_champ_interne(i, "bois")

        varstr=StringVar()
        varstr.set("")
        ### champ supplémentaire pour afficher des messages...
        champmsg = Label(self.cadrejeuinfo, text="",fg="red")
        champmsg.pack(side=LEFT)
        self.infohudnourriture["msggeneral"]=[champmsg]

        self.btnchat = Button(self.cadrejeuinfo, text="Chat", command=self.action.chatter)
        self.btnaide = Button(self.cadrejeuinfo, text="Aide", command=self.action.aider)
        self.btncraft = Button(self.cadrejeuinfo, text="Craft", command=self.action.crafter)
        self.btnaide.pack(side=RIGHT)
        self.btnchat.pack(side=RIGHT)
        self.btncraft.pack(side=RIGHT)

        self.cadrejeuinfo.grid(row=0, column=0, sticky=E+W)

    def creer_cadre_jeu_action(self):
        # Ajout du cadre d'action a droite pour identifier les objets permettant les commandes du joueur
        self.cadreaction=Frame(self.cadrepartie)
        self.cadreaction.grid(row=0, column=1, sticky=N+S)
        self.scrollVaction=Scrollbar(self.cadreaction,orient=VERTICAL)
        self.canevasaction=Canvas(self.cadreaction,width=200,height=300,bg="lightblue",
                            yscrollcommand=self.scrollVaction.set)

        self.scrollVaction.config( command = self.canevasaction.yview)
        self.canevasaction.grid(row=0,column=0, sticky=N+S)
        self.scrollVaction.grid(row=0,column=1, sticky=N+S)
        # les widgets
        self.canevasaction.create_text(100, 30, text=self.parent.monnom, font=("arial", 18, "bold"), anchor=S, tags=("nom"))

        # minicarte
        self.minicarte=Canvas(self.cadreaction, width=self.tailleminicarte, height=self.tailleminicarte, bg="tan1", highlightthickness=0)
        self.minicarte.grid(row=2, column=0)
        self.minicarte.bind("<Button-1>", self.deplacer_carte)

        # on retourne ce cadre pour l'insérer dans le dictionnaires des cadres
        self.canevasaction.rowconfigure(0, weight=1)
        self.cadreaction.rowconfigure(0, weight=1)

    def connecter_event(self):
        # actions de clics sur la carte
        self.canevas.bind("<Button-1>", self.annuler_action)
        self.canevas.bind("<Button-2>", self.indiquer_position)
        self.canevas.bind("<Button-3>", self.construire_batiment)
        # faire une multiselection
        self.canevas.bind("<Shift-Button-1>", self.debuter_multiselection)
        self.canevas.bind("<Shift-B1-Motion>", self.afficher_multiselection)
        self.canevas.bind("<Shift-ButtonRelease-1>", self.terminer_multiselection)
        # scroll avec roulette
        self.canevas.bind("<MouseWheel>", self.defiler_vertical)
        self.canevas.bind("<Control-MouseWheel>", self.defiler_horizon)

        # acgtions liées aux objets dessinés par tag
        self.canevas.tag_bind("batiment", "<Button-1>", self.creer_entite)
        self.canevas.tag_bind("perso", "<Button-1>", self.ajouter_selection)
        self.canevas.tag_bind("bois", "<Button-1>", self.ramasser_ressource)
        self.canevas.tag_bind("roche", "<Button-1>", self.ramasser_ressource)
        self.canevas.tag_bind("cuivre", "<Button-1>", self.ramasser_ressource)
        self.canevas.tag_bind("framboises", "<Button-1>", self.ramasser_ressource)
        self.canevas.tag_bind("bleuets", "<Button-1>", self.ramasser_ressource)
        self.canevas.tag_bind("champignons", "<Button-1>", self.ramasser_ressource)
        self.canevas.tag_bind("eau", "<Button-1>", self.ramasser_ressource)
        self.canevas.tag_bind("daim", "<Button-1>", self.chasser_ressource)
        self.canevas.tag_bind("fournaise", "<Button-1>", self.ramasser_ressource)

        self.canevas.bind("<Control-Button-1>", self.parent.montrer_stats)

    def defiler_vertical(self, evt):
        rep = self.scrollV.get()[0]
        if evt.delta < 0:
            rep = rep + 0.01
        else:
            rep = rep - 0.01
        self.canevas.yview_moveto(rep)

    def defiler_horizon(self, evt):
        rep = self.scrollH.get()[0]
        if evt.delta < 0:
            rep = rep + 0.02
        else:
            rep = rep - 0.02
        self.canevas.xview_moveto(rep)

    ### cadre qui s'Affichera par-dessus le canevas de jeu pour l'aide
    def creer_aide(self):
        self.cadreaide=Frame(self.canevas)
        self.scrollVaide=Scrollbar(self.cadreaide,orient=VERTICAL)
        self.textaide=Text(self.cadreaide,width=50,height=10,
                            yscrollcommand = self.scrollVaide.set )
        self.scrollVaide.config(command = self.textaide.yview)
        self.textaide.pack(side=LEFT)
        self.scrollVaide.pack(side=LEFT,expand=1, fill=Y)
        fichieraide=open("aide.txt")
        monaide=fichieraide.read()
        fichieraide.close()
        self.textaide.insert(END, monaide)
        self.textaide.config(state=DISABLED)

    ### cadre qui affichera un chatbox
    def creer_chatter(self):
        self.cadrechat=Frame(self.canevas,bd=2,bg="orange")
        self.cadrechatlist=Frame(self.cadrechat)

        self.scrollVchat=Scrollbar(self.cadrechatlist,orient=VERTICAL)
        self.textchat=Listbox(self.cadrechatlist,width=30,height=6,
                            yscrollcommand = self.scrollVchat.set )
        self.scrollVchat.config(command = self.textchat.yview)
        self.textchat.pack(side=LEFT)
        self.scrollVchat.pack(side=LEFT,expand=1, fill=Y)
        self.textchat.delete(0, END)
        self.cadrechatlist.pack()
        # inscrire texte et choisir destinataire
        self.cadreparler=Frame(self.cadrechat,bd=2)
        self.joueurs=ttk.Combobox(self.cadreparler,
                                  values=list(self.modele.joueurs.keys()))
        self.entreechat=Entry(self.cadreparler,width=20)
        self.entreechat.bind("<Return>")#,self.action.envoyerchat)
        self.joueurs.pack(expand=1,fill=X)
        self.entreechat.pack(expand=1,fill=X)
        self.cadreparler.pack(expand=1,fill=X)


    ## cadre qui affiche le menu de crafting
    def creercrafting(self):
        self.cadrecraft = Frame(self.canevas, height=300, width=300)
        self.cadrecraft.grid_propagate(0)
        self.btninventory = Button(self.cadrecraft, text="Inventaire")
        self.btncraft = Button(self.cadrecraft, text="Crafting", command=self.subcrafting)
        self.btninventory.grid(column=0, row=0, padx=2)
        self.btncraft.grid(column=1, row=0, padx=2)

    def subcrafting(self):
        self.cadresubcraft = Frame(self.cadrecraft, height=250, width=250, bg="blue")
        self.cadresubcraft.grid_propagate(0)
        self.craftinglabels = []
        self.craftinreqlabels = []
        for j in self.modele.joueurs.keys():
            if j==self.parent.monnom:
                clemaison = self.modele.joueurs[j].batiments["maison"].keys()
                cle = list(clemaison)[0]
                maison= self.modele.joueurs[j].batiments["maison"][cle]

                for k in maison.recettespossible:
                    recettenomlabel = Label(self.cadresubcraft, text=k)
                    keyslist = list(self.modele.partie.recettes[k])
                    reqtext = ""
                    for key in keyslist:
                        reqtext += key + ": " + maison.inventaire[key] + "/" + self.modele.partie.recettes[k][key] + ", "
                        recetterequislabel = Label(self.cadresubcraft, text=reqtext)
                        self.craftinglabels.append(recetterequislabel)

                    self.craftinglabels.append(recettenomlabel)


        self.cadresubcraft.grid(column=2, row=3)
        for label in self.craftinglabels:
            label.grid()
        for label in self.craftinreqlabels:
            label.grid()


##### FONCTIONS DU SPLASH #########################################################################
    def creer_partie(self):
        nom=self.nomsplash.get()
        self.parent.creer_partie(nom)

    ###  FONCTIONS POUR SPLASH ET LOBBY INSCRIPTION pour participer a une partie
    def update_splash(self,etat):
        if "attente" in etat or "courante" in etat:
            self.btncreerpartie.config(state=DISABLED)
        if "courante" in etat:
            self.etatdujeu.config(text="Desole - partie encours !")
            self.btninscrirejoueur.config(state=DISABLED)
        elif "attente" in etat:
            self.etatdujeu.config(text="Partie en attente de joueurs !")
            self.btninscrirejoueur.config(state=NORMAL)
        elif "dispo" in etat:
            self.etatdujeu.config(text="Bienvenue ! Serveur disponible")
            self.btninscrirejoueur.config(state=DISABLED)
            self.btncreerpartie.config(state=NORMAL)
        else:
            self.etatdujeu.config(text="ERREUR - un probleme est survenu")

    ##### FONCTION DU LOBBY #############
    def update_lobby(self,dico):
        self.listelobby.delete(0,END)
        for i in dico:
            self.listelobby.insert(END,i[0])
        if self.parent.joueur_createur:
            self.btnlancerpartie.config(state=NORMAL)

    def inscrire_joueur(self):
        nom=self.nomsplash.get()
        urljeu=self.urlsplash.get()
        self.parent.inscrire_joueur(nom,urljeu)

    def lancer_partie(self):
        self.parent.lancer_partie()

    def reset_partie(self):
        rep=self.parent.reset_partie()

    def initialiser_avec_modele(self,modele):
        self.modele=modele
        # on reassigne le nom final localement pour eviter
        # de toujours le requerir du parent
        self.monnom=self.parent.monnom
        # on ajuste la taille du canevas de jeu
        self.canevas.config(scrollregion=(0,0,self.modele.aireX,self.modele.aireY))
        self.canevasaction.delete("nom")
        self.canevasaction.create_text(100,30,text=self.monnom,font=("arial",18,"bold"),anchor=S,tags=("nom"))

        # on cree les cadres affichant les items d'actions du joueur
        # cadre apparaissant si on selectionne un ouvrier
        coul=self.modele.joueurs[self.parent.monnom].couleur
        self.cadrejeuinfo.config(bg=coul[1])
        self.creer_aide()
        self.creer_cadre_ouvrier(coul[0]+"_",["maison","caserne","abri","usineballiste","forge", "fournaise"])
        self.creer_chatter()
        self.creercrafting()
        # on affiche les maisons, point de depart des divers joueurs
        self.afficher_depart()
        self.root.update()
        #self.centrer_maison()

    def creer_cadre_ouvrier(self,coul,artefacts):
        self.cadreouvrier=Frame(self.canevasaction)
        for i in artefacts:
            btn=Button(self.cadreouvrier,text=i,image=self.images[coul+i])
            btn.bind("<Button>",self.batir_artefact)
            btn.pack()

    ##FONCTIONS D'AFFICHAGES##################################
    def afficher_depart(self):
        self.modele.listebiotopes.sort(key = lambda c: c.y)
        for i in self.modele.listebiotopes:
            if i.montype=="daim":
                monitem=self.canevas.create_image(i.x,i.y,image=self.images[i.img],anchor=S,
                                                  tags=("mobile","",i.id,"biotope",i.montype,""))
                                                  #tags=("mobile","",i.id,)
            else:
                monitem=self.canevas.create_image(i.x,i.y,image=self.images[i.img],anchor=S,
                                                  tags=("statique","",i.id,"biotope",i.montype,""))
                                                  #tags=("mobile","",i.id,)

        self.modele.listebiotopes=[]
        minitaillecase=int(self.tailleminicarte/self.modele.taillecarte)
        couleurs={0:"",
                  "bois":"light green",
                  "eau":"light blue",
                  "aureus":"tan",
                  "roche":"gray30",
                  "cuivre": "DarkOrange3",
                  "marais":"seagreen"}
        for i,t in enumerate(self.modele.regions):
            if t!="plaine":
                for j,c in enumerate(self.modele.regions[t]):
                    for cle,k in self.modele.regions[t][c].dicocases.items():
                        y1=k.y*minitaillecase
                        y2=y1+minitaillecase
                        x1=k.x*minitaillecase
                        x2=x1+minitaillecase
                        self.minicarte.create_rectangle(x1,y1,x2,y2,outline="",
                                                        #fill=couleurs[self.modele.cartecase[k[1]][k[0]].type]),
                                                        fill=couleurs[k.parent.montype])

        # Affichage des batiments intiaux sur l'aire de jeu et sur la minicarte
        px=int(self.tailleminicarte/self.modele.aireX)
        py=int(self.tailleminicarte/self.modele.aireY)

        for j in self.modele.joueurs.keys():
            for i in self.modele.joueurs[j].batiments["maison"].keys():
                m=self.modele.joueurs[j].batiments["maison"][i]
                coul=self.modele.joueurs[j].couleur[0]
                self.canevas.create_image(m.x,m.y,image=self.images[coul+"_maison"],
                                          tags=("statique",j,m.id,"batiment",m.montype,""))
                                          #tags=("mobile","",i.id,)
                # afficher sur minicarte
                coul=self.modele.joueurs[j].couleur[1]
                x1=int((m.x/self.modele.aireX)*self.tailleminicarte)
                y1=int((m.y/self.modele.aireY)*self.tailleminicarte)
                self.minicarte.create_rectangle(x1-2,y1-2,x1+2,y1+2,fill=coul,tags=(j,m.id,"artefact","maison"))

    def afficher_bio(self,bio):
        self.canevas.create_image(bio.x,bio.y,image=self.images[bio.img],tags=("statique","",bio.id,"biotope",bio.montype,""))

    def afficher_batiment(self,joueur,batiment):
        coul=self.modele.joueurs[joueur].couleur[0]

        self.canevas.delete(batiment.id)

        print(self.parent.monnom)
        chose=self.canevas.create_image(batiment.x,batiment.y,image=self.images[batiment.image],
                                  tags=("statique",self.parent.monnom,batiment.id,"batiment",batiment.montype,""))

        x0, y0, x2, y2 = self.canevas.bbox(chose)

        couleurs={0:"",
                  1:"light green",
                  2:"light blue",
                  3:"tan",
                  4:"gray30",
                  5:"orange"}
        coul=self.modele.joueurs[joueur].couleur[1]
        x1=int((batiment.x/self.modele.aireX)*self.tailleminicarte)
        y1=int((batiment.y/self.modele.aireY)*self.tailleminicarte)
        self.minicarte.create_rectangle(x1-2,y1-2,x1+2,y1+2,fill=coul,tags=(self.parent.monnom,batiment.id,"artefact",batiment.montype))
        return [x0, y0, x2, y2]

    def afficher_jeu(self):

        # On efface tout ce qui est 'mobile' (un tag)
        self.canevas.delete("mobile")

        # on se debarrasse des choses mortes (disparues), le id est dans le tag du dessin
        for i in self.modele.ressourcemorte:
            self.canevas.delete(i.id)

        # commencer par les choses des joueurs
        for j in self.modele.joueurs.keys():
            # ajuster les infos du HUD
            if j == self.parent.monnom:
                self.infohudnourriture["Viande"][0].set(self.modele.joueurs[j].ressources["viande"])
                self.infohudnourriture["Framboises"][0].set(self.modele.joueurs[j].ressources["framboises"])
                self.infohudnourriture["Bleuets"][0].set(self.modele.joueurs[j].ressources["bleuets"])
                self.infohudnourriture["Champignons"][0].set(self.modele.joueurs[j].ressources["champignons"])
                self.infohudnourriture["msggeneral"][0].config(text=self.modele.msggeneral)
                self.infohudbois["Bois"][0].set(self.modele.joueurs[j].ressources["bois"])
                self.infohudbois["Bois de base"][0].set(self.modele.joueurs[j].ressources["boisdebase"])
                self.infohudbois["Bois fin"][0].set(self.modele.joueurs[j].ressources["boisfin"])
                self.infohudpierremetaux["Cuivre"][0].set(self.modele.joueurs[j].ressources["cuivre"])
                self.infohudpierremetaux["Etain"][0].set(self.modele.joueurs[j].ressources["etain"])
                self.infohudpierremetaux["Fer"][0].set(self.modele.joueurs[j].ressources["fer"])
                self.infohudpierremetaux["Roche"][0].set(self.modele.joueurs[j].ressources["roche"])
                self.infohudpierremetaux["Silex"][0].set(self.modele.joueurs[j].ressources["silex"])
                self.infohudpierremetaux["charbon"][0].set(self.modele.joueurs[j].ressources["charbon"])

            # ajuster les constructions de chaque joueur
            for p in self.modele.joueurs[j].batiments['siteconstruction']:
                s=self.modele.joueurs[j].batiments['siteconstruction'][p]
                if s.etat=="attente":
                    self.canevas.create_image(s.x,s.y,anchor=CENTER,image=self.images["siteX"],
                                              tags=("mobile",j,p,"batiment",type(s).__name__,""))
                                              #tags=(j,s.id,"artefact","mobile","siteconstruction","batiments"))
                else:
                    self.canevas.create_image(s.x,s.y,anchor=CENTER,image=self.images["EnConstruction"],
                                              tags=("mobile",j,p,"batiment",type(s).__name__,""))

            # ajuster les persos de chaque joueur et leur dépendance (ici javelots des ouvriers)
            for p in self.modele.joueurs[j].persos.keys():
                for k in self.modele.joueurs[j].persos[p].keys():
                    i=self.modele.joueurs[j].persos[p][k]
                    coul=self.modele.joueurs[j].couleur[0]
                    self.canevas.create_image(i.x,i.y,anchor=S,image=self.images[i.image],
                                              tags=("mobile",j,k,"perso",type(i).__name__,""))
                                              #tags=(j,k,"artefact","mobile","perso",p))
                    if k in self.action.persochoisi:
                        self.canevas.create_rectangle(i.x-10,i.y+5,i.x+10,i.y+10,fill="yellow",
                                                      tags=("mobile",j,p,"perso",type(i).__name__,"persochoisi"))
                                                      #tags=(j,k,"artefact","mobile","persochoisi"))

                    # dessiner javelot de l'ouvrier
                    if p=="ouvrier":
                        for b in self.modele.joueurs[j].persos[p][k].javelots:
                            self.canevas.create_image(b.x,b.y,image=self.images[b.image],
                                                      tags=("mobile",j,b.id,"",type(b).__name__,""))
                                              #tags=(j,b.id,"artefact","mobile","javelot"))


        # ajuster les choses vivantes dependantes de la partie (mais pas des joueurs)
        for j in self.modele.biotopes["daim"].keys():
            i=self.modele.biotopes["daim"][j]
            if i.etat=="mort":
                self.canevas.create_image(i.x,i.y,image=self.images["daimMORT"],
                                          tags=("mobile","",i.id,"biotope",i.montype,""))
                                          #tags=("",i.id,"artefact","daim","mobile"))

            else:
                self.canevas.create_image(i.x,i.y,image=self.images[i.img],
                                          tags=("mobile","",i.id,"biotope",i.montype,""))
                                          #tags=("",i.id,"artefact","daim","mobile"))


        # ajuster les choses vivantes dependantes de la partie (mais pas des joueurs)
        for j in self.modele.biotopes["eau"].keys():
            i=self.modele.biotopes["eau"][j]
            if i.sprite:
                self.canevas.create_image(i.x,i.y,image=self.gifs[i.sprite][i.spriteno],
                                          tags=("mobile","",i.id,"biotope",type(i).__name__,""))
                                          #tags=("",i.id,"artefact","eau","mobile"))

        # mettre les chat a jour si de nouveaux messages sont arrives
        if self.textchat and self.modele.joueurs[self.parent.monnom].chatneuf:
            self.textchat.delete(0, END)
            self.textchat.insert(END, *self.modele.joueurs[self.parent.monnom].monchat)
            if self.modele.joueurs[self.parent.monnom].chatneuf and self.action.chaton==0:
                self.btnchat.config(bg="orange")
            self.modele.joueurs[self.parent.monnom].chatneuf=0

    def centrer_maison(self):
        self.root.update()
        cle=list(self.modele.joueurs[self.monnom].batiments["maison"].keys())[0]
        x=self.modele.joueurs[self.monnom].batiments["maison"][cle].x
        y=self.modele.joueurs[self.monnom].batiments["maison"][cle].y

        x1=self.canevas.winfo_width()/2
        y1=self.canevas.winfo_height()/2

        pctx=(x-x1)/self.modele.aireX
        pcty=(y-y1)/self.modele.aireY

        self.canevas.xview_moveto(pctx)
        self.canevas.yview_moveto(pcty)


##### ACTIONS DU JOUEUR #######################################################################

    def annuler_action(self,evt):
        mestags=self.canevas.gettags(CURRENT)
        if not mestags:
            self.canevasaction.delete(self.action.widgetsactifs)
            if self.action.btnactif:
                self.action.btnactif.config(bg="SystemButtonFace")
            self.action=Action(self)

    def fermer_chat(self):
        self.textchat=None
        self.fenchat.destroy()

    def ajouter_selection(self,evt):
        mestags=self.canevas.gettags(CURRENT)
        if self.parent.monnom == mestags[1]:
            if "Ouvrier" == mestags[4]:
                self.action.persochoisi.append(mestags[2])
                self.action.afficher_commande_perso()
        ######
            else:
                self.action.persochoisi.append(mestags[2])

        # BUG quand on attaque
        # elif self.action.persochoisi!= []:
        #     self.action.ciblechoisi=mestags
        #     self.action.attaquer()

    # Methodes pour multiselect
    def debuter_multiselection(self,evt):
        self.debutselect=(self.canevas.canvasx(evt.x),self.canevas.canvasy(evt.y))
        x1,y1=(self.canevas.canvasx(evt.x),self.canevas.canvasy(evt.y))
        self.selecteuractif=self.canevas.create_rectangle(x1,y1,x1+1,y1+1,outline="red",width=2,
                                                          dash=(2,2),tags=("","selecteur","","artefact"))


    def afficher_multiselection(self,evt):
        if self.debutselect:
            x1,y1=self.debutselect
            x2,y2=(self.canevas.canvasx(evt.x),self.canevas.canvasy(evt.y))
            self.canevas.coords(self.selecteuractif,x1,y1,x2,y2)

    def terminer_multiselection(self,evt):
        if self.debutselect:
            x1,y1=self.debutselect
            x2,y2=(self.canevas.canvasx(evt.x),self.canevas.canvasy(evt.y))
            self.debutselect=[]
            objchoisi=(list(self.canevas.find_enclosed(x1,y1,x2,y2)))
            for i in objchoisi:
                if self.parent.monnom not in self.canevas.gettags(i):
                    objchoisi.remove(i)
                else:
                    self.action.persochoisi.append(self.canevas.gettags(i)[2])

            if self.action.persochoisi:
                self.action.afficher_commande_perso()
            self.canevas.delete("selecteur")
    ### FIN du multiselect

    def ramasser_ressource(self,evt):
        tag=self.canevas.gettags(CURRENT)
        if tag[1]=="" and self.action.persochoisi:
            self.action.ramasser_ressource(tag)
        else:
            print(tag[4])

    def chasser_ressource(self,evt):
        tag=self.canevas.gettags(CURRENT)
        if tag[1]=="" and self.action.persochoisi and tag[4]=="daim":
            self.action.chasser_ressource(tag)
        else:
            print(tag[3])

    def indiquer_position(self,evt):
        tag=self.canevas.gettags(CURRENT)
        if not tag and self.action.persochoisi:
            x,y=(self.canevas.canvasx(evt.x),self.canevas.canvasy(evt.y))
            self.action.position=[x,y]
            self.action.deplacer()

    # Cette fonction permet se se deplacer via un click sur la minicarte
    def deplacer_carte(self,evt):
        x=evt.x
        y=evt.y

        pctx=x/self.tailleminicarte
        pcty=y/self.tailleminicarte

        xl=(self.canevas.winfo_width()/2)/self.modele.aireX
        yl=(self.canevas.winfo_height()/2)/self.modele.aireY

        self.canevas.xview_moveto(pctx-xl)
        self.canevas.yview_moveto(pcty-yl)
        xl=self.canevas.winfo_width()
        yl=self.canevas.winfo_height()

    def batir_artefact(self,evt):
        # on obtient l'information du bouton de menu cliquer
        obj=evt.widget
        if self.action.btnactif: # si un autre bouton etait deja choisi
            if self.action.btnactif != obj: # et qu'il est different du nouveau
                self.action.btnactif.config(bg="SystemButtonFace") # change couleur pour deselection du precedent
        #test de cout a cet endroit
        nomsorte=obj.cget("text") # on utilise pour identifier la sorte de batiment à produire
        self.action.btnactif=obj

        #on valide qu'on a assez de ressources pour construire
        vals=self.parent.trouver_valeurs()
        ok=1
        for k,val in self.modele.joueurs[self.monnom].ressources.items():
            if val != 0 and val<= vals[nomsorte][k]:
                ok=0 # on indique qu'on a PAS les ressources
                break
        if ok:
            self.action.prochaineaction=obj.cget("text")
            obj.config(bg="lightgreen")
        else:
            self.action.btnactif.config(bg="SystemButtonFace")
            print("VOUS N'AVEZ PAS ASSEZ DE",k)

    def construire_batiment(self,evt):
        mestags=self.canevas.gettags(CURRENT)
        if not mestags and self.action.persochoisi and self.action.prochaineaction:
            pos=(self.canevas.canvasx(evt.x),self.canevas.canvasy(evt.y))
            self.action.construire_batiment(pos)

    def creer_entite(self,evt):
        x,y=evt.x,evt.y
        mestags=self.canevas.gettags(CURRENT)
        if self.parent.monnom in mestags:
            if "batiment" in mestags:
                if "maison" in mestags:
                    pos=(self.canevas.canvasx(evt.x),self.canevas.canvasy(evt.y))
                    action=[self.parent.monnom,"creerperso",["ouvrier",mestags[4],mestags[2],pos]]
                if "caserne" in mestags:
                    pos=(self.canevas.canvasx(evt.x),self.canevas.canvasy(evt.y))
                    action=[self.parent.monnom,"creerperso",["soldat",mestags[4],mestags[2],pos]]
                if "abri" in mestags:
                    pos=(self.canevas.canvasx(evt.x),self.canevas.canvasy(evt.y))
                    action=[self.parent.monnom,"creerperso",["druide",mestags[4],mestags[2],pos]]
                if "usineballiste" in mestags:
                    pos=(self.canevas.canvasx(evt.x),self.canevas.canvasy(evt.y))
                    action=[self.parent.monnom,"creerperso",["ballista",mestags[4],mestags[2],pos]]
                if "fournaise" in mestags:
                    pos = (self.canevas.canvasx(evt.x), self.canevas.canvasy(evt.y))
                    action = [self.parent.monnom, "convertirbois", ["ouvrier", mestags[4], mestags[2], pos]]
                if "forge" in mestags:
                    actionsPossiblesForges = ["creerarmes", "creerarmures", "creeroutils"]
                    choixAleatoire = random.choice(actionsPossiblesForges)
                    pos = (self.canevas.canvasx(evt.x), self.canevas.canvasy(evt.y))
                    action = [self.parent.monnom, choixAleatoire, [mestags[4], mestags[2], pos]]

                self.parent.actionsrequises.append(action)
        ###### les ATTAQUES SUR BATIMENT INACTIFS
        # elif self.action.persochoisi:
        #     self.action.ciblechoisi=mestags
        #     self.action.attaquer()

# Singleton (mais pas automatique) sert a conserver les manipulations du joueur pour demander une action
######   CET OBJET SERVIRA À CONSERVER LES GESTES ET INFOS REQUISES POUR PRODUIRE UNE ACTION DE JEU
class Action():
    def __init__(self,parent):
        self.parent=parent
        self.persochoisi=[]
        self.ciblechoisi=None
        self.position=[]
        self.btnactif=None  # le bouton choisi pour creer un batiment
        self.prochaineaction=None # utiliser pour les batiments seulement
        self.widgetsactifs=[]
        self.chaton=0
        self.aideon=0
        self.craftwindow=0
        self.craftwindowtoggle=0

    def attaquer(self):
        if self.persochoisi:
            qui=self.ciblechoisi[1]
            cible=self.ciblechoisi[2]
            sorte=self.ciblechoisi[5]
            action=[self.parent.parent.monnom,"attaquer",[self.persochoisi,[qui,cible,sorte]]]
            self.parent.parent.actionsrequises.append(action)

    def deplacer(self):
        if self.persochoisi:
            action=[self.parent.parent.monnom,"deplacer",[self.position,self.persochoisi]]
            self.parent.parent.actionsrequises.append(action)

    def chasser_ressource(self,tag):
        if self.persochoisi:
            action=[self.parent.parent.monnom,"chasserressource",[tag[4],tag[2],self.persochoisi]]
            self.parent.parent.actionsrequises.append(action)

    def ramasser_ressource(self,tag):
        if self.persochoisi:
            action=[self.parent.parent.monnom,"ramasserressource",[tag[4],tag[2],self.persochoisi]]
            self.parent.parent.actionsrequises.append(action)

    def construire_batiment(self,pos):
        self.btnactif.config(bg="SystemButtonFace")
        self.btnactif=None
        action=[self.parent.monnom,"construirebatiment",[self.persochoisi,self.prochaineaction,pos]]
        self.parent.parent.actionsrequises.append(action)

    def afficher_commande_perso(self):
        self.widgetsactifs=self.parent.canevasaction.create_window(100,60,
                                                window=self.parent.cadreouvrier,
                                                anchor=N)
        self.parent.root.update()
        fh=self.parent.cadreouvrier.winfo_height()
        ch=int(self.    parent.canevasaction.cget("height"))
        if fh+60>ch:
            cl=int(self.parent.canevasaction.cget("width"))
            self.parent.canevasaction.config(scrollregion=(0,0,cl,fh+60))


    def envoyer_chat(self,evt):
        txt=self.parent.entreechat.get()
        joueur=self.parent.joueurs.get()
        if joueur:
            action=[self.parent.monnom,"chatter",[self.parent.monnom+": "+txt,self.parent.monnom,joueur]]
            self.parent.parent.actionsrequises.append(action)

    def chatter(self):
        if self.chaton==0:
            x1,x2=self.parent.scrollH.get()
            x3=self.parent.modele.aireX*x1
            y1,y2=self.parent.scrollV.get()
            y3=self.parent.modele.aireY*y1
            self.parent.cadrechaton=self.parent.canevas.create_window(x3,y3,
                                                window=self.parent.cadrechat,
                                                anchor=N+W)
            self.parent.btnchat.config(bg="SystemButtonFace")
            self.chaton=1
        else:
            self.parent.canevas.delete(self.parent.cadrechaton)
            self.parent.cadrechaton=0
            self.chaton=0

    def aider(self):
        if self.aideon==0:
            x1,x2=self.parent.scrollH.get()
            x3=self.parent.modele.aireX*x2
            y1,y2=self.parent.scrollV.get()
            y3=self.parent.modele.aireY*y1
            self.aideon=self.parent.canevas.create_window(x3,y3,
                                                window=self.parent.cadreaide,
                                                anchor=N+E)
        else:
            self.parent.canevas.delete(self.aideon)
            self.aideon=0

    def crafter(self):
        if self.craftwindowtoggle == 0:
            x1, x2 = self.parent.scrollH.get()
            x3 = self.parent.modele.aireX * x2
            y1, y2 = self.parent.scrollV.get()
            y3 = self.parent.modele.aireY * y1
            self.craftwindow = self.parent.canevas.create_window(x3, y3, window=self.parent.cadrecraft, anchor= N + E)
            self.craftwindowtoggle = 1

        else:
            self.parent.canevas.delete(self.craftwindow)
            self.craftwindowtoggle = 0



    ### FIN des methodes pour lancer la partie

class Champ(Label):
    def __init__(self,master,*args, **kwargs):
        Label.__init__(self,master,*args, **kwargs)
        self.config(font=("arial",13,"bold"))
        #self.config(bg="goldenrod3")

