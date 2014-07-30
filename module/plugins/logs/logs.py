#!/usr/bin/python

# -*- coding: utf-8 -*-

# Copyright (C) 2009-2014:
#    Gabes Jean, naparuba@gmail.com
#    Gerhard Lausser, Gerhard.Lausser@consol.de
#    Gregory Starck, g.starck@gmail.com
#    Hartmut Goebel, h.goebel@goebel-consult.de
#
# This file is part of Shinken.
#
# Shinken is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Shinken is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Shinken.  If not, see <http://www.gnu.org/licenses/>.

import time

from shinken.log import logger

# Mongodb lib
try:
    import pymongo
    from pymongo.connection import Connection
    import gridfs
except ImportError:
    Connection = None


### Will be populated by the UI with it's own value
app = None

# Get plugin's parameters from configuration file
params = {}
params['mongo_host'] = "localhost"
params['mongo_port'] = 27017
params['db_name'] = "Logs"
params['logs_limit'] = 500
params['logs_type'] = []
params['logs_hosts'] = []
params['logs_services'] = []

def load_cfg():
    global params
    
    import os,sys
    from config_parser import config_parser
    plugin_name = os.path.splitext(os.path.basename(__file__))[0]
    try:
        currentdir = os.path.dirname(os.path.realpath(__file__))
        configuration_file = "%s/%s" % (currentdir, 'plugin.cfg')
        logger.debug("Plugin configuration file: %s", configuration_file)
        scp = config_parser('#', '=')
        params = scp.parse_config(configuration_file)

        # mongo_host = params['mongo_host']
        params['mongo_port'] = int(params['mongo_port'])
        params['logs_limit'] = int(params['logs_limit'])
        params['logs_type'] = [item.strip() for item in params['logs_type'].split(',')]
        params['logs_hosts'] = [item.strip() for item in params['logs_hosts'].split(',')]
        params['logs_services'] = [item.strip() for item in params['logs_services'].split(',')]
        
        logger.debug("WebUI plugin '%s', configuration loaded." % (plugin_name))
        logger.debug("Plugin %s configuration, database: %s (%s)", plugin_name, params['mongo_host'], params['mongo_port'])
        logger.debug("Plugin %s configuration, fetching: %d %s", plugin_name, params['logs_limit'], params['logs_type'])
        logger.debug("Plugin %s configuration, hosts: %s", plugin_name, params['logs_hosts'])
        logger.debug("Plugin %s configuration, services: %s", plugin_name, params['logs_services'])
        return True
    except Exception, exp:
        logger.warning("WebUI plugin '%s', configuration file (%s) not available: %s", plugin_name, configuration_file, str(exp))
        return False


def reload_cfg():
    load_cfg()
    app.bottle.redirect("/config")


def checkauth():
    user = app.get_user_auth()

    if not user:
        app.bottle.redirect("/user/login")
    else:
        return user


def getdb(dbname):
    con = None
    db = None

    try:
        con = Connection(params['mongo_host'],int(params['mongo_port']))
    except:
        return (  
            "Error : Unable to create mongo DB connection %s:%s" % (params['mongo_host'],params['mongo_port']),
            None
        )

    try:
        db = con[dbname]
    except:
        return (  
            "Error : Unable to connect to mongo database %s" % dbname,
            None
        )

    return (  
        "Connected to mongo database '%s'" % dbname,
        db
    )


def show_logs():
    user = checkauth()    

    message,db = getdb(params['db_name'])
    if not db:
        return {
            'app': app,
            'user': user, 
            'message': message,
            'params': params,
            'records': []
        }

    records=[]

    try:
        logger.info("[Logs] Fetching records from database: %s / %s / %s (max %d)" % (params['logs_type'], params['logs_hosts'], params['logs_services'], params['logs_limit']))

        logs_limit = params['logs_limit']
        logs_type = params['logs_type']
        logs_hosts = params['logs_hosts']
        logs_services = params['logs_services']

        query = []
        if len(logs_type) > 0 and logs_type[0] != '':
            query.append({ "type" : { "$in": logs_type }})
        if len(logs_hosts) > 0 and logs_hosts[0] != '':
            query.append({ "host_name" : { "$in": logs_hosts }})
        if len(logs_services) > 0 and logs_services[0] != '':
            query.append({ "service_description" : { "$in": logs_services }})
            
        records=[]
        if len(query) > 0:
            for log in db.logs.find({'$and': query}).sort("time",-1).limit(logs_limit):
                records.append({
                    "date" : int(log["time"]),
                    "host" : log['host_name'],
                    "service" : log['service_description'],
                    "message" : log['message']
                })
        else:
            for log in db.logs.find().sort("time",-1).limit(logs_limit):
                records.append({
                    "date" : int(log["time"]),
                    "host" : log['host_name'],
                    "service" : log['service_description'],
                    "message" : log['message']
                })
        message = "%d records fetched from database." % len(records)
        logger.info("[Logs] %d records fetched from database.", len(records))
    except Exception, exp:
        logger.error("[Logs] Exception when querying database: %s", str(exp))

    return {
        'app': app,
        'user': user, 
        'message': message,
        'params': params,
        'records': records
    }


def form_hosts_list():
    user = checkauth()    

    return {'app': app, 'user': user, 'params': params}

def set_hosts_list():
    user = checkauth()    

    # Form cancel
    if app.request.forms.get('cancel'): 
        app.bottle.redirect("/logs")

    params['logs_hosts'] = []
    
    hostsList = app.request.forms.getall('hostsList[]')
    logger.debug("Selected hosts : ")
    for host in hostsList:
        logger.debug("- host : %s" % (host))
        params['logs_hosts'].append(host)

    app.bottle.redirect("/logs")
    return

def form_services_list():
    user = checkauth()    

    return {'app': app, 'user': user, 'params': params}

def set_services_list():
    user = checkauth()    

    # Form cancel
    if app.request.forms.get('cancel'): 
        app.bottle.redirect("/logs")

    params['logs_services'] = []
    
    servicesList = app.request.forms.getall('servicesList[]')
    logger.debug("Selected services : ")
    for service in servicesList:
        logger.debug("- service : %s" % (service))
        params['logs_services'].append(service)

    app.bottle.redirect("/logs")
    return

def form_logs_type_list():
    user = checkauth()    

    return {'app': app, 'user': user, 'params': params}

def set_logs_type_list():
    user = checkauth()    

    # Form cancel
    if app.request.forms.get('cancel'): 
        app.bottle.redirect("/logs")

    params['logs_type'] = []
    
    logs_typeList = app.request.forms.getall('logs_typeList[]')
    logger.debug("Selected logs types : ")
    for log_type in logs_typeList:
        logger.debug("- log type : %s" % (log_type))
        params['logs_type'].append(log_type)

    app.bottle.redirect("/logs")
    return

# Load plugin configuration parameters
load_cfg()

pages = {   
        reload_cfg: {'routes': ['/reload/logs']},

        show_logs: {'routes': ['/logs'], 'view': 'logs', 'static': True},
        
        form_hosts_list: {'routes': ['/logs/hosts_list'], 'view': 'form_hosts_list'},
        set_hosts_list: {'routes': ['/logs/set_hosts_list'], 'view': 'logs', 'method': 'POST'},
        form_services_list: {'routes': ['/logs/services_list'], 'view': 'form_services_list'},
        set_services_list: {'routes': ['/logs/set_services_list'], 'view': 'logs', 'method': 'POST'},
        form_logs_type_list: {'routes': ['/logs/logs_type_list'], 'view': 'form_logs_type_list'},
        set_logs_type_list: {'routes': ['/logs/set_logs_type_list'], 'view': 'logs', 'method': 'POST'},
}
