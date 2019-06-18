#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import jinja2
import os
import webapp2
import logging
from google.appengine.api import users
from google.appengine.ext import ndb
import datetime
import json
import unicodedata


jinja_environment = jinja2.Environment(loader=
    jinja2.FileSystemLoader(os.path.dirname(__file__)))

"""
-------------------------------------------------------------------------
Establishing the two classes, CheckList and Item
-------------------------------------------------------------------------
"""

class CheckList(ndb.Model):  # Sets up CheckList class
    title = ndb.StringProperty()
    owner = ndb.UserProperty()
    created = ndb.DateTimeProperty()
    copied = ndb.BooleanProperty()

class Item(ndb.Model): # Sets up Item class
    content = ndb.StringProperty()
    completion_status = ndb.BooleanProperty()
    created = ndb.DateTimeProperty()
    list_key = ndb.KeyProperty(CheckList)

"""
-------------------------------------------------------------------------
Login Handler, using the Google API
-------------------------------------------------------------------------
"""

class MainHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            nickname = user.nickname()
            logout_url = users.create_logout_url('/')
            greeting = 'Welcome, {}! (<a href="{}">sign out</a>) <br>'.format(
                nickname, logout_url) # Passes through one block for greeting
            open_checklist = '<a href="/mylists"> Create a checklist </a>' # A second block for the create a checklist button
            template_checklist = '<a href="/templatechecklists"> Check out some example checklists </a>'
            spotify = '<a href="/spotify"> Check out some playlists </a>'
            notes = '<a href="/notes"> Write down your thoughts </a>'
            template = jinja_environment.get_template('templates/main.html')
            template_vars = {"greeting": greeting, "open_checklist": open_checklist, "template_checklist": template_checklist, "spotify": spotify, "notes": notes}
            self.response.write(template.render(template_vars))
        else:
            login_url = users.create_login_url('/')
            greeting = '<a href="{}">Sign in</a>'.format(login_url)
            template_vars = {"greeting": greeting}
            template = jinja_environment.get_template('templates/main.html')
            self.response.write(template.render(template_vars))

"""
-------------------------------------------------------------------------
Page Handlers (rendering templates using jinja)
-------------------------------------------------------------------------
"""

class MyListsHandler(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template('templates/mylists.html')
        self.response.write(template.render())

class CheckListHandler(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template('templates/checklist.html')
        url_safe_id = str(self.request.get('id'))
        my_key = ndb.Key(urlsafe = url_safe_id)
        title = my_key.get().title
        key = self.request.get('id')
        template_vars = {"title": title, "id": key}
        self.response.write(template.render(template_vars))

class TemplateCheckListHandler(webapp2.RequestHandler):
    def get(self):
        # print 'running'
        dorm_url = str(makeDormEssentialsTemplateChecklist())
        snacks_url = str(makeSnacksTemplateChecklist())
        supplies_url = str(makeSuppliesTemplateChecklist())
        template_vars = {"dorm_essentials_url": dorm_url, "snacks_url" : snacks_url, "supplies_url": supplies_url}
        template = jinja_environment.get_template('templates/templatechecklist.html')
        self.response.write(template.render(template_vars))

# Note to self: will return if the stretch doesn't work. These are all for the Template Check List Page.

# class DormEssentialsHandler(webapp2.RequestHandler):
#     def get(self):
#         template = jinja_environment.get_template('templates/dormessentials.html')
#         self.response.write(template.render())
#
# class SchoolSuppliesHandler(webapp2.RequestHandler):
#     def get(self):
#         template = jinja_environment.get_template('templates/schoolsupplies.html')
#         self.response.write(template.render())
#
# class SnacksHandler(webapp2.RequestHandler):
#     def get(self):
#         template = jinja_environment.get_template('templates/snacks.html')
#         self.response.write(template.render())

class SpotifyHandler(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template('templates/spotify.html')
        self.response.write(template.render())

class NotesHandler(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template('templates/notes.html')
        self.response.write(template.render())
"""
-------------------------------------------------------------------------
Saving Lists and Items handlers
-------------------------------------------------------------------------
"""

#  Saves the checklist into the database
class SaveCheckListHandler(webapp2.RequestHandler):
    def post(self):
        input = json.loads(self.request.body.decode("utf-8"))
        user = users.get_current_user()
        my_list = CheckList(title = input['name'], created = datetime.datetime.now(), owner = user, copied = False) # Creates instance
        key = my_list.put() # Saves to database
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.dumps(key.urlsafe())) # Returns url safe key to front end

#  Saves the item into the database
class SaveItemHandler(webapp2.RequestHandler):
    def post(self):
        input = json.loads(self.request.body.decode("utf-8")) # Loads from front end
        my_key = ndb.Key(urlsafe = input['id'])
        my_item = Item(content = input['name'], completion_status = False, list_key = my_key, created = datetime.datetime.now()) #Returns you want to change back from url safe to regular)
        key = my_item.put()
        items = Item.query().fetch() # Gets all the items
        # Turns back into JSON object to display
        itemList = []
        for i in items:
            item = {}
            item['name'] = i.content # Finds the item from the database that matches the content
            itemList.append(item)
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.dumps(itemList))

"""
-------------------------------------------------------------------------
Returning List Handler
-------------------------------------------------------------------------
"""

# Return list everytime you open the page-- separate from save item
class ReturnListHandler(webapp2.RequestHandler):
    def get(self):
        url_safe_id = str(self.request.get('id')) # How to get it from top
        my_key = ndb.Key(urlsafe = url_safe_id)
        items = Item.query(Item.list_key == my_key).fetch() # want to query by list_key =
        itemList = []
        for i in items:
            item = {}
            item['name'] = i.content
            itemList.append(item)
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.dumps(itemList))

# Returns a list of the titles
class ReturnTitlesHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        lists = CheckList.query(CheckList.owner == user).fetch()
        titlesList = []
        for i in lists:
            title = {}
            title['name'] = i.title
            title['key'] = i.key.urlsafe() # Gives the key out
            titlesList.append(title)
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.dumps(titlesList))

"""
-------------------------------------------------------------------------
Deleting Item and List Handlers
-------------------------------------------------------------------------
"""
# Deletes the item from the database
class DeleteItemHandler(webapp2.RequestHandler):
    def post(self):
        content = self.request.get('itemText')
        items = Item.query(Item.content == content).fetch() # filter by content key
        my_item = items[0]
        my_item.key.delete()

# Deletes the list from the database
class DeleteListHandler(webapp2.RequestHandler):
    def post(self):
        title = self.request.get('listTitle')
        # Deletes checklist item
        listitles = CheckList.query(CheckList.title == title).fetch() # filter by content key
        my_list_title = listitles[0]
        my_list_title.key.delete()
        # Deletes items associated with checklist
        items = Item.query(Item.list_key == my_list_title.key).fetch() # filter by content key
        for my_item in items:
            my_item.key.delete()

"""
-------------------------------------------------------------------------
Stretch
-------------------------------------------------------------------------
"""
class VerifyEditorHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user() # Gets current user
        # Gets user who owns the checklist
        url_safe_id = str(self.request.get('id'))
        my_key = ndb.Key(urlsafe = url_safe_id)
        current_user = my_key.get().owner
        # Checks to see if they are the same user
        if user == current_user:
            print "access allowed, allow edits" # We want to send in the normal javascript
            editable = True
            # want to render with the general javascript
        else:
            print "access not allowed, show copy" # We don't want to seend in the javascript (except the return function with some features disabled)
            editable = False
            # when rendering we only want to link to the return function
        self.response.write(editable)

class CopyListHandler(webapp2.RequestHandler):
    def get(self):
        logging.info ("Hello")
        url_safe_id = str(self.request.get('id'))
        my_list_key = ndb.Key(urlsafe = url_safe_id)
        user = users.get_current_user() # Set as the new owner
        # my_list_key.get().title gets the title from the checklist it is copying
        my_copied_list = CheckList(title = my_list_key.get().title , created = datetime.datetime.now(), owner = user, copied = True) # Creates instance
        new_key = my_copied_list.put() # Saves to database
        # Search through items in the old list and add to the new list
        items = Item.query(Item.list_key == my_list_key).fetch() # want to query by list_key =
        for i in items:
            my_copied_item = Item(content = i.content, completion_status = False, list_key = new_key, created = datetime.datetime.now()) #Returns you want to change back from url safe to regular)
            key = my_copied_item.put()
        # Turn back into JSON object
        items = Item.query(Item.list_key == new_key).fetch()
        itemList = []
        for i in items:
            item = {}
            item['name'] = i.content # Finds the item from the database that matches the content
            itemList.append(item)
        # New URL Safe id
        url_string = new_key.urlsafe()
        self.response.write(url_string)

class CopyableAttributeHandler(webapp2.RequestHandler):
    def get(self):
        url_safe_id = str(self.request.get('id'))
        my_list_key = ndb.Key(urlsafe = url_safe_id)
        copyable = my_list_key.get().copied
        self.response.write(copyable)

# Here I want to run through the list and copy it but assign it to a new list key
class ChangeTitleHandler(webapp2.RequestHandler):
    def post(self):
        input = json.loads(self.request.body.decode("utf-8")) # Loads from front end
        url_safe_id = str(input['id'])
        my_list_key = ndb.Key(urlsafe = url_safe_id)
        copyable = my_list_key.get().copied
        new_title = str(input['new_title'])
        my_list_key.get().title = new_title
        my_list_key.get().put()
        self.response.write(copyable)
# Make a global scope variable that holds the keys for the handler when it randers

def makeDormEssentialsTemplateChecklist():
    user = users.User("demo@example.com")
    dorm_essentials = CheckList(title = "Dorm Essentials", created = datetime.datetime.now(), owner = user, copied = False)
    dorm_essentials_key = dorm_essentials.put()
    print dorm_essentials_key.urlsafe() # need to return url safe key and stream into
    dorm_essentials_item_1 = Item(content = "Bedding", completion_status = False, list_key = dorm_essentials_key, created = datetime.datetime.now())
    dorm_essentials_item_2 = Item(content = "Desk Lamp", completion_status = False, list_key = dorm_essentials_key, created = datetime.datetime.now())
    dorm_essentials_item_3 = Item(content = "Hangers", completion_status = False, list_key = dorm_essentials_key, created = datetime.datetime.now())
    dorm_essentials_item_4 = Item(content = "Toiletries", completion_status = False, list_key = dorm_essentials_key, created = datetime.datetime.now())
    list = [dorm_essentials_item_1, dorm_essentials_item_2, dorm_essentials_item_3, dorm_essentials_item_4]
    for i in list:
        i.put()
    base_url = "checklist?id="
    url = base_url + dorm_essentials_key.urlsafe()
    return(url)

def makeSnacksTemplateChecklist():
    user = users.User("demo@example.com")
    snacks = CheckList(title = "Snacks", created = datetime.datetime.now(), owner = user, copied = False)
    snacks_key = snacks.put()
    snacks_item_1 = Item(content = "Walnuts", completion_status = False, list_key = snacks_key, created = datetime.datetime.now())
    snacks_item_2 = Item(content = "Granola Bars", completion_status = False, list_key = snacks_key, created = datetime.datetime.now())
    snacks_item_3 = Item(content = "Apples", completion_status = False, list_key = snacks_key, created = datetime.datetime.now())
    snacks_item_4 = Item(content = "Oreos", completion_status = False, list_key = snacks_key, created = datetime.datetime.now())
    list = [snacks_item_1, snacks_item_2, snacks_item_3, snacks_item_4]
    for i in list:
        i.put()
    base_url = "checklist?id="
    url = base_url + snacks_key.urlsafe()
    return(url)

# TO DO FIGURE OUT HOW TO MAKE THE USER FOR THE DEMO TEMPLATES THE SAME

def makeSuppliesTemplateChecklist():
    user = users.User("demo@example.com")
    supplies = CheckList(title = "Supplies", created = datetime.datetime.now(), owner = user, copied = False)
    supplies_key = supplies.put()
    supplies_item_1 = Item(content = "Pens", completion_status = False, list_key = supplies_key, created = datetime.datetime.now())
    supplies_item_2 = Item(content = "Laptop", completion_status = False, list_key = supplies_key, created = datetime.datetime.now())
    supplies_item_3 = Item(content = "Notebooks", completion_status = False, list_key = supplies_key, created = datetime.datetime.now())
    supplies_item_4 = Item(content = "Planner", completion_status = False, list_key = supplies_key, created = datetime.datetime.now())
    list = [supplies_item_1, supplies_item_2, supplies_item_3, supplies_item_4]
    for i in list:
        i.put()
    base_url = "checklist?id="
    url = base_url + supplies_key.urlsafe()
    return(url)

app = webapp2.WSGIApplication([
    # Handlers for rendering
    ('/', MainHandler),
    ('/mylists', MyListsHandler),
    ('/checklist', CheckListHandler),
    ('/templatechecklists', TemplateCheckListHandler),
    ('/spotify', SpotifyHandler),
    ('/notes', NotesHandler),
    # Handlers called from Java Script
    ('/returnList', ReturnListHandler), # To return the items and lists from the database
    ('/returnTitles', ReturnTitlesHandler),
    ('/saveItem', SaveItemHandler), # To save item and lists
    ('/saveList', SaveCheckListHandler),
    ('/deleteItem', DeleteItemHandler), # To delete item and lists
    ('/deleteList', DeleteListHandler),
    ('/verifyEditor', VerifyEditorHandler),
    ('/copyList', CopyListHandler),
    ('/checkCopyableAttribute', CopyableAttributeHandler),
    ('/changeTitle', ChangeTitleHandler)
    # Note to self: will add back if the stretch doesn't work
    # ('/dormessentials', DormEssentialsHandler),
    # ('/schoolsupplies', SchoolSuppliesHandler),
    # ('/snacks', SnacksHandler),
], debug=True)
