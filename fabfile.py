from fabric.api import *
from fabtools import service
 
# Define sets of servers as roles
APP_NAME = "wholdus_api_test_app/"
SERVER_USER = "probzip@probzip.webfactional.com"
 
# Set the user to use for ssh
env.user = "probzip"
env.password = "Probzip@1234"
env.hosts = ["probzip.webfactional.com"]
#env.always_use_pty = False
 
# Restrict the function to the 'web' role

def restart_server():
	service.stop("$HOME/webapps/mysql/bin")
#run("$HOME/webapps/mysql/bin/stop; $HOME/webapps/mysql/bin/start",pty=True)
#run("$HOME/webapps/probzip_apis/apache2/bin/restart")

def run_local_tests():
	local("python manage.py test --settings=test_settings")