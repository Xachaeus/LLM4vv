queries = ["OpenMP", "OpenACC"]

def search_for_repositories(queries, max_repos_query=75):

    repositories = []

    for query in queries:
        repos = g.search_repositories(query=query)
        count = 0
        for repo in repos:
            if count > max_repos_query:
                break
            repositories.append(repo.full_name)
            count += 1

    return repositories






