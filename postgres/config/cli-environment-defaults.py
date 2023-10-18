import os
import shutil
from os import environ
from pathlib import Path

environ['HS_PG_HOME'] = environ.get('HS_GP_HOME', str(Path('postgres')))
environ['HS_PG_HOST'] = environ.get('HS_PG_HOST', '127.0.0.1')
environ['HS_PG_PORT'] = environ.get('HS_PG_PORT', str(5432 + int(environ['HS_PORT_OFFSET'])))
