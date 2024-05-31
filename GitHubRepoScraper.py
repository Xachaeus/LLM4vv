from github import Auth, Github
import time, json, GetRepo
import numpy as np
import multiprocessing as mp
from functools import partial

repos_to_scrape = ["OpenACCUserGroup/OpenACCV-V"]#, "UD-CRPL/ppm_one", "matt-stack/PhysiCell_GPU", "uhhpctools/openacc-npb",
                   #"NCAR/MURaM_main", ]
extensions_to_check = [".cpp",".c", ".F90"]
headers_to_check = [".h", ".Fh"]
c_libraries_to_check = ["omp.h", "openacc.h", "#pragma omp", "#pragma acc"]
f_libraries_to_check = ["USE OPENACC", "USE omp_lib"]
destination_file = "Test_Files/Passing_Codes.txt"
file_separator = "\n########## NEXT FILE ##########\n"
do_logging = True



class Clock:
    def __init__(self):
        self.start_time = time.time()
    
    def reset(self):
        self.start_time = time.time()
    def log(self):
        log(f"Time Elapsed: {time.time()-self.start_time}s")

def log(*args, **kwargs):
    global do_logging
    if do_logging: print(*args, **kwargs)
    
def search_for_text(files, text):
    passing_files = []
    for file in files:
        try:
            content = file.decoded_content.decode()
        except:
            continue
        
        for val in text:
            if content.find(val) > 0:
                log(f"Found {val} in file {file.name}!")
                passing_files.append(file)
                break
    return passing_files



def advanced_search(files, libraries, headers):
    passing_files = []
    for file in files:
        passes = False
        log(f"\nChecking file {file.repository.name}/{file.name}... ", end="")
        #passes = False #break out of loop if file passes
        try:
            content = file.decoded_content.decode()
        except:
            log("Failure to read file!")
            continue
        
        for header in libraries:
            if content.find(header)>0:
                log(f"Found {header}!", end="")
                passing_files.append(file)
                passes = True
                break
            
        if passes: continue
        
        for local_header in headers:
            if local_header.repository.name != file.repository.name: continue
            header = local_header.name
            if content.find(header)>0:
                log(f"Found {header}!", end="")
                passing_files.append(file)
                break
    return passing_files



def single_advanced_search(libraries, headers, header_repos, file, file_repo):
    if file is None: return None    
    return_val = None
    
    for header in libraries:
        if file.find(header)>0:
            return file
    
    for header in headers:
        if header_repos[headers.index(header)] != file_repo: continue
        header = local_header.name
        if file.find(header)>0:
            return file
    
    return return_val

def check_content(file):
    if file is None: return None
    return file.decoded_content.decode()

def check_repo(file):
    if file.repository is None: print(f"File {file} failed!"); return None
    print(file.repository.name)
    return file.repository.name

def check_name(file):
    
    return file.name



###START OF SCRIPT

if __name__=="__main__":

    clock = Clock()

    auth = Auth.Token("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")
    g = Github(auth=auth)

    c_target_files = []
    c_target_file_repos = []
    f_target_files = []
    c_header_files = []
    f_header_files = []
    #requires
    clock.reset()
    for name in repos_to_scrape:
        log(f"Getting content from repo {name}...")
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
                        c_target_files.append(file) if extension!=".F90" else f_target_files.append(file)
                        break
                except: pass
            for header in headers_to_check:
                try:
                    if file.name[-(len(header)):] ==  header:
                        c_header_files.append(file) if header!=".Fh" else f_target_files.append(file)
                        break
                except: pass
                



    log("Done checking repos!")
    clock.log()
    clock.reset()

    #Update header references
    log("\nUpdating header references...")

    c_passing_headers = search_for_text(c_header_files, c_libraries_to_check)
    f_passing_headers = search_for_text(f_header_files, f_libraries_to_check)

    log("Done!")
    clock.log()
                
    #Find all files with specified text/desired libraries included
    passing_files = c_passing_headers + f_passing_headers
    #min_length = min([len(s) for s in c_libraries_to_check])
    clock.reset()

    pool = mp.Pool()
    
    #log("Getting file contents...")
    #contents = pool.map(check_content, c_target_files)
    log("Getting parent repos...")
    [f.repository for f in c_target_files]
    repos = pool.map(check_repo, c_target_files)
    
    header_names = pool.map(check_name, c_passing_headers)
    header_repos = pool.map(check_repo, c_passing_headers)
    
    c_search = partial(single_advanced_search, c_libraries_to_check, header_names, header_repos)
    passing_files = pool.starmap(c_search, zip(contents, repos))

    #log("\n\nDone checking files! Passing files are:\n" + '\n'.join([f"{f.repository.name}/{f.name}" for f in passing_files]))
    clock.log()

    clock.reset()
    final_string = ""
    for file in passing_files:
        if file is not None: final_string += file_separator + file
    with open(destination_file, 'w') as f:
        f.write(final_string)
                
    clock.log()

    g.close()

