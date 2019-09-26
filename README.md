# ShaVas #

ShaVas ist eine Web-Application mit der man zwei, frei gewählte Formen zum Erkennen einzeichnen und mithilfe eines speziellen Feldes diese erkennen lassen kann.


## Vorbereitung und Installation ## 

Als erstes müssen Sie das Repository klonen oder downloaden.
Öffnen Sie die Konsole und wechseln sie in das geklonte/heruntergeladene Repository.

**1. Frontend einrichten**
----
  1. In das **frontend**-Verzeichnis wechseln.
  2. Die packages ins Verzeichnis laden:
      1. Falls kein npm installiert ist, bitte npm installieren/updaten.
      ```
      npm install
      ```
  3. Dadurch sollten *package-lock.json*- (und/oder *yarn.lock*-)Dateien und ein Ordner *node_modules* im **frontend**-Verzeichnis zu sehen sein (das kann eine Weile dauern):
      ```
      ├── ShaVas
          ├── ...
          ├── frontend
              ├── node_modules
              ├── ...
              ├── package.json
              └── ...
      ```
  4. Danach können Sie folgende packages kontrollieren und sind mit der Einrichtung des Frontends fertig.
      1. Zum Kontrollieren:
          ```
          npm list --depth=0
          ```
      2. Die packages, die aufgelistet werden sollten:
          ```
          react@<version>
          react-dom@<version>
          react-scripts<version>
          typescript<version>
          ```
**2. Backend einrichten**
----
  1. Im Root des Repositories folgenden Command/Behfehl ausführen:
      1. falls pipenv nicht existiert, bitte pipenv einrichten.
      ```
      pipenv shell
      ```
  2. Falls die virtuelle Umgebung damit aktiviert wurde, müssen Sie hier jetzt in das **backend**-Verzeichnis wechseln.
  3. Dort einfach folgendes ausführen:
      1. Dafür muss eine python-Version von 3+ existieren.
      ```
      python3 main.py
      ```
  4. Bei den ersten Ausführungen werden Sie aufgefordert, Module im Projekt zu installieren.
      1. Der Command/Befehl fürs installieren der Module lautet:
      ```
      pip3 install <package_name>
      ```
      2. Dies ist die Liste an <package_name>n die installiert werden müssen:
      ```
      opencv-python
      flask
      numpy
      tensorflow
      ```
      3. Falls Sie aufgefordert werden, weitere Module in der virtuellen Umgebung zu installieren, dann installieren Sie diese bitte auch.
  5. Um zu kontrollieren, ob alles da ist, können folgende Commands/Befehle ausgeführt werden:
      ```
      pip3 freeze
      ```
      oder
      ```
      pip3 list --local
      ```
  6. Ist das backend aktiviert und Sie möchten es abschalten bzw. die virtuelle Umgebung schließen, so müssen Sie das backend mit
  
      <kbd>⌃</kbd>+<kbd>C</kbd>
      
      oder
      
      <kbd>Strg</kbd>+<kbd>C</kbd>
      
      deaktivieren und danach
      ```
      exit
      ```
      oder
      ```
      exit()
      ```
      ausführen.

**3. Frontend starten**
----
  Da die Applikation mithilfe von React gebaut wurde, muss man im **frontend**-Verzeichnis einfach folgedes ausführen:
  ```
  npm start
  ```
  Dadurch sollte sich ein Fenster im Browser öffnen, wo dann die Applikation läuft.
  * Falls sich kein Fenster öffnet, dies in die Adressezeile eintragen:
    ```
    localhost:3000
    ```
  * Falls der Port geändert werden soll, einfach die package.json öffnen und folgenden Eintrag entsprechend ändern:
    ```
    ...
    "scripts": {
      "start": "react-scripts start",
    ...

     │   │
     │   │
    \│   │/
     \   /
      \ /
       V

    ...
    "scripts": {
    "start": "PORT=<desired_port_number> react-scripts start",
    ...
    ```
    Das Frontend ist somit einsatzbereit. Um es also wieder abzuschalten, muss einfach nur
    
    <kbd>⌃</kbd>+<kbd>C</kbd>
    
    oder
    
    <kbd>Strg</kbd>+<kbd>C</kbd>
    
    in der Konsole gedrückt werden.


**4. Backend starten**
----
  Um das Python-Backend zu starten müssen Sie wie in Schritt *"2. Backend einrichten"* die virtuelle Umgebung mit
  ```
  pipenv shell
  ```
  vom Root des Repositories starten.
  Danach ins **backend**-Verzeichnis wechseln und dort
  ```
  python3 main.py
  ```
  ausführen.
  Wenn alles erfolgreich war, dann müsste folgendes in etwa stehen:
  ```
  ...
  !!!!!!!!!!!!!!!!!!!!!!!!!!
  !!!!!!!!START MAIN!!!!!!!!
  !!!!!!!!!!!!!!!!!!!!!!!!!!
  * Debugger is active!
  * Debugger PIN: <PIN>
  ```
