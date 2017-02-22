import sys
 
sys.path.append('/var/www/html/catalog')
 
from project import app as application
application.secret_key = "california"
