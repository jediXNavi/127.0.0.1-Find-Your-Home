"""
SFU CMPT 756
Tenant service.
"""

# Standard library modules
import logging
import sys
import time

# Installed packages
from flask import Blueprint
from flask import Flask
from flask import request
from flask import Response

import jwt

from prometheus_flask_exporter import PrometheusMetrics

import requests

import simplejson as json

# The application

app = Flask(__name__)

metrics = PrometheusMetrics(app)
metrics.info('app_info', 'Tenant process')

bp = Blueprint('app', __name__)

services = {
    "property": "http://service-property:30002/api/v1/property",
    #"property": "http://host.docker.internal:30002/api/v1/property", #For Local testing
    # "property": "http://172.17.0.1:30002/api/v1/property", #For linux
    "endpoint": [
        "service_req",
        "service_req_update",
        "apply_property"
    ]
}

db = {
    "name": "http://teamadb:30000/api/v1/datastore", #For Online testing
    #"name": "http://host.docker.internal:30000/api/v1/datastore", #For Local Testing
    # "name": "http://172.17.0.1:30000/api/v1/datastore", #For linux
    "endpoint": [
        "read",
        "write",
        "delete",
        "update"
    ]
}


@bp.route('/', methods=['GET'])
@metrics.do_not_track()
def hello_world():
    return ("If you are reading this in a browser, your service is "
            "operational. Switch to curl/Postman/etc to interact using the "
            "other HTTP verbs.")


@bp.route('/health')
@metrics.do_not_track()
def health():
    return Response("", status=200, mimetype="application/json")


@bp.route('/readiness')
@metrics.do_not_track()
def readiness():
    return Response("", status=200, mimetype="application/json")


@bp.route('/<user_id>', methods=['PUT'])
def update_tenant(user_id):
    headers = request.headers
    # check header here
    if 'Authorization' not in headers:
        return Response(json.dumps({"error": "missing auth"}), status=401,
                        mimetype='application/json')
    try:
        content = request.get_json()
        email = content['email']
        fname = content['fname']
        lname = content['lname']
        password = content['password']
        contact = content['contact']
    except Exception:
        return json.dumps({"message": "error reading arguments"})
    url = db['name'] + '/' + db['endpoint'][3]
    response = requests.put(
        url,
        params={"objtype": "user_details", "objkey": user_id},
        json={"email": email, "fname": fname, "lname": lname ,"password": password, "contact" : contact})
    return (response.json())


@bp.route('/', methods=['POST'])
def create_tenant():
    """
    Creating a new tenant account that starts with username t_<username>. .
    """
    try:
        content = request.get_json()
        username = content['username']
        password = content['password']
        fname = content['fname']
        lname = content['lname']
        email = content['email']
        contact = content['contact']
    except Exception:
        return Response(json.dumps({"error": "All tenant arguments not passed"}), status=400,
                        mimetype='application/json')
    url = db['name'] + '/' + db['endpoint'][1]
    response = requests.post(
        url,
        json={"objtype": "user_details",
              "username": 'T_'+ username,
              "lname": lname,
              "email": email,
              "fname": fname,
              "password": password,
              "contact": contact})
    #return (response.json())
    return Response(response.json(),status=200,
                        mimetype='application/json')



@bp.route('/service_req', methods=['POST'])
def create_servicereq():
    """
    Create a Service Request by Tenant.
    """
    headers = request.headers
    # check header here
    if 'user_id' not in headers:
        return Response(json.dumps({"error": "missing auth"}), status=401,
                        mimetype='application/json')

    else:
        user_id = headers['user_id']
        if user_id.startswith('T_'):
            try:

                content = request.get_json()
                property_id = content['property_id']
                query = content['query']

            except Exception:
                return json.dumps({"message": "error reading arguments"})

            url = services['property'] + '/' + services['endpoint'][0]

            response = requests.post(
                url,
                json={"objtype": "service_requests",
                    "property_id": property_id,
                    "user_id": user_id,
                    "query": query,
                    })

            return (response.json())
        else:
            return Response(json.dumps({"error": "Only Tenant can create a service request"}), status=401,
                        mimetype='application/json')

@bp.route('/service_req_update/<query_id>', methods=['PUT'])
def update_servicereq(query_id):
    """
    Update a Service Request by Tenant.
    """
    headers = request.headers
    # check header here
    if 'user_id' not in headers:
        return Response(json.dumps({"error": "missing auth"}), status=401,
                        mimetype='application/json')

    else:
        user_id = headers['user_id']
        if user_id.startswith('T_'):
            try:

                content = request.get_json()
                property_id = content['property_id']
                query = content['query']

            except Exception:
                return json.dumps({"message": "error reading arguments"})
            url = services['property'] + '/' + services['endpoint'][1]
            response = requests.put(
                url,
                json={
                    "property_id": property_id,
                    "user_id": user_id,
                    "query_id": query_id,
                    "query": query,
                    })
            return (response.json())
        else:
            return Response(json.dumps({"error": "Only Tenant can update a service request"}), status=401,
                        mimetype='application/json')


@bp.route('/<user_id>', methods=['DELETE'])
def delete_tenant(user_id):
    headers = request.headers
    # check header here
    if 'Authorization' not in headers:
        return Response(json.dumps({"error": "User has not provided authorization token, user is not logged in!"}),
                        status=401,
                        mimetype='application/json')
    # Check if user_id is for landlord
    if user_id.startswith('T_'):
        # Delete landlord from user_details table
        url = db['name'] + '/' + db['endpoint'][2]
        response = requests.delete(url,
                               params={"objtype": "user_details", "objkey": user_id})
    else:
        return Response(json.dumps({"error": "Not a tenant user_id"}), status=403,
                                    mimetype='application/json')
    return Response(json.dumps(response.json()), status=response.status_code,
                                    mimetype='application/json')

@bp.route('/apply/<user_id>', methods=['PUT'])
def apply_property(user_id):
    """
    Tenant applies for available property.
    """
    headers = request.headers
    # check header here
    if 'Authorization' not in headers:
        return Response(json.dumps({"error": "missing auth"}),
                        status=400,
                        mimetype='application/json')
    else:
        # Check if user applying for property is a tenant
        if user_id.startswith('T_'):
            try:
                # Read property ID from request body
                content = request.get_json()
                property_id = content['prop_id']
            except Exception:
                return Response(json.dumps({"message": "error reading arguments"}), status=400,
                        mimetype='application/json')
            try:
                # Check if tenant already has a property
                url = db['name'] + '/' + db['endpoint'][0]
                response = requests.get(url, params={"objtype": "user_details", "type": "read_user", "objkey": user_id})
                response_items = list(response.json()['Items'][0])

                try:
                    # Only apply for property if tenant doesn't already have a property
                    if 'properties' not in response_items:
                        # Call property service
                        url = services['property'] + '/' + services['endpoint'][2]
                        response2 = requests.post(url,
                                                json={"property_id": property_id,
                                                      "user_id": user_id})
                        return Response(json.dumps(response2.json()), status=response2.status_code,
                                                    mimetype='application/json')

                    else:
                        return Response(json.dumps({"error": "Tenant already has a property, remove current property before applying for new one."}), status=403,
                                mimetype='application/json')
                except Exception:
                    return Response(json.dumps({"error": "Some error occured"}), status=400,
                            mimetype='application/json')
            except Exception:
                return Response(json.dumps({"error": "User ID not found, recheck and try again"}), status=404,
                        mimetype='application/json')
        else:
            return Response(json.dumps({"error": "Only Tenant can apply for property."}), status=403,
                        mimetype='application/json')


@bp.route('/<user_id>', methods=['GET'])
def get_user(user_id):
    headers = request.headers
    # check header here
    if 'Authorization' not in headers:
        return Response(
            json.dumps({"error": "missing auth"}),
            status=401,
            mimetype='application/json')
    payload = {"objtype":"user_details","type":"read_user","objkey":user_id}
    url = db['name'] + '/' + db['endpoint'][0]
    response = requests.get(url, params=payload)
    return (response.json())



@bp.route('/login', methods=['PUT'])
def login():
    try:
        content = request.get_json()
        username = 'T_' + content['username']
        password = content['password']
    except Exception:
        return json.dumps({"message": "error reading parameters"})
    url = db['name'] + '/' + db['endpoint'][0]
    response = requests.get(url, params={"objtype": "user_details", "type": "login", "objkey": username, "passkey": password})

    if response.status_code == 200:
        data = response.json()
        if data['password']==password:
            encoded = jwt.encode({'user_id': username,'time': time.time()},'secret',algorithm='HS256')
        else:
            return json.dumps({"message": "Username/Password Incorrect!!!"})
        return encoded
    else:
        return json.dumps({"message": "Login unsuccessful! Check username and password."})

@bp.route('/logoff', methods=['PUT'])
def logoff():
    try:
        headers = request.headers
        _ = headers['jwt']
    except Exception:
        return json.dumps({"message": "error reading parameters"})

    return json.dumps({"message": "Successfully logged out."})


# All database calls will have this prefix.  Prometheus metric
# calls will not---they will have route '/metrics'.  This is
# the conventional organization.
app.register_blueprint(bp, url_prefix='/api/v1/tenant/')

if __name__ == '__main__':
    if len(sys.argv) < 2:
        logging.error("Usage: app.py <service-port>")
        sys.exit(-1)

    p = int(sys.argv[1])
    # Do not set debug=True---that will disable the Prometheus metrics
    app.run(host='0.0.0.0', port=p, threaded=True)
