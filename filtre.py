import os
import re
from subprocess import Popen, PIPE

class Scenario:

    def __init__(self):

        self.date         = "none"
        self.auteur       = "none"
        self.indice       = "none"
        self.description  = "none"
        self.nomProg      = "none"
        self.numProg      = "none"

    def update(self,nomScenario):

        self.nomScenario = nomScenario

        self.nomFichier = os.path.basename(self.nomScenario)
        
        #Récupère le contenu du scénario.
        self.scenario  = open(self.nomScenario,"r")
        self.cScenario = self.scenario.readlines()
        self.scenario.close()

        #Récupère uniquement la cartouche des évolutions à partir du scénario.

        self.lst_cartouche = []

        for self.line in self.cScenario:            
    
            self.tmpLine = (self.line.strip())

            if(re.findall("Programme", self.tmpLine)):
                self.nomProg = self.tmpLine
                self.nomProg = self.nomProg.split(":")
                self.nomProg = self.nomProg[1].strip()

            if(re.findall("Num", self.tmpLine)):
                self.numProg = self.tmpLine
                self.numProg = self.numProg.split(":")
                self.numProg = self.numProg[1].strip()

            if(len(self.tmpLine.split("|")) == 5):
                self.lst_cartouche.append(self.tmpLine.split("|"))
    
            if(re.findall("}", self.tmpLine)):
                break

        #Récupère les lignes de la cartouche sauf la ligne vide.
        self.lst_new = []
        self.vide = True

        for self.con in self.lst_cartouche:
                
            for self.elmt in self.con:
                if(self.elmt.strip() != ""):
                    self.vide = False

            if(self.vide == False):
                self.lst_new.append(self.con)
                self.vide = True

        #Récupère la dernière ligne d'évolution.
        self.lst_lastUpdate = self.lst_new[len(self.lst_new)-1]

        #Supprime les cases vide.
        self.lst_lastUpdate = [self.i.strip() for self.i in self.lst_lastUpdate if(self.i.strip() != "")]

        #Récupère et affecte les valeurs.
        self.date, self.auteur, self.indice, self.description = (self.lst_lastUpdate)

class Git():

    def __init__(self,repository):

        #Répertoire contenant le .git
        self.repository = repository

        #Initialisation des attributs
        self._sha         = ""
        self._auteur      = ""
        self._date        = ""
        self._description = ""
        self.mail         = ""

        self._nbeCommit   = 0

        #Récupération du dernier commit
        self.commit(0)    

    def gitCmd(self,cmd):

        """Cette fonction permet d'envoyer des requêtes à git et renvoie un retour."""

        #Attributs
        self.git_response = ""
        self.error        = ""

        #Attribut contenant la requête
        self.cmd          = cmd
        
        self.git_command  = ['C:/Program Files/Git/bin/git.exe',self.cmd]

        self.git_query = Popen(self.git_command, cwd=self.repository, stdout=PIPE, stderr=PIPE, shell=True)
        (self.git_response, self.error) = self.git_query.communicate()

        return((self.git_response.decode("utf-8")))

    def formatDate(self,sDate):

        """Cette fonction récupère la réponse de git en renvoie une date au format AAAA-MM-DD."""

        self.sDate = sDate
        
        self.date = []
        self.date = self.sDate.split(" ")

        self.date = [ self.i for self.i in self.date if self.i != ""]

        self.mois  = self.date[2]

        if(self.mois.upper() == "JAN"):
            self.mois = "01"
        if(self.mois.upper() == "FEB"):
            self.mois = "02"
        if(self.mois.upper() == "MAR"):
            self.mois = "03"
        if(self.mois.upper() == "APR"):
            self.mois = "04"        
        if(self.mois.upper() == "MAY"):
            self.mois = "05"
        if(self.mois.upper() == "JUN"):
            self.mois = "06"
        if(self.mois.upper() == "JUL"):
            self.mois = "07"
        if(self.mois.upper() == "AUG"):
            self.mois = "08"
        if(self.mois.upper() == "SEP"):
            self.mois = "09"
        if(self.mois.upper() == "OCT"):
            self.mois = "10"
        if(self.mois.upper() == "NOV"):
            self.mois = "11"
        if(self.mois.upper() == "DEC"):
            self.mois = "12"        
    
        self.jour  = self.date[3]
        if(len(self.jour) == 1):
            self.jour = "0" + self.jour
        self.annee = self.date[5]
        return(self.annee+"-"+self.mois+"-"+self.jour)

    def formatAuthor(self,sAuthor, typeInfo):
        
        """
        Cette fonction récupère une chaîne de caractère et renvoie :
        - soit le nom de l'auteur,
        - soit le mail de l'auteur,
        en fonction du paramètre typeInfo
        """

        #Attributs
        self.sAuthor  = sAuthor
        self.typeInfo = typeInfo
        
        self.list_auteur = []
        self.list_auteur = self.sAuthor.split(" ")

        if(self.typeInfo.upper() == "NOM"):
            return(self.list_auteur[1])

        if(self.typeInfo.upper() == "MAIL"):
            self.sMail = self.list_auteur[2]
            self.sMail = self.sMail[1:-1]
            return(self.sMail)

    def commit(self, idxCommit):

        """
        Cette fonction récupère met à jour les attributs à partir de l'indice du commit :        
        """        

        self.list_log  = []
        self.idxCommit = idxCommit

        if((self._nbeCommit == 1) and (self.idxCommit != 0)):
            self.idxCommit = 0            
            print("log : only one commit exist...")

        #Vérifie que la branche courante est le master
        if(self.checkMasterBranch() == True):

            if(self.checkStatus() == True):            

                #Commande git pour récupérer le log
                self.git_response = self.gitCmd('log')

                #Conversion de la trame en string
                self.log = str(self.git_response)

                #Création d'une liste par commit
                self.log = self.log.split("commit")           

                #Parcours de la liste et suppression des cases vides de la liste.
                self.log = [self.i.strip() for self.i in self.log if self.i.strip() != "" ]

                #nbeCommit
                self._nbeCommit   = len(self.log)
   
                #Récupération du dernier commit
                self.maChaine = self.log[self.idxCommit]

                #Découpage et création d'une nouvelle liste propre
                self.sTmp = self.maChaine[:-1]                    
                self.sTmp = self.sTmp.split("\n")

                self.sTmp = [self.i.strip() for self.i in self.sTmp if self.i.strip() != "" ]

                #Debug
                """
                for self.l in self.sTmp : 
                    print("self.sTmp : "+self.l)
                """
                
                self._sha         = self.sTmp[0]
                self._auteur      = self.formatAuthor(self.sTmp[1],"NOM")
                self.mail         = self.formatAuthor(self.sTmp[1],"MAIL")
                self._date        = self.formatDate(self.sTmp[2])
                self._description = self.sTmp[3]
            else:
                print("log : commit last modification...")
        else:
            print("log : switch to the master before...")

    def checkMasterBranch(self):

        """
        Cette fonction renvoie :
        - True si la branche est sur master dans les autres cas False.
        """        

        #Commande git
        self.sBranch = (self.gitCmd('branch').strip())

        #Vérifie si c'est bien la branche master
        self.sBranch = self.sBranch.split("\n")

        try:
            self.sBranch.index("* master")
            return(True)
        except:
            return(False)

    def checkStatus(self):
        if(re.search("nothing to commit, working directory clean",self.gitCmd("status")) is not None):
            return(True)
        else:
            return(False)

    def _get_nbeCommit(self):
        return(self._nbeCommit)

    def _set_nbeCommit(self,val_Commit):
        self._nbeCommit = val_Commit

    nbeCommit = property(_get_nbeCommit,_set_nbeCommit)        

    def _get_sha(self):
        return(self._sha)

    def _set_sha(self,val_sha):
        self._sha = val_sha

    sha = property(_get_sha,_set_sha)

    def _get_auteur(self):
        return(self._auteur)

    def _set_auteur(self,val_auteur):
        self._auteur = val_auteur    

    auteur = property(_get_auteur,_set_auteur)

    def _get_mail(self):
        return(self._mail)

    def _set_mail(self,val_mail):
        self._mail = val_mail   

    mail = property(_get_mail,_set_mail)    

    def _get_date(self):        
        return(self._date)

    def _set_date(self, val_date):               
        self._date = val_date

    date = property(_get_date, _set_date)

    def _get_description(self):
        return(self._description)

    def _set_description(self, val_description):
        self._description = val_description        

    description = property(_get_description, _set_description)

def main():

    ModuleGit = Git("C:/GitHub/Test")
    print(ModuleGit.sha)
    print(ModuleGit.date)
    print(ModuleGit.auteur)
    print(ModuleGit.mail)
    print(ModuleGit.description)    
    
    programme = Scenario("C:/GitHub/DV_PPA.psc")

    print(programme.nomFichier)
    print(programme.numProg)
    print(programme.nomProg)    
    print(programme.date)
    print(programme.auteur)
    print(programme.indice)
    print(programme.description)    
    
if __name__ == "__main__":
    main()

