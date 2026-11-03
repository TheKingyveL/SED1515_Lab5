import machine
import time

# INITIALISATION DU BUS I2C ET DU RTC
i2c = machine.I2C(1, sda=machine.Pin(14), scl=machine.Pin(15))  # I2C1, SDA sur GP14, SCL sur GP15
RTC_ADDR = 0x68                                                 # Adresse par défaut du DS3231

# INITIALISATION DU BOUTON SW1 sur GPIO 10
bouton = machine.Pin(10, machine.Pin.IN, machine.Pin.PULL_DOWN)


# FONCTIONS DE CONVERSION 
'''
 Le DS3231 stocke le temps en Décimal Codé Binaire (DCB).
'''
def bcd_en_decimal(bcd):
  x =  (bcd >> 4) * 10 + (bcd & 0x0F)
  return x

def lire_secondes_rtc():
  """Lit les secondes sur le RTC et le convertit."""
  donnees = i2c.readfrom_mem(RTC_ADDR, 0x00, 1)
  secondes_bcd = donnees[0]
  secondes = bcd_en_decimal(secondes_bcd & 0x7F)
  return secondes

# BOUCLE PRINCIPALE DU JEU
print("Bienvenue au Jeu de précision temporelle")
print("Appuyez sur le bouton pour commencer et appuyez à nouveau quand vous pensez que 15s se sont écoulées.\n")

try:
    " Ouverture du fichier journal en mode 'append' "
    log = open("log.txt", "a")
    log.write(" Nouvelle session de jeu \n")

    while True:
       while bouton.value() == 0:
         time.sleep(0.01)
            
        print("C'est parti ! Comptez 15 secondes...")
        temps_debut = lire_secondes_rtc()   # On note le temps de départ 
        # Attendre que le bouton soit relâché
        while bouton.value() == 1:
            time.sleep(0.01)
            
        # Attendre le deuxième appui pour ARRÊTER
        while bouton.value() == 0:
            time.sleep(0.01)
            
        temps_fin = lire_secondes_rtc()     # On note le temps d'arrivée 
        
      # Anti-rebond pour le relâchement
        while bouton.value() == 1:
            time.sleep(0.01)
            
        # Calcul du temps écoulé
        if temps_fin >= temps_debut:
          " Cas où on passe de 59 à 0 "
          duree = temps_fin - temps_debut
        else:
          " Si on a passé la minute dans laquelle on a débuté "
          duree = (60 - temps_debut) + temps_fin
            
        print(f"Temps mesuré : {duree} secondes.")
        print("Appuyez sur le bouton pour recommencer.\n")
        
        # Écriture dans le fichier log et sauvegarde
        log.write(f"Temps : {duree} s\n")
        log.flush()       # Force l'écriture sur la mémoire flash

except KeyboardInterrupt:
  # Si on arrête le programme, on ferme le fichier
  print("\nFin du programme. Sauvegarde du journal...")
  log.close()
  print("Fichier log.txt sauvegardé.")
