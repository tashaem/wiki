import random

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django import forms

import markdown2
from markdown2 import Markdown
markdowner = Markdown()

from . import util

# Form for the searchbar feature
class QueryForm(forms.Form):
    query = forms.CharField(label="",widget=forms.TextInput(attrs={'placeholder':'Search Encyclopedia'}))

# Form for creating new entry
class newEntryForm(forms.Form):
    newtitle = forms.CharField(label="Entry title",required=True,widget=forms.TextInput(attrs={'placeholder':'Title'}))
    newcontent = forms.CharField(label="",required=True,widget=forms.Textarea(attrs={'placeholder':'Enter entry content here..'}))

# Form for editting existing entry
class editForm(forms.Form):
    editbox=forms.CharField(label="", widget=forms.Textarea)

def index(request):
    """Home page listing titles of all available entries."""

    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "searchbar": QueryForm()
    })

def results(request):
    """Shows results of search query."""

    # Extracting query data
    form = QueryForm(request.POST)

    if form.is_valid():
        query = form.cleaned_data["query"]

        if util.get_entry(query)!=None:
            # Redirects to specified entry page if an exact match is found
            return HttpResponseRedirect(reverse('wiki:entry', kwargs={'title':query}))
        else:
            matches=[]

            # Selecting entry titles containing query as a substring
            for entry in util.list_entries():
                if query.lower() in str(entry.lower()):
                    matches.append(entry)

            if matches!=None:
                return render(request, "encyclopedia/results.html",{
                    "matches": matches,
                    "searchbar": QueryForm()
                    })
            else:
                return render(request, "encyclopedia/results.html",{
                    "message": "No results.",
                    "searchbar": QueryForm()
                    })

    else:
        return render(request, "encyclopedia/error.html",{
            "message": "Invalid query.",
            "searchbar": QueryForm()
        })

def entry(request, title):
    """Renders page that displays entry content."""

    # Displays error page if entry doesn't exist
    if util.get_entry(title)==None:
        return render(request, "encyclopedia/error.html",{
            "message": "The requested page was not found.",
            "searchbar": QueryForm()
        })

    # Converts markdown content to HTML
    entrycontent = markdowner.convert(util.get_entry(title))

    # Displays page with specified entry's contents
    return render(request, "encyclopedia/entry.html",{
        "title":title.capitalize(),
        "entrycontent": entrycontent,
        "searchbar": QueryForm()
    })

def create(request):
    """Allows user to create their own encyclopedia entry."""

    already_exists=False

    # Attempts to save new entry content inputted by user
    if request.method=="POST":

        # Extracting query data
        form = newEntryForm(request.POST)

        if form.is_valid():

            # Compares inputted title with existing entry titles
            for entry in util.list_entries():
                # Displays warning message if entry already exists
                if form.cleaned_data["newtitle"].lower() == entry.lower():
                    already_exists = True

            # Saves form contents as a new entry
            if already_exists == False:
                title = form.cleaned_data["newtitle"]
                content = form.cleaned_data["newcontent"]
                util.save_entry(title,content)
                return HttpResponseRedirect(reverse('wiki:entry', kwargs={'title':title}))
        else:
            return render(request, "encyclopedia/error.html",{
                "message": "Invalid inputs.",
                "searchbar": QueryForm()
            })

    return render(request, "encyclopedia/create.html",{
        "searchbar": QueryForm(),
        "form": newEntryForm(),
        "already_exists":already_exists
    })

def edit(request, title):
    """Allows user to edit existing entries."""

    # To pre-populate the editting text area with existing page content
    existing_content = util.get_entry(title)

    # When user tries to save their edits
    if request.method=="POST":

        # Extracting query data
        form = editForm(request.POST)

        if form.is_valid():

            # Replaces old entry with newly editted entry
            util.save_entry(title,form.cleaned_data["editbox"])
            return HttpResponseRedirect(reverse('wiki:entry', kwargs={'title':title}))

        else:
            return render(request, "encyclopedia/error.html",{
                "message": "Invalid inputs.",
                "searchbar": QueryForm()
            })

    return render(request, "encyclopedia/edit.html",{
        "searchbar": QueryForm(),
        "form": editForm(initial={'editbox':existing_content}),
        "title":title
    })

def randompg(request):
    """Redirects user to a random entry."""

    # Select a random item from list of entries
    list = util.list_entries()
    title = random.choice(list) # from Python's random module

    return HttpResponseRedirect(reverse('wiki:entry', kwargs={'title':title}))
