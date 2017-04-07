from flask import Flask
from flask import url_for
from flask import jsonify
from flask import render_template
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
        return url_for('index_route', sort=col_key, direction=direction)

@app.route('/table_widget.html')
def get_table__widget_route():
    repos = get_repos()
    table_html = get_table_html(repos)
    return table_html 

@app.route('/get_repos')
def get_repos_route():
    return jsonify(get_repos())

def get_table_html(repos):
    repo_table = RepoTable(repos)
    return repo_table.__html__()

@app.route('/')
def index_route():
    repos = get_repos()
    html = render_template('custom.html', repos=repos)
    return html

def travis_badger(repo):
    return 'https://img.shields.io/travis/{}.svg'.format(repo.full_name)

def coveralls_badger(repo):
    return 'https://img.shields.io/coveralls/{}.svg'.format(repo.full_name)

badgeToBadger = {
	'Travis' : travis_badger,
        'Coveralls': coveralls_badger
}

def transform_repos(repos):
    return map(transform_repo, repos)

#'
#' @param repos - list of PyGithub Repository objects
def transform_repo(repo):
    badges = []
    for badge, badger in badgeToBadger.iteritems():
        badge_url = badger(repo)
        badges.append({
            'name' : badge,
            'url' : badge_url
        })

    dict_repo = {
        'full_name' : repo.full_name,
        'name' : repo.name,
        'html_url' : repo.html_url,
        'description' : repo.description,
        'badges' : badges
    }
    print(dict_repo)
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
    print len(repos)
    transformed_repos = transform_repos(repos)

    return transformed_repos
   
def write_repos_to_file(the_file):
    g = Github()
    org = g.get_organization('USGS-CIDA')
    paged_repos = org.get_repos()
    repos = []
    for repo in paged_repos:
           repos.append(repo) 
    pickle.dump(repos, the_file)
    return repos
    
