from github import Github
import pandas as pd

class GithubAPIHandler:
    def __init__(self, token):
        self.github_obj = Github(token)

    def get_author_repo_info(self, author_name_email):
        name, email = author_name_email.split("<")
        name = name.strip()
        email = email.replace(">", "").strip()
        
        print(email)
        print(name)
        
        repositories = self.github_obj.search_users(query=f"{name} in:fullname").get_page(0)

        if len(repositories) > 0:
            author = repositories[0]  # The first result is usually the most accurate
        else:
            raise ValueError("No GitHub user found with provided name and email.")
        

        repo_data = []

        for repo in author.get_repos():
            try:
                readme = repo.get_readme().decoded_content.decode('utf-8')
            except:
                readme = None
            try:
                tags = ''.join(repo.get_topics())
            except:
                tags = None

            repo_data.append({'repo_name': repo.name, 
                            'description': repo.description,
                            'repo_tags': tags, 
                            'readme_text': readme}, )
        
        df = pd.DataFrame(repo_data)
        
        return df
