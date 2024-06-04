import git, subprocess, shutil, stat, os, platform, glob
from time import time
from functools import partial
from github import Auth, Github
import multiprocessing as mp

repos = ["https://github.com/matt-stack/PhysiCell_GPU.git","https://github.com/OpenACCUserGroup/OpenACCV-V.git","https://github.com/uhhpctools/openacc-npb.git","https://github.com/UD-CRPL/ppm_one.git","https://github.com/NCAR/MURaM_main.git"]

root_dir = "D:/Programming/CRPL/LLM4vv/SearchAlgorithm-v2/"
shellx = "D:/Programming/CRPL/LLM4vv/SearchAlgorithm-v2/shell2.sh"
#shellx = root_dir+"shell2.sh"
clonedestx = "G:/Programming/CRPL/LLM4vv/SearchAlgorithm-v2/fol"
#clonedestx = root_dir+"fol"
output_dir = "G:/Programming/CRPL/LLM4vv/SearchAlgorithm-v2/outputs"
#output_dir = root_dir+"outputs"
outputfilex= "D:/Programming/CRPL/LLM4vv/SearchAlgorithm-v2/output.txt"
#outputfilex = root_dir+"output.txt"
bash_path = "C:/cygwin64/bin/bash.exe"

phrase_c_x = ["omp.h", "openacc.h","#pragma omp", "#pragma acc"]
phrase_f_x = ["USE OPENACC", "USE OPENMP","!$omp", "!$acc"]

def onerror(func, path, exc_info):
    """
    Error handler for ``shutil.rmtree``.

    If the error is due to an access error (read only file)
    it attempts to add write permission and then retries.

    If the error is for another reason it re-raises the error.
    
    Usage : ``shutil.rmtree(path, onerror=onerror)``
    """
    # Is the error an access error?
    if not os.access(path, os.W_OK):
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise

def clone_repo(repo_url, dest_dir):
    try:
        git.Repo.clone_from(repo_url, dest_dir)
    except Exception as e:
        print(f"Error cloning the {repo_url}: {e}")
        
def search_for_repositories(g, queries, max_repos_query=75):

    repositories = []

    for query in queries:
        repos = g.search_repositories(query=query)
        count = 0
        for repo in repos:
            if count > max_repos_query:
                break
            rc = repo.html_url + ".git"
            repositories.append(rc)
            count += 1

    return repositories


def Search_For_Phrase(phrases_c, phrases_f,clone_dest,shell,repo_url):
    dest_dir = clone_dest +'/'+ repo_url.replace('.','').replace('/','').replace(':','')
    outputfile = output_dir + '/' + repo_url.replace('.','').replace('/','').replace(':','') + '.txt'
    logfile = dest_dir+'/log.txt'
    print(f"Processing repo {repo_url}...")
    clone_repo(repo_url,dest_dir)
    #print("Done!\nSearching for phrases...\n")
    
    for phrase in phrases_c:
        #print(f"Searching for phrase '{phrase}' in repo {repo_url[19:]}...")
        if platform.system() == "Windows":
            result = subprocess.run([bash_path, "-l", shell,phrase,dest_dir,logfile,outputfile,"1"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        else:
            result = subprocess.run([shell,phrase,dest_dir,logfile,outputfile,"1"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        #print(result.stdout, end="")
        print(result.stderr, end="")
        
    open(logfile, 'w').close()
        
    for phrase in phrases_f:
        #print(f"Searching for phrase '{phrase}'...")
        if platform.system() == "Windows":
            result = subprocess.run([bash_path, "-l", shell,phrase,dest_dir,logfile,outputfile,"2"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        else:
            result = subprocess.run([shell,phrase,dest_dir,logfile,outputfile,"2"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        #print(result.stdout, end="")
        print(result.stderr, end="")
        
        
    shutil.rmtree(f"{dest_dir}", onerror=onerror)
    print(f">>> Finished processing repo {repo_url}!")


if __name__=="__main__":
    start_time = time()
    try:
        shutil.rmtree(f"{clonedestx}", onerror=onerror)
        print("Removed destination directory!")
    except Exception as e:
        if(type(e) != FileNotFoundError): print(f"Could not remove directory {clonedestx}: {e}")
    try:
        shutil.rmtree(f"{output_dir}", onerror=onerror)
        print("Removed output directory!")
    except Exception as e:
        if(type(e) != FileNotFoundError): print(f"Could not remove directory {output_dir}: {e}")
        
    os.mkdir(clonedestx)
    os.mkdir(output_dir)
    
    open(outputfilex, 'w').close()
    
    print("Searching for appropriate repositories...")

    auth = Auth.Token("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")
    g = Github(auth=auth)

    queries = ["OpenMP", "OpenACC"]

    repos = search_for_repositories(g,queries,75)
    
    print("Done!")
    
    pool = mp.Pool(8)
    func = partial(Search_For_Phrase, phrase_c_x,phrase_f_x,clonedestx,shellx)
    pool.map(func, repos)
    pool.close()
    
    print("Concatenating all outputs to single file...")
    
    with open(outputfilex, 'w') as outfile:
        for filename in glob.glob(output_dir+'/*'):
            with open(filename, 'r') as infile:
                try:
                    shutil.copyfileobj(infile,outfile)
                except:
                    print(f"Problem reading file {filename}, skipping...")
                
        

    print(f"Done!\nTotal processing time: {time() - start_time} seconds")
    shutil.rmtree(f"{clonedestx}", onerror=onerror)
    shutil.rmtree(output_dir, onerror=onerror)
    quit()    