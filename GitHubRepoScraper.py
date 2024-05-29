from github import Auth, Github

repos_to_scrape = ["UD-CRPL/ppm_one", "matt-stack/PhysiCell_GPU"]
extensions_to_check = [".cpp",".c"]
headers_to_check = [".h"]
libraries_to_check = ["omp.h", "openacc.h"]
destination_file = "Test_Files/Passing_C-CPP_Codes.txt"
file_separator = "\n########## NEXT FILE ##########\n"


def search_for_text(files, text):
    passing_files = []
    min_length = min([len(s) for s in text])
    for file in files:
        passes = False #break out of loop if file passes
        try:
            content = file.decoded_content.decode()
        except:
            continue
            
        length = len(content)
        for i in range(length//min_length): #iterate every x characters
            if passes: break
            c = content[i*min_length]
            for val in text:
                index = val.find(c)
                if index<0: break #wrong character
                
                start = (i*min_length)-index
                if content[start:start+len(val)] == val or content[start-1:start+len(val)-1] == val:
                    passing_files.append(file)
                    passes = True
                    break
                
    return passing_files

auth = Auth.Token("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")
g = Github(auth=auth)

target_files = []
header_files = []

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
        for header in headers_to_check:
            try:
                if file.name[-(len(header)):] ==  header:
                    header_files.append(file)
                    break
            except: pass

print("Done checking repos!")

#Update header references
print("\nUpdating header references...")
passing_headers = search_for_text(header_files, libraries_to_check)
libraries_to_check += [f.name for f in passing_headers]
print("Done!")
            
#Find all files with specified text/desired libraries included
passing_files = passing_headers
min_length = min([len(s) for s in libraries_to_check])

for file in target_files:
    print(f"Checking file {file.name}... ", end="")
    passes = False #break out of loop if file passes
    try:
        content = file.decoded_content.decode()
    except:
        print("Failure to read file!")
        continue
        
    length = len(content)
    for i in range(length//min_length): #iterate every x characters
        if passes: break
        c = content[i*min_length]
        for header in libraries_to_check:
            index = header.find(c)
            if index<0: break #wrong character
            
            start = (i*min_length)-index
            if content[start:start+len(header)] == header or content[start-1:start+len(header)-1] == header:
                print(f"Found {header}!", end="")
                passing_files.append(file)
                passes = True
                break
    print("")

print("\nDone checking files! Passing files are:\n" + '\n'.join([f.name for f in passing_files]))
            
#Write passing files to single text file   
full_string = ""
for file in passing_files:
    full_string += file.decoded_content.decode()
    full_string += file_separator
with open(destination_file, 'w') as f:
    f.write(full_string)
            
    

g.close()

