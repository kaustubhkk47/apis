from fabric.api import *
 
# Define sets of servers as roles
APP_NAME = "wholdus_api_test_app/"
SERVER_USER = "probzip@probzip.webfactional.com"
 
# Set the user to use for ssh
env.user = "probzip"
env.password = "Probzip@1234"
env.hosts = ["probzip.webfactional.com"]
 
# Restrict the function to the 'web' role

def ssh_into_server():
	local("ssh " + SERVER_USER)

def get_version():
    run('cat /etc/issue')

def restart_server():
	run("~/webapps/"+APP_NAME+"apache2/bin/restart")
	run("~/webapps/mysql/bin/start")