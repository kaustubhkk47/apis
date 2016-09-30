from fabric.api import *
from fabtools import service
 
# Define sets of servers as roles
TEST_APP_DIR = "/home/probzip/webapps/wholdus_api_test_app/"
PROD_APP_DIR = "/home/aditya/webapps/wholdus-apis/apis/"
SERVER_USER = "aditya@52.187.33.84"
 
# Set the user to use for ssh
env.user = "aditya"
env.password = "Wholdus_prod@0987"
env.hosts = ["52.187.33.84"]
#env.always_use_pty = False
 
# Restrict the function to the 'web' role

def restart_mysql():
	run("~/webapps/mysql/bin/stop")
	run("~/webapps/mysql/bin/start")
#run("$HOME/webapps/mysql/bin/stop; $HOME/webapps/mysql/bin/start",pty=True)
#run("$HOME/webapps/probzip_apis/apache2/bin/restart")
#just testing

def restart_server():
	run(PROD_APP_DIR + "apache2/bin/restart")

def run_local_test():
	local("python manage.py test --settings=test_settings")

def deploy(message):
	#run_local_test()
	push_to_master(message)
	deploy_prod_server()

def push_to_master(message):
	message = "'" + message + "'"
	local("git add --all")
	local("git commit -m " + message)
	local("git checkout master")
	local("git merge develop --no-edit")
	local("git push origin master")
	local("git checkout develop")

def deploy_prod_server():
	run("cd " + PROD_APP_DIR + " && git checkout .")
	run("cd " + PROD_APP_DIR + " && git pull kaustubh develop --quiet")
	run("cd " + PROD_APP_DIR + " && python manage.py migrate")
	run("echo 'Wholdus_prod@0987' | sudo -S service apache2 restart")