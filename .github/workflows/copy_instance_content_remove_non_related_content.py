def cleanup_directory_for_non_important_models(content_directory, list_of_models, shared_directory):
    #walks through the instance export from looker deployer
    for root, dirs, files in os.walk(content_directory):
        for file in files:
            #Only looking to at dashboard and look files
            if file.endswith(".json") and (file.startswith("Dashboard") or file.startswith("Look")):
                #Complete Filepath for the current file
                current_file = os.path.join(root, file)
                file_contains_model = False
                #Read the file
                with open(current_file, 'rb', 0) as file_read, \
                mmap.mmap(file_read.fileno(), 0, access=mmap.ACCESS_READ) as s:
                    #searches for model name
                    for model in list_of_models:
                        model_as_bytes = str.encode(model)
                        if s.find(model_as_bytes) != -1:
                            file_contains_model = True
                    #if file doesn't contain model, then delete
                    if file_contains_model == False:
                        print(current_file)
                        os.remove(current_file)

    #walks through the instance export and deletes empty directories
    for root, dirs, files in os.walk(shared_directory, topdown=False):
        #check for subdirectories
        directoryCounter = 0
        for _, dirs, _ in os.walk(root):
            directoryCounter += len(dirs)
        if root != shared_directory and directoryCounter == 0:
            contentCounter = 0
            #Counts only content files
            for file in files:
                if file.endswith(".json") and (file.startswith("Dashboard") or file.startswith("Look")):
                    contentCounter += 1
            try:
                if contentCounter == 0:
                    print( "Deleting", os.path.join(root, file) )
                    try:
                        #need to delete the space file
                        for file in files:
                            os.remove(os.path.join(root,file))
                        os.rmdir( root )
                    except:
                        print( "FAILED :", os.path.join(root) )
                        pass
            except:
                pass

def relative_root(path,removal_path):
    relative_root = path.replace(removal_path,'')
    return(relative_root)

def check_if_file_exists_in_new_location(comparison_directory,comparison_directory_full,original_relative_root,original_file):
    check_result = False
    relative_root_to_delete_from = ''
    for root, __, files in os.walk(comparison_directory):
        comparison_relative_root = relative_root(path=root,removal_path=comparison_directory_full)
        for file in files:
            if file == original_file:
                if comparison_relative_root != original_relative_root:
                    check_result = True
                    break
            if check_result == True:
                break
        if check_result == True:
            break

    if check_result == True:
        relative_root_to_delete_from = comparison_relative_root
    return(relative_root_to_delete_from)

def check_if_file_exists(comparison_directory,comparison_directory_full,original_relative_root,original_file):
    check_result = False
    relative_root_to_delete_from = ''
    for root, __, files in os.walk(comparison_directory):
        comparison_relative_root = relative_root(path=root,removal_path=comparison_directory_full)
        for file in files:
            if file == original_file:
                check_result = True
                break
        if check_result == True:
            break
    if check_result == False:
        relative_root_to_delete_from = comparison_relative_root
    return(relative_root_to_delete_from)

def delete_file(path):
    if os.path.exists(path):
        os.remove(path)
    else:
        print("Warning: " + path + " does not exist")

import mmap
import os
import sys
import shutil
from distutils.dir_util import copy_tree

#obtain directory
#Git
git_directory = str(sys.argv[1]) #will be .
git_content_directory = git_directory + "/instance_content"
git_shared_directory = git_content_directory + "/Shared"
#Exported
exported_content_directory = str(sys.argv[2]) #will be ./instance_content_new
exported_shared_directory = exported_content_directory + "/Shared"
#Copied Content
copied_content_directory = git_directory + "/instance_content_copied"
copied_shared_directory = copied_content_directory + "/Shared"

#variables
list_of_models = []

#create a list of models in the project
for root, dirs, files in os.walk(git_directory):
    for file in files:
        #Only looking for model files
        if file.endswith(".model.lkml"):
            list_of_models.append("\"model\": \""+file.split(".")[0]+"\"")

#1- you need to cleanup the freshed exported directory for files we care about
cleanup_directory_for_non_important_models(content_directory=exported_content_directory, list_of_models=list_of_models, shared_directory=exported_shared_directory)

#2- you need to copy the existing content directory 
copy_tree(git_content_directory, copied_content_directory)

#3- you need to cleanup the existing content directory for the files we are about (so it's an apples to apples comparison for the next section)
cleanup_directory_for_non_important_models(content_directory=copied_content_directory, list_of_models=list_of_models, shared_directory=copied_shared_directory)

#4- determine if the file was moved, deleted, added, or changed
# First determine if a file was moved (compare copied and export), if it was then delete out of copied directory and git directory
for root, dirs, files in os.walk(exported_shared_directory):
    exported_relative_root = relative_root(path=root,removal_path=exported_content_directory)
    for file in files:
        relative_root_to_delete_from = check_if_file_exists_in_new_location(comparison_directory=copied_shared_directory,comparison_directory_full=copied_content_directory,original_relative_root=exported_relative_root,original_file=file)
        if relative_root_to_delete_from != '':
            git_file_to_delete = git_content_directory + relative_root_to_delete_from + "/" + file
            copied_file_to_delete = copied_content_directory + relative_root_to_delete_from + "/" + file
            print("DELETING " + git_file_to_delete + " because cause it was moved")
            delete_file(git_file_to_delete)
            delete_file(copied_file_to_delete)
        else:
            next

# Second determine if the file was deleted (compare copied and export), if it was then delete out of copied directory and git directory
for root, dirs, files in os.walk(copied_shared_directory):
    copied_relative_root = relative_root(path=root,removal_path=copied_content_directory)
    for file in files:
        relative_root_to_delete_from = check_if_file_exists(comparison_directory=exported_shared_directory,comparison_directory_full=exported_content_directory,original_relative_root=copied_relative_root,original_file=file)
        if relative_root_to_delete_from != '':
            git_file_to_delete = git_content_directory + relative_root_to_delete_from + "/" + file
            copied_file_to_delete = copied_content_directory + relative_root_to_delete_from + "/" + file
            print("DELETING " + git_file_to_delete + " because cause it does not exist")
            delete_file(git_file_to_delete)
            delete_file(copied_file_to_delete)
        else:
            next

# Third merge directories from third step to git directory
shutil.copytree(exported_shared_directory,git_shared_directory,dirs_exist_ok=True)
shutil.rmtree(exported_content_directory)
shutil.rmtree(copied_content_directory)
