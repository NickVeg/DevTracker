import re
import json
from database import get_document
from database import ClickhouseData
from ml_model import classify_commit_messages, predict_job_role
from collaboration import fetch_collaboration_network, replace_aliases_with_primary

# Load the whitelist
with open('developer_profile/whitelist.json') as f:
    whitelist = json.load(f)


class DeveloperProfile:
    def __init__(self, author_id, date_range=None, projects=None):
        self.author_id = author_id
        self.date_range = date_range
        self.projects = projects
        self.author_profile = self.get_author_profile()

        author_names = [self.author_profile['AuthorName']]
        ## To work without aliases and just AuthorName just comment out the next and then replace aliases with primary
        if 'aliases' in self.author_profile and isinstance(self.author_profile['aliases'], list):
           author_names.extend(self.author_profile['aliases'])
        author_names =list(set(author_names)) #To avoid duplicates
        self.clickhouse_data = ClickhouseData(author_names, self.date_range, self.projects)

        # Fetch collaboration network of the author and add data to author_profile
        collaboration_network = fetch_collaboration_network(author_names)
        collaboration_network = replace_aliases_with_primary(collaboration_network, self.author_profile['AuthorName'], author_names)
        # Transform the data to a version ready for visualization
        self.author_profile['collaboration_network'] = self.transform_network_for_viz(collaboration_network)

    def get_author_profile(self):
        author_doc = get_document(self.author_id)
        AuthorName = author_doc.get("AuthorID")
        num_commits = author_doc.get("NumCommits")
        num_projects = author_doc.get("NumProjects")
        num_files = author_doc.get("NumFiles")
        file_info = author_doc.get("FileInfo",{})
        api_info = author_doc.get("ApiInfo",{})
        aliases = author_doc.get("Alias", None)
        num_originating_blobs = author_doc.get("NumOriginatingBlobs")

        popular_libraries, not_matched_libraries = self.filter_popular_libraries(api_info, whitelist)

        author_profile = {
            "AuthorName": AuthorName,
            "num_commits": num_commits,
            "num_projects": num_projects,
            "num_files": num_files,
            "file_info": file_info,
            "popular_libraries": popular_libraries,
            "not_matched_libraries": not_matched_libraries,
            "aliases": aliases,
            "num_originating_blobs": num_originating_blobs
        }
        return author_profile

    def create_profile(self):
        task_categories = classify_commit_messages(self.clickhouse_data)
        self.author_profile['task_categories'] = task_categories

        projects_and_commits = self.clickhouse_data.get_projects_and_commits()
        self.author_profile['projects_and_commits'] = projects_and_commits

        job_role = predict_job_role(self.author_profile['AuthorName'])
        self.author_profile['job_role'] = job_role

        print(job_role)

        language_use_over_time = self.clickhouse_data.get_language_use_over_time()
        self.author_profile['language_use_over_time'] = language_use_over_time

        commit_heatmap = self.clickhouse_data.get_commit_heatmap()
        self.author_profile['commit_heatmap'] = commit_heatmap

        return self.author_profile
    
    def filter_and_update(self, date_range=None, projects=None):
        self.date_range = date_range
        self.projects = projects
        self.clickhouse_data.df = self.clickhouse_data.filter_dataframe(date_range=self.date_range, projects=self.projects)

    def filter_popular_libraries(self, api_info, whitelist):
        popular_libraries = []
        not_matched_libraries = []

        for library_info, count in api_info.items():
            programming_language, library = library_info.split(':')
            if programming_language in whitelist:
                for lib_name, lib_info in whitelist[programming_language].items():
                    if any(re.search(library, import_entry, re.IGNORECASE) for import_entry in lib_info["imports"]):
                        popular_libraries.append({
                            "library_name": lib_name,
                            "programming_language": programming_language,
                            "count": count,
                            "description": lib_info["description"]
                        })
                        break
                else:
                    not_matched_libraries.append({
                        "library_name": library,
                        "programming_language": programming_language,
                        "count": count,
                    })
            else:
                not_matched_libraries.append({
                    "library_name": library,
                    "programming_language": programming_language,
                    "count": count,
                })

        popular_libraries.sort(key=lambda x: x['count'], reverse=True)
        not_matched_libraries.sort(key=lambda x: x['count'], reverse=True)
        return popular_libraries, not_matched_libraries

    def transform_network_for_viz(self, network):
        nodes = []
        edges = []
        for node, neighbours in network.items():
            nodes.append({"id": node, "label": node})
            for neighbour, attributes in neighbours.items():
                edges.append({"from": node, "to": neighbour, "value": attributes['projects']})
        return {"nodes": nodes, "edges": edges}

