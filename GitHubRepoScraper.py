from github import Auth, Github

repos_to_scrape = ["UD-CRPL/ppm_one"]
extensions_to_check = [".cpp",".c",".h"]
libraries_to_check = ["<omp.h>", "<openacc.h>", "use openacc"]
destination_file = "Test_Files/Passing_Codes.txt"


     

auth = Auth.Token("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")
g = Github(auth=auth)

target_files = []

for name in repos_to_scrape:
    repo = g.get_repo(name)
    contents = repo.get_contents("")
    files = []
    
    #Get all files in repo
    while contents:
        file_content = contents.pop(0)
        if file_content.type == "dir":
            contents.extend(repo.get_contents(file_content.path))
        else: files.append(file_content)


    #Find all files with desired file extensions
        
    for file in files:
        for extension in extensions_to_check:
            try:
                if file.name[-(len(extension)):] == extension :
                    target_files.append(file)
                    break
            except: pass
            
#Find all files with specified text/desired libraries included
passing_files = []
    
min_length = min([len(s) for s in libraries_to_check])

for file in target_files:
    passes = False #break out of loop if file passes
    try:
        content = file.decoded_content.decode()
    except:
        continue
        
    length = len(content)
    for i in range(length//min_length): #iterate every x characters
        if passes: break
        c = content[i]
        for header in libraries_to_check:
            index = header.find(c)
            if index<0: break #wrong character
            start = i-index
            if content[start:start+len(header)] == header:
                passing_files.append(file)
                passes = True
                break
            
#Write passing files to single text file   
print(passing_files)
full_string = ""
for file in passing_files:
    full_string += file.decoded_content.decode()
    full_string += "\n########## NEXT FILE ##########\n"
with open(destination_file, 'w') as f:
    f.write(full_string)
            
    

g.close()

