from flask import Flask
app = Flask(__name__)
from github import Github
from flask_table import Table, Col
from pprint import PrettyPrinter
import pickle 

CACHED_FILE_NAME = 'cached_repos.pickle'

# Declare your table
class RepoTable(Table):
    name = Col('name')
    full_name = Col('full_name')
    html_url = Col('html_url')
    description = Col('description')

@app.route('/')
def hello_world():
    repos = get_repos()
    table_html = get_table_html(repos)    
    return table_html 

def get_table_html(repos):
    repo_table = RepoTable(repos)
    return repo_table.__html__()

def get_repos():
    try:
        f = open(CACHED_FILE_NAME, 'rb')
        repos = pickle.load(f)
        print('cache hit, loaded repository information from ' + CACHED_FILE_NAME)
    except IOError:
        print('cache miss, retrieving from github and writing to file ' + CACHED_FILE_NAME)
        f = open(CACHED_FILE_NAME, 'wb')
        repos = write_repos_to_file(f)
    return repos
   
def write_repos_to_file(the_file):
    g = Github()
    org = g.get_organization('USGS-CIDA')
    paged_repos = org.get_repos()
    repos = []
    for repo in paged_repos:
           repos.append(repo) 
    pickle.dump(repos, the_file)
    return repos
    
