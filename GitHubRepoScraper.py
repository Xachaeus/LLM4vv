from github import Auth, Github

repos_to_scrape = ["UD-CRPL/ppm_one"]
extensions_to_check = [".cpp",".c",".F90", ".h"]

     

auth = Auth.Token("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")
g = Github(auth=auth)

for name in repos_to_scrape:
    repo = g.get_repo(name)
    contents = repo.get_contents("")
    files = []
    
    while contents:
        file_content = contents.pop(0)
        if file_content.type == "dir":
            contents.extend(repo.get_contents(file_content.path))
        else: files.append(file_content)
        
        
    for file in files:
        for extension in extensions_to_check:
            try:
                if file.name[-(len(extension)):] == extension : print(file.name)
            except: pass
        



g.close()

