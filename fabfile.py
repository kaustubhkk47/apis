from fabric.api import *
from fabtools import service
 
# Define sets of servers as roles
TEST_APP_DIR = "/home/kaustubh/webapps/wholdus-apis/apis/"
PROD_APP_DIR = "/home/aditya/webapps/wholdus-apis/apis/"
SERVER_USER = "aditya@52.187.33.84"
 
# Set the user to use for ssh

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
	message = "'" + message + "'"
	push_to_master(message)
	deploy_prod_server()
	deploy_test_server()

def push_to_master(message):
	local("git add --all")
	local("git commit -m " + message)
	local("git checkout master")
	local("git merge develop --no-edit")
	local("git push origin master")
	local("git checkout develop")
	local("git push origin develop")

def deploy_prod_server():
	env.user = "aditya"
	env.password = "Wholdus_prod@0987"
	env.hosts = ["52.187.33.84"]
	run("cd " + PROD_APP_DIR + " && git checkout .")
	run("cd " + PROD_APP_DIR + " && git pull kaustubh master")
	run("cd " + PROD_APP_DIR + " && python manage.py migrate")
	run("echo 'Wholdus_prod@0987' | sudo -S service apache2 restart")

def deploy_test_server():
	env.user = "kaustubh"
	env.password = "Wholdus_test@0987"
	env.hosts = ["13.76.211.119"]
	run("cd " + TEST_APP_DIR + " && git checkout .")
	run("cd " + TEST_APP_DIR + " && git pull origin develop")
	run("cd " + TEST_APP_DIR + " && python manage.py migrate")