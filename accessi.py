#TecnoGeppetto aka Valerio Tognozzi 
# 
# Sistema controllo Accessi ad Archivio Documenti Sensibili
# Due lettori Rfid leggono gli accessi e le uscite
# Accesso su ttyUSB0  -  Uscita su ttyUSB1
# registro il log degli accessi/uscite,   dei tentati accessi/uscita e tutte le operazioni effettuate (inserimento utente e acccesso manuale) 
# scrive su log_accessi.log tutto quello che accade in modo verboso.  e su log_ufficiale.log solo i dati necessari per stilare registro cartaceo
# Tramite APP si stampa il registro e si gestiscono i dati degli utenti
# #
#

# Import necessary libraries for communication and display use
import lcddriver
import time
# Importa librerie gestione Porta Seriale
from serial import Serial 
from sys import exit
#importa libreria gestione GPIO Raspberry Pi
import RPi.GPIO as GPIO
from os import path



L1 = 5
L2 = 6
L3 = 13
L4 = 19

C1 = 12
C2 = 16
C3 = 20
C4 = 21

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO.setup(L1, GPIO.OUT)
GPIO.setup(L2, GPIO.OUT)
GPIO.setup(L3, GPIO.OUT)
GPIO.setup(L4, GPIO.OUT)

GPIO.setup(C1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(C2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(C3, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(C4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

scelta = ""


# Load the driver and set it to "display"
# If you use something from the driver library use the "display." prefix first
display = lcddriver.lcd()

#Prima Porta RFID
serial_obj = Serial()

serial_obj.port = "/dev/ttyUSB0"
serial_obj.baudrate = 9600
serial_obj.timeout = 0.5
serial_obj.open()
assert(serial_obj.isOpen())

## quando abbiamo a disposizione la scheda clone va attivata anche questa parte

#Seconda porta RFID
serial1_obj = Serial()
serial1_obj.baudrate = 9600
serial1_obj.timeout = 0.5
no_port = False
if path.exists("/dev/ttyUSB1"):
    serial1_obj.port = "/dev/ttyUSB1"
    serial1_obj.open()
    no_port = serial1_obj.isOpen()


# Funzione da scrivere per gestire lo sblocco della serratura. - non richiesta ma prevista - 
# # il sistema  la chiama  se consentito l'accesso o l'uscita
def sblocca_serratura():
    pass

# gestione tastierino manuale
def readLine(line, characters):
    global scelta
    GPIO.output(line, GPIO.HIGH)
    if(GPIO.input(C1) == 1):
        scelta = (characters[0])
    if(GPIO.input(C2) == 1):
       scelta = (characters[1])
    if(GPIO.input(C3) == 1):
        scelta = (characters[2])
    if(GPIO.input(C4) == 1):
        scelta = (characters[3])
    GPIO.output(line, GPIO.LOW)

def timer(delta, tempo_funz, tempo_mac):
    if (tempo_funz-tempo_mac ) > delta:
        return True
    return False


def tastierino(tempo_mac):
    tempo_funz = time.time()
    delta = 0.3
   
    if (timer(delta, tempo_funz, tempo_mac)):
        readLine(L1, ["1","2","3","A"])
        readLine(L2, ["4","5","6","B"])
        readLine(L3, ["7","8","9","C"])
        readLine(L4, ["*","0","#","D"])
        
# menu che gira all'infinito
def menu_start(Z,sel):
    while True:
        if (time.time() - Z) >= 0 and (time.time() - Z) < 2 and sel == 0:
            display.lcd_clear()
            display.lcd_display_string("  Blue  Factor", 1)
            display.lcd_display_string(" Contr. Accessi", 2)
            sel = 1
            return (Z,sel)
        elif (time.time() - Z) >= 2 and (time.time() - Z) < 4 and sel == 1:
            display.lcd_clear()
            display.lcd_display_string("  Blue  Factor", 1)
            display.lcd_display_string(" Premi un Tasto", 2)
            sel = 2
            return (Z, sel)
        elif (time.time() - Z) >= 4 and (time.time() - Z) < 6 and sel == 2:
            display.lcd_clear()
            ora = time.ctime()
            display.lcd_display_string("  Blue  Factor", 1)
            display.lcd_display_string("    "+ora[11:20], 2)
            sel = 0
            return (Z,sel)
        elif  (time.time() - Z) > 6:
            sel = 0
            Z = time.time()
            return (Z,sel)
        
        
#menu Accesso Manuale
def menu_accesso_manuale():                                        
    display.lcd_clear()
    display.lcd_display_string(" Accesso Manuale", 1)
    display.lcd_display_string("  Digita il Cod.", 2)
def accesso_manuale():
    global X
    global scelta
    codice = ""
    display.lcd_clear()
    display.lcd_display_string("  Blue  Factor", 1)
    display.lcd_display_string(" Digita CODICE", 2)
    while True:
        tastierino(X)
            
        if scelta != "":
                display.lcd_display_string("                ", 2)
                #qui passo al menu accesso
                codice = codice + scelta
                display.lcd_display_string(codice, 2)
                X = time.time()
                scelta = ""
        if len(codice) == 4 :
            display.lcd_clear()
            display.lcd_display_string(codice, 1)
            display.lcd_display_string(" Conf.=# Esc.=*", 2)
            
            while True:
                tastierino(X)
                if scelta == "#":
                        display.lcd_display_string("                ", 2)
                        #qui passo al menu accesso
                        display.lcd_display_string("Hai Confermato", 2)
                        X = time.time()
                        scelta = ""
                        time.sleep(2)
                        f1=open("garanted.txt", "r")
                        garanted = f1.readlines()
                        
                        for el in garanted:
                            for codici in el.split(","):
                                if codice in codici:
                                    nome_cog = el.split(",")[1] 
                                    mansione = el.split(",")[2]
                                    scrivi_log("Accesso MANUALE", codice, nome_cog=nome_cog, mansione=mansione)
                                    sblocca_serratura()
                                    display.lcd_clear()
                                    display.lcd_display_string(nome_cog, 1)
                                    display.lcd_display_string("  AUTORIZZATO", 2)
                                    time.sleep(2)
                                    f1.close()
                                    return codice
                        display.lcd_clear()
                        display.lcd_display_string("  SORRY NON", 1)
                        display.lcd_display_string("  AUTORIZZATO", 2)
                        scrivi_log("Accesso FALLITO", codice)
                        time.sleep(2)
                        f1.close()
                        return codice
                elif scelta == "*" :
                        display.lcd_display_string("                ", 2)
                        display.lcd_display_string("Scelta Annullata", 2)
                        codice = ""
                        scelta = ""
                        time.sleep(2)
                        return codice

def menu_scelte():
    global X
    global scelta
    
    display.lcd_clear()
    display.lcd_display_string("BADGE Manual > 1", 1)
    display.lcd_display_string("Agg. Utente  > 2", 2)
    
    while True:
        tastierino(X)
        
        if scelta == "1" :
                X = time.time()
                scelta = ""
                badge = accesso_manuale()   
                scelta = ""
                return True
        elif scelta == "2":
                X = time.time()
                scelta = ""
                aggiungi_utente()
                scelta = ""
                return True
        elif scelta == "*":
                scelta = ""
                X = time.time()
                return True

        


def aggiungi_utente():
    global X
    global scelta
    badge = ""
    display.lcd_clear()
    display.lcd_display_string("AGGIUNGI UTENTE", 1)
    display.lcd_display_string("Passa il BADGE ", 2)
    uten = 0
    while uten == 0:
        try:
            rfid_code = serial_obj.read_until(expected='\n', size=14).decode('ascii')

        except:
            print('Invalid RFID code.')
            continue
        
        if len(rfid_code) > 0:
            display.lcd_clear()
            display.lcd_display_string(rfid_code, 1)
            display.lcd_display_string(" Conf.=# Esc.=*", 2)
            time.sleep(2)
            
            while uten == 0:
                tastierino(X)
                if scelta =="#":
                    display.lcd_clear()
                    display.lcd_display_string(rfid_code, 1)
                    display.lcd_display_string("Confermato !", 2)
                    X = time.time()
                    scelta = ""
                    time.sleep(2)
                    rfid_code = rfid_code[1:13]
                    f1=open("garanted.txt", "a")
                    f1.write(rfid_code+"\n")
                    f1.close()
                    display.lcd_clear()
                    display.lcd_display_string("UTENTE AGGIUNTO", 1)
                    display.lcd_display_string(rfid_code, 2)
                    time.sleep(2)
                    scrivi_log("Nuovo utente   ", rfid_code)
                    uten = 1
                    serial_obj.flushInput()
                    


                elif scelta == "*":
                    uten = 1
        
def leggi_rfid(N):
    try:
        if N == 0:
            rfid_code    = serial_obj.read_until(expected='\n', size=14).decode('ascii')   
        elif N == 1:
            rfid_code    = serial1_obj.read_until(expected='\n', size=14).decode('ascii') #seconda scheda differente dall'altra
    
    except:
        print('Invalid RFID code.')
        return False
    rfid_code = rfid_code[1:13]
    gar_index = 0
    if len(rfid_code) != 0:                        
        f=open("garanted.txt", "r")
        garanted = f.readlines()
        if rfid_code+"\n" in garanted and N == 0:    # (N=0) = lettore dell'ingresso
            gar_index = garanted.index(rfid_code+"\n")
            nome_cog = garanted[gar_index+1].split(",")[1]
            mansione = garanted[gar_index+1].split(",")[2]  
            display.lcd_clear()
            display.lcd_display_string(rfid_code, 1)
            display.lcd_display_string(nome_cog, 2)
            time.sleep(2)
            display.lcd_display_string("ACCESSO OK !", 2)
            scrivi_log("Accesso OK     ", rfid_code, nome_cog, mansione)
            sblocca_serratura()
        elif rfid_code+"\n" in garanted and N == 1:  # (N=1) = lettore dell'uscita
            gar_index = garanted.index(rfid_code+"\n")
            nome_cog = garanted[gar_index+1].split(",")[1] 
            mansione = garanted[gar_index+1].split(",")[2] 
            display.lcd_clear()
            display.lcd_display_string(rfid_code, 1)
            display.lcd_display_string("USCITA  OK !", 2)
            scrivi_log("Uscita  OK     ", rfid_code, nome_cog, mansione)
            sblocca_serratura()         
        else:
            display.lcd_clear()
            display.lcd_display_string(rfid_code, 1)
            display.lcd_display_string("NON AUTORIZZATO!", 2)
            scrivi_log("Accesso FALLITO", rfid_code)
        f.close()
        time.sleep(4)
        serial_obj.flushInput()
        if no_port:
            serial1_obj.flushInput()

def scrivi_log(caccade, badge, nome_cog="Nessuno", mansione="Nessuno"):
    f= open("log_accessi.log","a")
    f.write(caccade+" --> ")
    f.write(badge+"\t")
    f.write(time.ctime())
    f.write("\n")
    f.close()
    if caccade == "Accesso OK     ":
        f= open("log_ufficiale.log","a")
        f.write("ENTRATA"+",")
        f.write(time.ctime())
        f.write(","+nome_cog+","+mansione)
        f.close()
    elif caccade == "Uscita  OK     ":
        f= open("log_ufficiale.log","a")
        f.write("USCITA"+",")
        f.write(time.ctime())
        f.write(","+nome_cog+","+mansione)
        f.close()
    elif caccade == "Accesso MANUALE":
        f= open("log_ufficiale.log","a")
        f.write("MANUALE"+",")
        f.write(time.ctime())
        f.write(","+nome_cog+","+mansione)
        f.close()
    

# Main body of code
try:
    X = time.time()
    Z = time.time()
    sel = 0
    while True:
        Z, sel = menu_start(Z, sel)
        tastierino(X)
        if scelta != "":
            scelta = ""
            menu_scelte()
            X = time.time()
            scelta = ""
        leggi_rfid(0)
        if no_port:
            leggi_rfid(1)

            
        
 
except KeyboardInterrupt: # If there is a KeyboardInterrupt (when you press ctrl+c), exit the program and cleanup
    print("Cleaning up!")
    display.lcd_clear()

