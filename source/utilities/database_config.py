# Jonathan Valiente.  All rights reserved. 2022

# The software is provided "As is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.
# in no event shall the authors be liable for any claim, damages or
# other liability, whether in an action of contract, tort or otherwise,
# arising from, out of or in connection with the software or the use or
# other dealings in the software.


global db
import os
import pickle
import platform
import sys
import sqlite3



operating_system = platform.system()

if getattr(sys, "frozen", False):
    # If the application is run as a bundle, the PyInstaller bootloader
    # extends the sys module by a flag frozen=True and sets the app
    # path into variable _MEIPASS'.
    resource_path = sys._MEIPASS

    if operating_system == "Darwin": #MacOS
        darwin_network_visualizer_dir = os.path.expanduser('~/Library/Application Support/Network-Visualizer')
        database_location = os.path.join( darwin_network_visualizer_dir, "data.sqlite")

    else:
        database_location = os.path.join(resource_path, "assets/database/data.sqlite")


else:
    # otherwise get the path from where the python file is executed
    resource_path = os.path.dirname( os.path.dirname( os.path.dirname( os.path.abspath( __file__ ) ) ) )
    database_location = os.path.join(resource_path, "assets/database/data.sqlite")
    

db = sqlite3.connect(database_location, isolation_level=None, timeout=10)
db.text_factory = str

sqlite3.register_adapter(dict, lambda d: pickle.dumps(d))
sqlite3.register_converter("dictionary", lambda d: pickle.loads(d))