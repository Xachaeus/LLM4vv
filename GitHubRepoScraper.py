from github import Auth, Github
from numba import cuda
import time, json, GetRepo
import numpy as np

repos_to_scrape = ["OpenACCUserGroup/OpenACCV-V"]#, "UD-CRPL/ppm_one", "matt-stack/PhysiCell_GPU", "uhhpctools/openacc-npb",
                   #"NCAR/MURaM_main", ]
extensions_to_check = [".cpp",".c", ".F90"]
headers_to_check = [".h", ".Fh"]
c_libraries_to_check = ["omp.h", "openacc.h", "#pragma omp", "#pragma acc"]
f_libraries_to_check = ["USE OPENACC", "USE omp_lib"]
destination_file = "Test_Files/Passing_C-CPP_Codes.txt"
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

@cuda.jit
def get_content(arr, dest_arr):
    index = cuda.grid(1)
    if index < arr.shape[0]:
        if(arr[index][0] == "a"):
            dest_arr[index] = 1
        else:
            dest_arr[index] = 0

###START OF SCRIPT

clock = Clock()

auth = Auth.Token("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")
g = Github(auth=auth)

c_target_files = []
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

files_arr = np.array([f.name for f in c_target_files])
dest_arr = files_arr
new_arr = cuda.to_device(files_arr)
get_content[512,64](files_arr, dest_arr)
#files_arr = dest_arr.copy_to_host()
print(dest_arr)
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
passing_files += advanced_search(c_target_files, c_libraries_to_check, c_passing_headers)
passing_files += advanced_search(f_target_files, f_libraries_to_check, f_passing_headers)



log("\n\nDone checking files! Passing files are:\n" + '\n'.join([f"{f.repository.name}/{f.name}" for f in passing_files]))
clock.log()

final_string = ""
for file in passing_files:
    final_string += file_separator + "::: " + file.name + " :::\n" + file.decoded_content.decode()
with open(destination_file, 'w') as f:
    f.write(final_string)
            
    

g.close()

