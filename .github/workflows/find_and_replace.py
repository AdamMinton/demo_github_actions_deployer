import os, fnmatch, json, sys

def findReplace(directory, find, replace, filePattern):
    for path, __, files in os.walk(os.path.abspath(directory)):
        for filename in fnmatch.filter(files, filePattern):
            filepath = os.path.join(path, filename)
            with open(filepath) as f:
                s = f.read()
            s = s.replace(find, replace)
            with open(filepath, "w") as f:
                f.write(s)

json_file_path = "./.github/workflows/environment_variables.json"
environment = str(sys.argv[1])
directory = "./"

with open(json_file_path, 'r') as j:
     contents = json.loads(j.read())

for key in contents:
    search_term = key
    replacement_term = contents[key][environment]
    print(search_term)
    print(replacement_term)
    findReplace(directory=directory,find=search_term,replace=replacement_term,filePattern="*.lkml")
