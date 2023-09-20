from database.clickhouse import clickhouse_client
from collections import defaultdict
import networkx as nx

def fetch_projects(author):
    query = f"SELECT DISTINCT project FROM b2cPtaPkgR_all WHERE author = '{author}'"
    result = clickhouse_client.execute(query)
    return [row[0] for row in result]

def fetch_collaborators(project):
    query = f"SELECT DISTINCT author FROM b2cPtaPkgR_all WHERE project = '{project}'"
    result = clickhouse_client.execute(query)
    return [row[0] for row in result]

def get_top_collaborators(author, original_author, top_n=5): #top_n dictates how many top collaborators are to be fetched. Default set to 5 for original author
    """
    This function fetches the top collaborators for an author, excluding the provided list of original authors.
    """
    projects = fetch_projects(author)
    collaborator_counts = defaultdict(int)
    for project in projects:
        collaborators = fetch_collaborators(project)
        for collaborator in collaborators:
            # Exclude the original authors and the author
            if collaborator != author and collaborator not in original_author:  #To exclude double edges
                collaborator_counts[collaborator] += 1
    sorted_collaborations = sorted(collaborator_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]
    return dict(sorted_collaborations)

def fetch_collaboration_network(author_list, depth=3): ###!!!
    """
    This function fetches the collaboration network for a list of authors, 
    treating all the authors in the list as the same person (because they're aliases).
    """
    # Assume that author_names is a list of names. 
    # If a single name is provided (string), convert it to a list with a single item.   
    if isinstance(author_list, str):
        author_list=[author_list]

    network = {}
    # Union of all the authors added to the network so far
    added_authors = set(author_list) 
    # Set of authors already processed
    processed_authors = set() 
    # Initialize queue with all authors and depth
    queue = [(author, depth) for author in author_list]

    while queue:
        current_author, current_depth = queue.pop(0)
        if current_depth < 1:
            continue
        top_n = 5 if current_author in author_list else 2 #Fetch top 5 for original and 2 for the rest
        collaborations = get_top_collaborators(current_author, author_list, top_n) # Exclude all authors in the author_list when fetching collaborators
        
        for collaborator in collaborations.keys():
            if collaborator not in added_authors: #Avoid adding one that is already in the netwrok
                queue.append((collaborator, current_depth - 1))
                added_authors.add(collaborator) # Add the author to added_authors 
        
        # Add collaborators to network, with depth and number of shared projects
        network[current_author] = {collaborator: {'depth': current_depth, 'projects': num_projects} 
                                   for collaborator, num_projects in collaborations.items() 
                                   if collaborator not in processed_authors}   
        processed_authors.add(current_author)
    return network

def replace_aliases_with_primary(network, author_name, author_names):
    new_network = {}
    for author, collaborators in network.items():
        if author in author_names:
            if author_name not in new_network:
                new_network[author_name] = {}
            for collaborator, details in collaborators.items():
                if collaborator in author_names:
                    collaborator = author_name
                new_network[author_name][collaborator] = details
        else:
            new_network[author] = {}
            for collaborator, details in collaborators.items():
                if collaborator in author_names:
                    collaborator = author_name
                new_network[author][collaborator] = details
    return new_network
