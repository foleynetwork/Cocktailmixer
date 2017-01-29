import time
import Datenbank
import thread
#from enum import Enum

ButtonLock = thread.allocate_lock()
SimLock = thread.allocate_lock()
ButtonAuswahl = None
SimPress = [False,False,False,False,False,False,False]

def SimButton(Button):
    SimPress[Button] = True

#class OtherPin(Enum):
    #BECHER200ML = 1

class GPIOPin:
    def __init__(self,Pinnummer,Name,Input,MeinCocktail = None,Other = None):
        self._Pinnummer = Pinnummer
        self._Name = Name
        self._Input = Input
        #self.Listen(self._Pinnummer,self._Name,
                                #self._Input,MeinCocktail,Other)
        if MeinCocktail is not None:
            thread.start_new_thread(self.Listen,(self._Pinnummer,self._Name,
                                self._Input,MeinCocktail,Other))
        
    def SignalOn(self):
        print("Oeffne " + self._Name + ": GPIO PIN " + str(self._Pinnummer) + " Set to HIGH")

    def SignalOff(self):
        print("Schliesse " + self._Name + ": GPIO PIN " + str(self._Pinnummer) + " Set to Low")

    def Listen(self,Pinnummer,Name,Input,MeinCocktail,Other):
        global ButtonLock
        while(True):
            if self.CheckButtonPress(Pinnummer) == True:
                SimPress[Pinnummer] = False #Simuliert
                self.DoJob(ButtonLock,MeinCocktail,Other)
            time.sleep(0.010)

    def CheckButtonPress(self,Pinnummer):
        global SimPress,SimLock
        SimLock.acquire()
        rtn = SimPress[Pinnummer] #Simuliert
        SimLock.release()
        return rtn

    def DoJob(self,lock,MeinCocktail,Other):
        global ButtonAuswahl
        if Other is None and ButtonAuswahl == None:
            lock.acquire()
            ButtonAuswahl = MeinCocktail
            lock.release()
            

class Zutat:
    
    def __init__(self,ZutatID,Name,Ventilgruppe,Ventilnummer,Alkohol,Min1,T100M,GPIOPIN):
        self.ZutatID = ZutatID
        self.Name = Name
        self.Ventilgruppe = Ventilgruppe
        self.Ventilnummer = Ventilnummer
        self.Alkohol = Alkohol
        self.Min1 = Min1
        self.T100M = T100M
        self.GPIOPin = GPIOPin(GPIOPIN,Name,False)


class ParameterZutat:
    def __init__(self,Zutat,Menge):
        self.Zutat = Zutat
        self.Menge = Menge

class Cocktail:
    def __init__(self,CocktailID,Name,GPIOPIN):
        self._ParameterZutaten = []
        self.Name = Name
        self.CocktailID = CocktailID
        self._StandardFuellmenge = -1
        self._JobList = None
        self.GPIOPin = GPIOPin(GPIOPIN,Name,True,self)

    def PrintZutaten(self):
        for MeineParameterZutaten in self._ParameterZutaten:
            print MeineParameterZutaten.Zutat.Name
            print MeineParameterZutaten.Menge

    def AddParameterZutat(self,ParameterZutat):
        self._ParameterZutaten.append(ParameterZutat)
        self.CalcStandardFuellmenge()

    def CalcStandardFuellmenge(self):
        self._StandardFuellmenge = 0
        for ParameterZutat in self._ParameterZutaten:
            self._StandardFuellmenge += ParameterZutat.Menge
        return self._StandardFuellmenge

    def Mixen(self):
        print "Cocktail wird gemixt: " + self.Name
        self._CreateJobList()
        self._JobList.DoJobs()
        print "Cocktail wurde erfolgreich gemixt!"

    def _CreateJobList(self):
        self._JobList = JobList()
        for MeinParameterZutat in self._ParameterZutaten:
            MeineZutat = MeinParameterZutat.Zutat
            MeineMenge = MeinParameterZutat.Menge
            self._JobList.AddJobZutat(MeineZutat,True)
            if MeineMenge == -1:
                WarteZeit = MeineZutat.Min1
            else:
                WarteZeit = (MeineMenge / 100.0) * MeineZutat.T100M
                # Pro Sekunde / 1000
            self._JobList.AddJobWarten(WarteZeit)
            self._JobList.AddJobZutat(MeineZutat,False)

class Job:
    def __init__(self,Zutat,WarteZeit,Open):
        self._Zutat = Zutat
        self._WarteZeit = WarteZeit
        self._Open = Open

    def DoJob(self):
        if self._WarteZeit == - 1:
            if self._Open:
                self.OpenGPIOPin(self._Zutat)
            else:
                self.CloseGPIOPin(self._Zutat)
        else:
            print "Sleep(): " + str(self._WarteZeit) + "ms"
            time.sleep(self._WarteZeit / 1000)

    def OpenGPIOPin(self,Zutat):
        Zutat.GPIOPin.SignalOn()

    def CloseGPIOPin(self,Zutat):
        Zutat.GPIOPin.SignalOff()

    def GetWarteZeit(self):
        return self.WarteZeit

class JobList:
    def __init__(self):
        self._Jobs = []

    def AddJobZutat(self,Zutat,Open):
        NewJob = Job(Zutat,-1,Open)
        self._Jobs.append(NewJob)

    def AddJobWarten(self,Wartezeit):
        NewJob = Job(-1,Wartezeit,False)
        self._Jobs.append(NewJob)
        
    def CalcKompletteZeit(self):
        Zeit = 0
        for Job in self._Jobs:
            if Job.GetWarteZeit() > 0:
                Zeit += Job.GetWarteZeit()

    def DoJobs(self):
        for Job in self._Jobs:
            Job.DoJob()

class CocktailMaschine:
    def __init__(self):
        self._DBHandler1 = Datenbank.DBHandler('Cocktailmixer.db')
        self._AlleCocktails = []
        self.LoadAlleCocktails()
        thread.start_new_thread(self.Listen,())

    def Close(self):
        self._DBHandler1.Close()

    def Listen(self):
        global ButtonLock
        while(True):
            ButtonLock.acquire()
            self.CheckButtonPress()
            ButtonLock.release()
            time.sleep(0.010)

    def CheckButtonPress(self):
        global ButtonAuswahl
        if ButtonAuswahl is not None:
            ButtonAuswahl.Mixen()
            ButtonAuswahl = None

    def LoadRezept(self,MeinCocktail):
        rezepte = self._DBHandler1.GetRezeptByCocktailID(MeinCocktail.CocktailID)
        for rezept in rezepte:
            zutat = self._DBHandler1.GetZutatByID(rezept[1])
            menge = rezept[2]
            GPIOPIN = self._DBHandler1.GetPINByZutatID(rezept[1])
            klassezutat = Zutat(zutat[0],zutat[1],zutat[2],
                                zutat[3],zutat[4],zutat[5],
                                zutat[6],GPIOPIN)
            parameterzutat = ParameterZutat(klassezutat,menge)
            MeinCocktail.AddParameterZutat(parameterzutat)

    def LoadAlleCocktails(self):
        print "Lade alle Cocktails"
        Cocktails = self._DBHandler1.GetAllCocktails()
        for dbCocktail in Cocktails:
            GPIOPIN = self._DBHandler1.GetPINByCocktailID(dbCocktail[0])
            self._AlleCocktails.append(Cocktail(dbCocktail[0],dbCocktail[1],
                                     GPIOPIN))
        for aCocktail in self._AlleCocktails:
            print "[" + str(aCocktail.GPIOPin._Pinnummer) + "]" + aCocktail.Name
            self.LoadRezept(aCocktail)



CocktailMaschine1 = CocktailMaschine()
MeinCocktail = CocktailMaschine1._AlleCocktails[0]
#MeinCocktail.Mixen()



