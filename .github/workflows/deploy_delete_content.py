def output_to_log(message):
    default = 'echo \"\u001b[31m' + message + '\"'
    os.system(default)

def determine_file_looker_object(file_name):
    first_file_part = file_name.split("_")[0]
    if first_file_part == 'Dashboard':
        looker_object = 'dashboard'
    elif first_file_part == 'Look':
        looker_object = 'look'
    else: looker_object = 'unknown'
    return(looker_object)

def retrieve_dashboard_slug(json_file_path):
    with open(json_file_path) as json_file:
        dashboard = json.load(json_file)
        dashboard_slug = dashboard.get('slug')
    return(dashboard_slug)

def retrieve_look_title(json_file_path):
    with open(json_file_path) as json_file:
        look = json.load(json_file)
        look_title = look.get('title')
    return(look_title)

import git
import os
import configparser
import looker_sdk
import json
import sys

#Args from starting python script
repo_directory_arg = str(sys.argv[1]) #./
destination_commit_arg = str(sys.argv[2]) #60b1292a6832da6a3b0d6fae7752d4bd4c82d0cd
section = str(sys.argv[3]) #saleseng
project = str(sys.argv[4]) #demo_github_actions_deployer

#Defaults
ini_file = repo_directory_arg + 'looker.ini'

#Read ini file 
config = configparser.ConfigParser()
config.read(ini_file)
client_id = config[section]['client_id']
client_secret = config[section]['client_secret']
base_url = config[section]['base_url']
url = base_url+'/api/3.1/'

#Parse the host and port
host_start = base_url.find('//') + 2
port_start = base_url.find('m:') + 2
host_end = port_start - 1
port_end = len(base_url)

host = base_url[host_start:host_end]
port = base_url[port_start:port_end]

#Iniate looker sdk
sdk = looker_sdk.init31(config_file = ini_file, section=section)

#Initiate Repo
repo = git.Repo(repo_directory_arg)
commits_list = list(repo.iter_commits())

#Switch to section branch to pull source commit
repo.git.checkout(section)
branch = repo.head.reference
source_commit_arg = branch.commit.hexsha
repo.git.checkout('master')
source_commit = repo.commit(source_commit_arg)
output_to_log("Current Commit is " + source_commit_arg)
destination_commit = repo.commit(destination_commit_arg)
output_to_log("Destination Commit is " + destination_commit_arg)

#Source Commit (A) is compared to Destination Commit (B).
diff = source_commit.diff(destination_commit)

for diff_item in diff:
    diff_item_path = diff_item.a_path.split("/") 
    output_to_log("Diff item is " + diff_item.a_path)
    if diff_item_path[0] == 'instance_content':
        #Only look at differences inside of the instance content
        #Process deletes first to prep instance for full import
        #Change types of R are files that are moved and change types of D are deleted files
        if diff_item.change_type == 'R' or diff_item.change_type == 'D':
            looker_object = determine_file_looker_object(diff_item.a_blob.name)
            if looker_object =='dashboard' or looker_object == 'look':
                looker_dev_id = diff_item.a_blob.name.split("_")[1]
                operation = 'rm'

                #Retrieve instance being deployed to with IDs for content to be deleted                
                if looker_object =='dashboard':
                    dashboard_slug = retrieve_dashboard_slug(repo_directory_arg+diff_item.a_path)
                    dashboard = sdk.search_dashboards(slug=dashboard_slug)
                    try:
                        looker_id = dashboard[0].id
                    except:
                        continue
                elif looker_object == 'look':
                    look_title = retrieve_look_title(repo_directory_arg+diff_item.a_path)
                    look = sdk.search_looks(title=look_title)
                    try:
                        looker_id = look[0].id
                    except:
                        continue
                else: looker_id = 0
                
                output_to_log("Deleting " + diff_item.a_path)
                gzr_command = "gzr " + looker_object + " " + operation + " " + looker_id + " --host=" + host + " --client-id=" + client_id + " --client-secret=" + client_secret + " --port=" + port
                os.system(gzr_command)
