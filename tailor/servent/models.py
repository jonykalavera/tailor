import simplejson
import urllib2

from django.db import models
from django.http import HttpResponse
from fabric.api import *

from tailor.servent.stich import Sew

class Project(models.Model):

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    
    tailor_api = models.CharField(max_length=255, blank=True, default='http://project/tailor/api/v1/schema/')
            
    def __unicode__(self):
        return str(self.name)
    
    def run_fab(self, _input):
        try:
            client_url = "%s?key=%s" % (self.tailor_api, _input['api_key'])
            client_data = urllib2.urlopen(client_url)
            client_json = client_data.read()
            client_dict = simplejson.loads(client_json)
            env.hosts = _input['hosts']
            
            sewing = Sew()
            sewing.setup()
            sewing.add_vars(client_dict['env'])
            sewing.add_methods(client_dict['dependencies'])
            sewing.add_methods(client_dict['tasks'])
            result, response_list = sewing.execute(_input['commands'])
            sewing.cleanup()
            if result:    
                response_dict = {'success':True, 'message':"Commands Executed", 'responses': response_list}
                print response_dict
                #from django.core import serializers
                response = simplejson.dumps(response_dict)
                return HttpResponse(response, mimetype='application/json', status=200)
            else:
                response_dict = {'success':False, 'message':"Coudn't not execute commands"}
                response = simplejson.dumps(response_dict)
                return HttpResponse(response, mimetype='application/json', status=400)
        except Exception, e:
            print "Error: %s" % e
            response_dict = {'success':False, 'message':"Coudn't not execute commands"}
            response = simplejson.dumps(response_dict)
            return HttpResponse(response, mimetype='application/json', status=400)