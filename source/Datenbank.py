import sqlite3

def CreateScript():
    conn = sqlite3.connect('Cocktailmixer.db')
    c = conn.cursor()
    c.execute('''SELECT * FROM Zutaten''')
    print "zutaten = " + str(c.fetchall()) + "\n"
    print """c.executemany('INSERT INTO Zutaten VALUES(?,?,?,?,?,?,?)',zutaten)\n"""
    c.execute('''SELECT * FROM Cocktail''')
    print "cocktails = " + str(c.fetchall()) + "\n"
    print """c.executemany('INSERT INTO Cocktail VALUES(?,?)',cocktails)\n"""
    c.execute('''SELECT * FROM Rezept''')
    print "Rezept = " + str(c.fetchall()) + "\n"
    print """c.executemany('INSERT INTO Rezept VALUES(?,?,?)',rezepte)\n"""
    c.execute('''SELECT * FROM GPIOPIN''')
    print "gpiopins = " + str(c.fetchall()) + "\n"
    print """c.executemany('INSERT INTO GPIOPIN VALUES(?,?)',gpiopins)\n"""
    conn.close()
    
def DBScript():
    conn = sqlite3.connect('Cocktailmixer.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE Zutaten
    (ZutatID integer primary key,Name text,Ventilgruppe integer,Ventilnummer integer,Alkohol real,Min1 Integer,T100M Integer)''')
    c.execute('''CREATE TABLE Cocktail
    (CocktailID integer primary key,Name text)''')
    c.execute('''CREATE TABLE Rezept
    (CocktailID integer,ZutatID integer,Fuellmenge integer)''')
    c.execute('''CREATE TABLE GPIOPIN
    (Pinnummer integer,ZutatID integer)''')

    zutaten = [(1,"Orangensaft",1,1,0.0,50,500),
               (2,"Limettensaft",1,2,0.0,51,501),
               (3,"Vodka",1,3,40.0,52,302)
               ]
    c.executemany('INSERT INTO Zutaten VALUES(?,?,?,?,?,?,?)',zutaten)

    cocktails = [(1,"Vodka-O"),
                 (2,"Vodka-LimOr"),
                 (3,"Multivitaminsaft")
                 ]
    c.executemany('INSERT INTO Cocktail VALUES(?,?)',cocktails)

    gpiopins = [(1,1), #Zutaten
                (2,2),
                (3,3)
                ]
    c.executemany('INSERT INTO GPIOPIN VALUES(?,?)',gpiopins)

    rezepte = [(1,3,121), #Vodka-O
               (1,1,283),
               (2,3,121), #Vodka-LimOr
               (2,1,122),
               (2,2,123),
               (3,1,201), #Multivitaminsaft
               (3,2,202)
               ]
    c.executemany('INSERT INTO Rezept VALUES(?,?,?)',rezepte)
    conn.commit()
    conn.close()

class DBHandler():
    
    def __init__(self,Datenbankpfad):
        self._conn = sqlite3.connect(Datenbankpfad)
        print("DB Verbindung geoeffnet")

    def __exit__(self, exc_type, exc_value, traceback):
        self.CloseConnection()

    def Close(self):
        self._conn.close()
        print("DB Verbindung geschlossen")
        
    def GetAllZutaten(self):
        c = self._conn.cursor()
        c.execute('''SELECT * FROM Zutaten''')
        return c.fetchall()

    def GetAllCocktails(self):
        c = self._conn.cursor()
        c.execute('''SELECT * FROM Cocktail''')
        return c.fetchall()

    def GetPINByZutatID(self,ZutatID):
        c = self._conn.cursor()
        c.execute('''SELECT Pinnummer FROM GPIOPIN Where ZutatID = ?''',(ZutatID,))
        return c.fetchone()[0]

    def GetRezeptByCocktailID(self,CocktailID):
        c = self._conn.cursor()
        c.execute('''SELECT * FROM Rezept Where CocktailID = ?''',(CocktailID,))
        return c.fetchall()

    def GetZutatByID(self,ZutatID):
        c = self._conn.cursor()
        c.execute('''SELECT * FROM Zutaten Where ZutatID = ?''',(ZutatID,))
        return c.fetchone()
    

def Buildup():
    conn = sqlite3.connect('Cocktailmixer.db')
    c = conn.cursor()
    
    #c.execute('''SELECT sql FROM sqlite_master''')
    #print c.fetchall()
    c.execute('''SELECT * FROM Rezept''')
    print c.fetchall()
    #DBScript()

    conn.commit()
    conn.close()

def Test():
    DBHandler1 = DBHandler('Cocktailmixer.db')
    print DBHandler1.GetAllZutaten()
    print DBHandler1.GetAllCocktails()
    print DBHandler1.GetPINByCocktailID(1)
    print DBHandler1.GetPINByZutatID(2)
    print DBHandler1.GetRezeptByCocktailID(2)
    print DBHandler1.GetZutatByID(2)
    DBHandler1.Close()
    #Buildup()

#Test()


