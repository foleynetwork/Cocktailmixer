import time
import Datenbank
import thread

class GPIOPin:
    def __init__(self,Pinnummer,Name):
        self._Pinnummer = Pinnummer
        self._Name = Name
                
    def SignalOn(self):
        print("Oeffne " + self._Name + ": GPIO PIN " + str(self._Pinnummer) + " Set to HIGH")

    def SignalOff(self):
        print("Schliesse " + self._Name + ": GPIO PIN " + str(self._Pinnummer) + " Set to Low")
            
class Zutat:
    
    def __init__(self,ZutatID,Name,Ventilgruppe,Ventilnummer,Alkohol,Min1,T100M,GPIOPIN):
        self.ZutatID = ZutatID
        self.Name = Name
        self.Ventilgruppe = Ventilgruppe
        self.Ventilnummer = Ventilnummer
        self.Alkohol = Alkohol
        self.Min1 = Min1
        self.T100M = T100M
        self.GPIOPin = GPIOPin(GPIOPIN,Name)


class ParameterZutat:
    def __init__(self,Zutat,Menge):
        self.Zutat = Zutat
        self.Menge = Menge

class Cocktail:
    def __init__(self,CocktailID,Name):
        self._ParameterZutaten = []
        self.Name = Name
        self.CocktailID = CocktailID
        self._StandardFuellmenge = -1
        self._Alkoholmenge = -1
        self._NichtAlkoholmenge = -1
        self._Alkoholmengepur = -1
        self._ProzentStaerke = -1
        self._JobList = None
        self._NewCocktail = None
        
    def PrintZutaten(self):
        for MeineParameterZutaten in self._ParameterZutaten:
            print MeineParameterZutaten.Zutat.Name
            print MeineParameterZutaten.Menge

    def AddParameterZutat(self,ParameterZutat):
        self._ParameterZutaten.append(ParameterZutat)
        self.CalcStandardFuellmenge()

    def CalcStandardFuellmenge(self):
        self._StandardFuellmenge = 0
        self._Alkoholmenge = 0
        self._Alkoholmengepur = 0
        self._NichtAlkoholmenge = 0
        for ParameterZutat in self._ParameterZutaten:
            self._StandardFuellmenge += ParameterZutat.Menge
            if ParameterZutat.Zutat.Alkohol > 0:
                self._Alkoholmenge += ParameterZutat.Menge
                self._Alkoholmengepur += ParameterZutat.Menge * (ParameterZutat.Zutat.Alkohol/100.0)
        try:
            self._ProzentStaerke = self._Alkoholmengepur / float(self._StandardFuellmenge)
        except:
            self._ProzentStaerke = 0
        self._NichtAlkoholmenge = self._StandardFuellmenge - self._Alkoholmenge 
        return self._StandardFuellmenge

    def _GetAlkoholFaktoren(self,Staerke,Fuellmenge):
        FaktorFuellmenge = float(Fuellmenge) / self._StandardFuellmenge
        newNichtAlkoholmenge = self._StandardFuellmenge - (self._Alkoholmenge * Staerke)
        FaktorAlkoholmenge = Staerke
        FaktorNichtAlkoholmenge = float(newNichtAlkoholmenge) / self._NichtAlkoholmenge
        FaktorAlkoholmenge *= FaktorFuellmenge
        FaktorNichtAlkoholmenge *= FaktorFuellmenge
        return FaktorAlkoholmenge,FaktorNichtAlkoholmenge
        

    def Mixen(self,Staerke,Fuellmenge): #Staerke in %/Fuellmenge in ml
        FaktorAlkoholmenge,FaktorNichtAlkoholmenge = self._GetAlkoholFaktoren(Staerke,Fuellmenge)
        self._NewCocktail = Cocktail(self.CocktailID,self.Name)
        for xParameterZutat in self._ParameterZutaten:
            newParameterZutat = ParameterZutat(xParameterZutat.Zutat,xParameterZutat.Menge)
            if xParameterZutat.Zutat.Alkohol > 0:
                newParameterZutat.Menge *= FaktorAlkoholmenge
            else:
                newParameterZutat.Menge *= FaktorNichtAlkoholmenge
            self._NewCocktail.AddParameterZutat(newParameterZutat)
        self._NewCocktail._RealMixen()
        
        
    def _RealMixen(self):
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
            self._JobList.AddJobWarten(MeineZutat,WarteZeit)
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


    def _ModifyJobToFast(self):
        OpenJobs = []
        CloseJobs = []
        WarteJobs = []
        for xJob in self._Jobs:
            if xJob._Open:
                OpenJobs.append(xJob)
            else:
                if xJob._WarteZeit > - 1:
                    WarteJobs.append(xJob)                    
        WarteJobs = sorted(WarteJobs, key=lambda Job: Job._WarteZeit)
        tmp = 0
        for xJob in WarteJobs:
            newJob = Job(xJob._Zutat,-1,False)
            CloseJobs.append(newJob)
            xJob._WarteZeit -= tmp
            tmp += xJob._WarteZeit
        self._Jobs = []
        for xJob in OpenJobs:
            self._Jobs.append(xJob)
        for i in range(0,len(WarteJobs)):
            self._Jobs.append(WarteJobs[i])
            self._Jobs.append(CloseJobs[i])
        

    def AddJobZutat(self,Zutat,Open):
        NewJob = Job(Zutat,-1,Open)
        self._Jobs.append(NewJob)

    def AddJobWarten(self,Zutat,Wartezeit):
        NewJob = Job(Zutat,Wartezeit,False)
        self._Jobs.append(NewJob)
        
    def CalcKompletteZeit(self):
        Zeit = 0
        for Job in self._Jobs:
            if Job.GetWarteZeit() > 0:
                Zeit += Job.GetWarteZeit()

    def Abort(self):
        return False

    def DoJobs(self):
        #self._ModifyJobToFast()
        for Job in self._Jobs:
            if not self.Abort():
                Job.DoJob()

class CocktailMaschine:
    def __init__(self):
        self._DBHandler1 = Datenbank.DBHandler('Cocktailmixer.db')
        self._AlleCocktails = []
        self.LoadAlleCocktails()

    def Close(self):
        self._DBHandler1.Close()

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
            self._AlleCocktails.append(Cocktail(dbCocktail[0],dbCocktail[1]))
        for aCocktail in self._AlleCocktails:
            print aCocktail.Name
            self.LoadRezept(aCocktail)



CocktailMaschine1 = CocktailMaschine()
MeinCocktail = CocktailMaschine1._AlleCocktails[1]
MeinCocktail.Mixen(1.12,600)



