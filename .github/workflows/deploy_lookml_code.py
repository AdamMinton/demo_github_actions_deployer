import configparser
import requests
import json
import sys

def generate_auth_token(url, client_id, client_secret): 
    """Generates an access token for the Looker API that can be passed in the required authorization header. These tokens expire in an hour""" 
    data = { 'client_id': client_id, 'client_secret': client_secret } 
    auth_token = requests.post(url+'login', data=data) 
    return auth_token.json().get('access_token') 

def deploy_ref_to_production(commit, project):
    data = { 'ref': commit } 
    response = requests.post(url + '/projects/'+project+'/deploy_ref_to_production', data=data,headers=HEADERS) 
    return response

def deploy_branch_to_production(branch, project):
    data = { 'branch': branch } 
    response = requests.post(url + '/projects/'+project+'/deploy_ref_to_production', data=data,headers=HEADERS) 
    return response

#Passed from github
section = str(sys.argv[1]) #'profservices'

project = 'demo_github_actions_deployer'
ini_file = 'looker.ini'

#Read ini file 
config = configparser.ConfigParser()
config.read(ini_file)
client_id = config[section]['client_id']
client_secret = config[section]['client_secret']
base_url = config[section]['base_url']
url = base_url+'/api/3.1/'

#Obtain authorization token
access_token = generate_auth_token(url,client_id,client_secret)
HEADERS = {
    'Authorization': 'token {}'.format(access_token)
}

#Deploy commit
print(deploy_branch_to_production(section,project))
