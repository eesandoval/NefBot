# NefBot - A Discord Bot for Dragalia Lost - Server Updates
1. [About](#about)
2. [Installation](#installation)
# About
This folder and the contents within are for updating the server that the database and pictures sit on. To run this update, execute the update.py file which will utilize the gamepedia site to get images and information to load into the database. Please note this is only if you wish to change the server location where the remote database and pictures are stored (picture server in the config file). If you're fine with the default one, the contents of this folder do not apply.


# Installation
## Requirements
- [Python 3.6 or higher](https://www.python.org/)
- [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/)

## Instructions 
1. If not installed, download [Python 3.6 or higher](https://www.python.org) 
2. Once installed, open a command prompt window or terminal window and type the following to install [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) 
```
python -m pip install beautifulsoup4
```
3. Make sure the server structure is in the below format
```
root_server_folder
|---adventurers
|   |---portraits
|   |---full
|
|---database
|   |   master.db
|
|---dragons
|   |---portraits
|   |---full
|
|---weapons
|   |---portraits
|
|---wyrmprints
|   |---portraits
|   |---full
|   |---base
```
4. Optional: Make a backup of the above folder
5. Run the update.py file using 
```
python update.py
```