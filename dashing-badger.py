from flask import Flask, url_for
app = Flask(__name__)
from github import Github
from flask_table import Table, Col
from pprint import PrettyPrinter
import pickle 

CACHED_FILE_NAME = 'cached_repos.pickle'

# Declare your table
class RepoTable(Table):
    allow_sort = True
    name = Col('name')
    description = Col('description')
    full_name = Col('full_name')
    html_url = Col('html_url')

    def sort_url(self, col_key, reverse=False):
        if reverse:
            direction =  'desc'
        else:
            direction = 'asc'
        return url_for('index', sort=col_key, direction=direction)

@app.route('/')
def index():
    repos = get_repos()
    transformed_repos = transform_repos(repos)
    table_html = get_table_html(transformed_repos)
    return table_html 

def get_table_html(repos):
    repo_table = RepoTable(repos)
    return repo_table.__html__()


def transform_repos(repos):
    return map(transform_repo, repos)

#'
#' @param repos - list of PyGithub Repository objects
def transform_repo(repo):
#    dict_repo = dict((key, value) for key, value in repo.__dict__.iteritems() 
#        if not callable(value) and not key.startswith('__'))
#    print(dir(dict_repo))
    dict_repo = repo.__dict__
    print(dict_repo)
    exit()
    return dict_repo

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
    
