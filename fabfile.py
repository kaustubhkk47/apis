from fabric.api import *
 
# Define sets of servers as roles
APP_NAME = "wholdus_api_test_app/"
SERVER_USER = "probzip@probzip.webfactional.com"
 
# Set the user to use for ssh
env.user = "probzip"
env.hosts = ["probzip.webfactional.com"]
 
# Restrict the function to the 'web' role

def ssh_into_server():
	local("ssh " + SERVER_USER)

def get_version():
    run('cat /etc/issue')

def hello():
    print("Hello world!")

def restart_webserver():
	sudo("~/webapps/"+APP_NAME+"apache2/bin/restart")