@echo off
REM Crea l'ambiente Conda Principale
conda create -n scope python=3.10 -y

REM Attiva l'ambiente appena creato
CALL conda activate scope

REM Avvisa che le librerie sono state installate con successo è terminato
echo Ambiente Conda **scope** creato con successo!

REM Install dependecy
CALL pip install -r requirements_scope.txt

REM Avvisa che il processo è terminato
echo [scope] Librerie installate con successo!

@echo off
REM Crea l'ambiente Conda Secondario
conda create -n twitter_env python=3.10 -y

REM Attiva l'ambiente appena creato
CALL conda activate twitter_env

REM Avvisa che le librerie sono state installate con successo è terminato
echo Ambiente Conda **scope** creato con successo!

REM Install dependecy
CALL pip install -r requirements_twitter_env.txt

REM Avvisa che il processo è terminato
echo [twitter_env] Librerie installate con successo!

@echo off

REM --- Avvia Ollama in una nuova finestra ---
start /B "" "ollama serve"

REM --- Avvia Verba in una nuova finestra ---
start /B "" "verba start"

exit


