from pymongo import MongoClient

# Specify the host and port
host = 'localhost'
port = 27017

# Define the mongodb client and databases
mongodb_client = MongoClient(host, port)
db = mongodb_client["WoC"]
coll1 = db["A_metadata.U"]
coll2 =db["P_metadata.U"]
coll3 = db["API_metadata.U"]

def get_document(AuthorID):
    """
    Returns the document matching the provided query.
    If multiple documents match the query, only the first one is returned.
    If no document matches the query, None is returned.
    """
    query = {"AuthorID": AuthorID}
    return coll1.find_one(query)

def get_documents(author_name, limit=5):
    """
    Returns all documents matching the provided query.
    If limit is provided, only up to limit' documents are returned.
    """
    query = {"AuthorID": {"$regex": author_name, "$options": 'i'}}
    projection = {"AuthorID": 1, "_id": 0}  # This will ensure only 'AuthorID' field is returned
    return coll1.find(query, projection).limit(limit)

def get_project(ProjectID):
    query = {"ProjectID": ProjectID}
    project = coll2.find_one(query)
    if project:
        project_summary = {
            "ProjectID": project["ProjectID"],
            "NumAuthors": project["NumAuthors"],
            "NumCommits": project["NumCommits"],
            "NumBlobs": project.get("NumBlobs"),
            "NumStars": project.get("NumStars"),
            "NumForks": project.get("NumForks"),
            "FileInfo": project.get("FileInfo", {}),
            "Core": project.get("Core", {}),
            "MonNauth": project.get("MonNauth",{}),
            "MonNcmt": project.get("MonNcmt",{})
        }    
        if project.get('MonNauth'):
            project_summary['MonNauth_keys'] = list(project['MonNauth'].keys())
            project_summary['MonNauth_values'] = list(project['MonNauth'].values())
        else:
            project_summary['MonNauth_keys'] = []
            project_summary['MonNauth_values'] = []

        if project.get('MonNcmt'):
            project_summary['MonNcmt_keys'] = list(project['MonNcmt'].keys())
            project_summary['MonNcmt_values'] = list(project['MonNcmt'].values())
        else:
            project_summary['MonNcmt_keys'] = []
            project_summary['MonNcmt_values'] = []

        return project_summary
    else:
        return None
    
def get_api(API):
    query = {"API": API}
    return coll3.find_one(query)