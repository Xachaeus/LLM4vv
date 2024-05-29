from github import Auth, Github

repos_to_scrape = ["UD-CRPL/ppm_one"]
extensions_to_check = [".cpp",".c",".h"]
libraries_to_check = ["omp.h", "openacc.h"]
destination_file = "Test_Files/Passing_C-CPP_Codes.txt"
file_separator = "\n########## NEXT FILE ##########\n"


     

auth = Auth.Token("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")
g = Github(auth=auth)

target_files = []

for name in repos_to_scrape:
    print(f"Checking repo {name}...")
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

print("Done checking repos!")
            
#Find all files with specified text/desired libraries included
passing_files = []
min_length = min([len(s) for s in libraries_to_check])

for file in target_files:
    print(f"Checking file {file.name}...", end="")
    passes = False #break out of loop if file passes
    try:
        content = file.decoded_content.decode()
    except:
        print("Failure to read file!")
        continue
    print("")
        
    length = len(content)
    for i in range(length//min_length): #iterate every x characters
        if passes: break
        c = content[i*min_length]
        for header in libraries_to_check:
            index = header.find(c)
            if index<0: break #wrong character
            
            start = (i*min_length)-index
            if content[start:start+len(header)] == header or content[start-1:start+len(header)-1] == header:
                print("Found " + header)
                passing_files.append(file)
                passes = True
                break

print("Done checking files! Passing files are:\n" + '\n'.join([f.name for f in passing_files]))
            
#Write passing files to single text file   
full_string = ""
for file in passing_files:
    full_string += file.decoded_content.decode()
    full_string += file_separator
with open(destination_file, 'w') as f:
    f.write(full_string)
            
    

g.close()

