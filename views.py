from flask import render_template, request, jsonify
from developer_profile.developer_profile import DeveloperProfile
from database.mongodb import get_documents, get_project, get_api
from datetime import datetime
from extensions import cache  # Directly import the cache object
import inspect
import logging


def home():    
    return render_template('home.html')

def make_cache_key(*args, **kwargs):
    path = request.path
    args = str(hash(frozenset(request.args.items())))
    form = str(hash(frozenset(request.form.items())))
    return (path+args+form).encode('utf-8')


@cache.memoize(timeout=60*60*24*30, make_name=make_cache_key)  # Cache for one day
def search():
    # This does the author search and renders the author_matches page
    author_name = request.form['author_name']
    matches = get_documents(author_name)

    
    return render_template('author_matches.html', matches=matches)


profiles={}
dev_object={}

def my_memoize_make_cache_key(f, *args, **kwargs):
    argnames = list(inspect.signature(f).parameters.keys())
    kwargs.update(zip(argnames, args))
    key = 'profile_{}'.format(kwargs['author_id'])
    return key.encode('utf-8')



@cache.memoize(timeout=60*60*24*30)  # Cache 
def create_and_cache_profile(author_id):
    developer = DeveloperProfile(author_id) #Just the object
    dev_object[author_id] = developer #Save the developer oject
    profile = developer.create_profile() #Create the profile

    return profile


def author_overview(author_id):   
    profile = create_and_cache_profile(author_id)    
    profiles[author_id] = profile  # Save the profile for share_profile to use

    return render_template('overview.html', profile=profile)

def share_profile(author_id):
    if author_id in profiles:
        profile = profiles[author_id]
    else:
        profile = create_and_cache_profile(author_id)
        profiles[author_id] = profile

    return render_template('share_profile.html', profile=profile)


def author_overview_filtered(author_id):
    if request.method == 'POST':
        start_date_str = request.form.get('start_date', '')
        end_date_str = request.form.get('end_date', '')

        start_date = datetime.strptime(start_date_str, '%Y-%m-%d') if start_date_str else None
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d') if end_date_str else None
        date_range = (start_date, end_date) if start_date and end_date else None

        projects = request.form.get('projects')

        developer = dev_object.get(author_id) #New dictionary with objects(DeveloperProfile)
        if not developer:
            developer = DeveloperProfile(author_id, date_range, projects)
            dev_object[author_id] = developer
        else:
            # If it is in the cache, apply the filters to it
            developer.filter_and_update(date_range, projects)
        profile = developer.create_profile()

        profiles[author_id] = profile
        return render_template('overview.html', profile=profile)

def project(project_id):
    project_summary = get_project(project_id)
    return render_template('project.html', project_summary = project_summary)

def api(API):
    api_summary = get_api(API)
    return render_template('api.html', api_summary = api_summary)
