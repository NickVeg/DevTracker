# DevTracker

This repository contains the code for DevTracker. DevTracker is a profiling tool designed to create insightful profiles for developers, leveraging their commit history across various forges like GitHub, GitLab, Bitbucket, and others. It utilizes the World of Code (WoC) infrastructure to provide users with comprehensive profiles based on individual developer contributions, offering a detailed overview of a developer's coding footprint.

This tool was developed as part of a thesis project titled "Development of a Profiling Application for Software Engineers from Open Source Software Repository Data".

## Installation/Setup

### Virtual Environment Setup
1. Set up a virtual environment in your project directory to keep the project dependencies isolated.
2. Once the virtual environment is activated, install the necessary dependencies using the provided __`requirements.txt`__ file.
   ```sh
   pip install -r requirements.txt

### GitHub Token

- A GitHub account is required to use this tool.
- Generate a GitHub token by following the [GitHub Token Creation Guide](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)
- After generating the token, set it as an enviroment variable named __'GITHUB_TOKEN'__.

## Usage

### World of Code Registration

- To access the WoC infrastucture, follow the registration instructions provided [here](https://github.com/woc-hack/tutorial).
- This involves generation a public SSH key and including it in the WoC registration form.

### Connection to Servers

- Before running the tool, connect to the __'da3'__ and __'da1'__ servers of the WoC infrastucture.
- The connection needs to be established every time before running the tool.

## Running the Tool

- After completing the the installation and setup, and connecting to the servers, run __'app.py'__ to start using the tool.
````sh
  python app.py



