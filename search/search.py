from flask import request, redirect, url_for, render_template
from database.mongodb import get_document, get_documents

def get_author_doc(AuthorID):
    # Query the database for the author document
    author_doc = get_document(AuthorID)

    return author_doc

def search_authors():
    if request.method == 'POST':
        # get author name from form
        author_name = request.form['author_name']    
        
        # query the A_metadata.U collection for potential author matches
        authors = get_documents(author_name, limit=10)
        
        if authors:
            # if matching authors are found, render a new template with these authors
            return render_template('author_matches.html', authors=authors)
        
    # Stay on the home page if no author is found or if the request method is GET
    return render_template('home.html')

