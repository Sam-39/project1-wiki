from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django import forms
from . import util
from markdown2 import markdown
import random


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

# ENTRY PAGE.
def entry(request, title):
    my_entry = util.get_entry(title)
    if my_entry != None:
        page = markdown(my_entry)
        return render(request, "encyclopedia/entry.html", {
            "title": title,
            "entry": page
        })
    return render(request, "encyclopedia/error.html", {
        "alert": "The requested page was not found."
    })

# SEARCH PAGE.
def search(request):
    query = request.GET.get('q')
    if util.get_entry(query) != None:
        return HttpResponseRedirect(reverse("entry", args=[query]))
    else:
        related_searches = []
        entries = util.list_entries()
        for entry in entries:
            if query.lower() in entry.lower():
                related_searches.append(entry)

    return render(request, "encyclopedia/search.html", {
        "related": related_searches,
        "query": query
    })

# CREAT NEW PAGE.
class NewPage(forms.Form):
    title = forms.CharField(label="", widget=forms.TextInput(attrs={"placeholder": "Page title"}))
    content = forms.CharField(label="", widget=forms.Textarea(attrs={"placeholder": "Page content"}))

def create(request):
    if request.method == "POST":
        data = NewPage(request.POST)
        if data.is_valid():
            title = data.cleaned_data["title"]
            content = data.cleaned_data["content"]
            if util.get_entry(title) != None:
                return render(request, "encyclopedia/error.html", {
                    "alert": "Page already exist."
                })
            else:
                util.save_entry(title, content)
                return HttpResponseRedirect(reverse("entry", args=[title]))

    return render(request, "encyclopedia/create.html", {'create_form':NewPage()})

# EDIT PAGE.
class EditPage(forms.Form):
    content = forms.CharField(widget=forms.Textarea(), label="")

def edit(request, title):

    if request.method == "POST":
        data = EditPage(request.POST) 
        if data.is_valid():
            content = data.cleaned_data["content"]
            util.save_entry(title, content)
            page_md = util.get_entry(title)
            new_page = markdown(page_md)

            return render(request, "encyclopedia/entry.html", {
                'entry': new_page,
                'title': title
            })
    
    if request.method == "GET":
        entry = util.get_entry(title)
        if entry == None:
            return render(request, "encyclopedia/error.html", {
                "alert": "Can't Edit: Page does not exist"
            })
    
    return render(request, "encyclopedia/edit.html", {
        'edit_form': EditPage(initial={'content': entry}),
        'title': title
    })

# RANDOM PAGE.
def random_page(request):
    entries = util.list_entries()
    random_page = random.choice(entries)

    return HttpResponseRedirect(reverse("entry", args=[random_page]))
