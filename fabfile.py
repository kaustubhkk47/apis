from fabric.api import *
from fabtools import service
 
# Define sets of servers as roles
TEST_APP_DIR = "/home/probzip/webapps/wholdus_api_test_app/"
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

def run_local_test():
	local("python manage.py test --settings=test_settings")

def deploy(message):
	run_local_test()
	push_to_develop(message)
	deploy_test_server()

def push_to_develop(message):
	message = "'" + message + "'"
	local("git add --all")
	local("git commit -m " + message)
	local("git push origin develop")

def deploy_test_server():
	run("cd " + TEST_APP_DIR + "src/ && git pull origin develop")
	run("cd " + TEST_APP_DIR + "src/ && python manage.py migrate")
	run(TEST_APP_DIR + "apache2/bin/restart")