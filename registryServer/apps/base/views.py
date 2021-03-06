#-*- coding: utf-8 -*-

import httplib
import json
from django.shortcuts import render_to_response, HttpResponse, redirect
from django.template import RequestContext
from oauth2app.models import Client, AccessToken, AccessRange
from django.contrib.auth.decorators import login_required
from django import forms
from apps.account.models import Profile

class LocationForm(forms.Form):
    location = forms.CharField()

@login_required
def homepage(request):

    template = {}

    if request.user.is_authenticated():
	user_profile = None
	try:
	    user_profile = request.user.get_profile()
	except:
	    # On first login, a user will not have a profile...what to do?
	    new_profile = Profile()
	    new_profile.user = request.user
	
	    new_client = Client(name=request.user.username+"_pds", user=request.user, description="user "+request.user.username+"'s Personal Data Store", redirect_uri="http://"+new_profile.pds_ip+":"+new_profile.pds_port+"/?username="+request.user.username)
	    new_client.save()
	    new_profile.pds_client = new_client
	    new_profile.save()

	if request.GET.get('location'):
	    new_profile = request.user.get_profile()
	    new_location = request.GET['location'].split(":")

	    new_profile.pds_ip = new_location[0]
	    new_profile.pds_port = new_location[1]

        clients = Client.objects.filter(user=request.user)
        access_tokens = AccessToken.objects.filter(user=request.user).select_related()
#        funf_access_token = AccessToken.objects.get_or_create(user=request.user, scope="funf_write")
#        access_tokens = access_tokens.select_related()
	form = LocationForm()

        template["access_tokens"] = access_tokens
        template["clients"] = clients
        template["profile"] = user_profile
	template['form']=form
	template['isup']=is_pds_up(user_profile)

    return render_to_response(
        'base/homepage.html', 
        template, 
        RequestContext(request))


def is_pds_up(profile):
    '''Verifies that a user's PDS is set up and responding'''
#    pds_location = profile.pds_location

    try:
	path = str(profile.pds_ip)+":"+str(profile.pds_port)
	print path
        conn = httplib.HTTPConnection(path, timeout=2.5)
        request_path="/discovery/ping"
        conn.request("GET",str(request_path))
        r1 = conn.getresponse()
        response_text = r1.read()
	print response_text
        result = json.loads(response_text)

        if result['success'] != True:
             raise Exception(result['message'])
        conn.close()
        return True
    except Exception as ex:
        print ex
        return False



    

#TODO DELETE this section. testing mongoEngine
# handle static pages (such as the About pg, Terms pg, and Privacy policy pg)
from mongoengine import *
class Puser(Document):
    email = StringField(required=True)
    first_name = StringField(max_length=50)
    last_name = StringField(max_length=50)
def static(request):

  connect('project1')#, username='webapp', password='pwd123')
  john = Puser(email='jdoe@example.com', first_name='sfds', last_name='S')
  john.save()
  str = ''
  for p in Puser.objects:
    str += p.first_name + ' ' +p.last_name + '<br/>'
  return HttpResponse(str)

def returnToAndroidApp(request):
    response = HttpResponse(content="", status=302)
    response["Location"] = "my_android_application:///dcapsdev.media.mit.edu/returnToAndroidApp"
    return response#HttpResponseRedirect('mypds-android-app:///dcapsdev.media.mit.edu/returnToAndroidApp')
