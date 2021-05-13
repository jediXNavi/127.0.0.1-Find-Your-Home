"""
SFU CMPT 756
Property service.
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
metrics.info('app_info', 'Property process')

bp = Blueprint('app', __name__)

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
def update_user(user_id):
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
    except Exception:
        return json.dumps({"message": "error reading arguments"})
    url = db['name'] + '/' + db['endpoint'][3]
    response = requests.put(
        url,
        params={"objtype": "user", "objkey": user_id},
        json={"email": email, "fname": fname, "lname": lname})
    return (response.json())

@bp.route('/create_property', methods=['POST'])
def create_property():
    #Context passed from Landlord to create property, add to city table and add to user_details table

    try:
        content = request.get_json()
        content['objtype'] = 'property'

        url = db['name'] + '/' + db['endpoint'][1]
        response = requests.post(
                url,
                json=content)

        if response.status_code == 200:

            prop_id = response.json()['property_id']
            city = content['city'].title()  # Use title to capatalize first letter of every word (for consistency)

            url = db['name'] + '/' + db['endpoint'][1]
            response_city = requests.post(
            url,
            json={"objtype": "city",
                "city_id": city,
                "prop_id": prop_id
                })
        else:
            return Response(json.dumps({"error":"An error occurreced processing this request"}), status=401,
                                    mimetype='application/json')

        if response.status_code == 200:
            #Get Property List for the user from user_details table, append current prop ID, then update table
            try:
                user_id = content['user_id']
                payload={"objtype": "user_details_property", "objkey": user_id}
                url = db['name'] + '/' + db['endpoint'][0]
                response_proplist = requests.get(url, params=payload)
                response_dict = response_proplist.json()

                if response_dict['property_details'] == 'Not Found':
                    #This means first property for user
                    url = db['name'] + '/' + db['endpoint'][3]
                    response2 = requests.put(
                        url,
                        params={"objtype": "user_details_property", "objkey": user_id},
                        json={"properties": [prop_id]})

                else:
                    #This means property already exist for the user
                    property_list = response_dict['property_details']
                    property_list.append(prop_id)
                    url = db['name'] + '/' + db['endpoint'][3]
                    response3 = requests.put(
                        url,
                        params={"objtype": "user_details_property", "objkey": user_id},
                        json={"properties": property_list})

            except Exception:
                return json.dumps({"message": "There was an error"})


        return (response.json())

    except Exception as e:
        return Response(json.dumps({"error":e}), status=401,
                                    mimetype='application/json')

@bp.route('/delete_property', methods=['POST'])
def delete_property():
    try:
        content = request.get_json()
        objtype = content['objtype']
        objkey = content['objkey']
        property_id = content['prop']


        # Update user details
        url = db['name'] + '/' + db['endpoint'][3]
        response = requests.put(url,
                                params={"objtype": objtype, "objkey": objkey},
                                json={"prop": property_id})

        # Delete property from property table
        if response.status_code == 200:
            url = db['name'] + '/' + db['endpoint'][2]
            response = requests.delete(url, params={"objtype": "property", "objkey": property_id})
        else:
            return Response(json.dumps({"error1": "selected property does not belong to landlord OR",
                                        "error2": "landlord username/password is incorrect!"}),
                            status=401, mimetype='application/json')

    except Exception as e:
        return Response(json.dumps({"error":e}), status=401,
                        mimetype='application/json')

    return (response.json())

@bp.route('/<property_id>', methods=['GET'])
def get_property_details(property_id):
    """
    Get the details of a property.
    """
    headers = request.headers
    if 'Authorization' not in headers:
        return Response(json.dumps({"error": "missing auth"}),
                        status=401,
                        mimetype='application/json')

    try:
        payload={"objtype": "property", "objkey": property_id}
        url = db['name'] + '/' + db['endpoint'][0]
        response = requests.get(url, params=payload)
        return (response.json())

    except Exception:
        return json.dumps({"message": "Check the property ID and try again"})

@bp.route('/service_req', methods=['POST'])
def create_servicereq():
    """
    Create a Service Request by Tenant.
    """

    try:

        content = request.get_json()
        property_id = content['property_id']
        user_id = content['user_id']
        query = content['query']
        url = db['name'] + '/' + db['endpoint'][1]
        response = requests.post(
        url,
        json={"objtype": "service_requests",
            "property_id": property_id,
            "user_id": user_id,
            "query": query,
            "resolved": False
            })

        return (response.json())

    except Exception:
        return json.dumps({"message": "error reading arguments"})


@bp.route('/service_req', methods=['GET'])
def get_servicereq():
    """
    Get the status of service request.
    """
    try:
        content = request.get_json()
        user_id = content['user_id']

        payload={"objtype": "service_requests", "objkey": user_id}
        url = db['name'] + '/' + db['endpoint'][0]
        response = requests.get(url, params=payload)
        return (response.json())

    except Exception:
        return json.dumps({"message": "Check the user ID and try again"})


@bp.route('/service_req_update', methods=['PUT'])
def update_servicereq():
    """
    Update a Service Request by Tenant.
    """
    try:

        content = request.get_json()

        property_id = content['property_id']
        user_id = content['user_id']
        query = content['query']
        query_id = content['query_id']

    except Exception:
        return json.dumps({"message": "error reading arguments"})

    url = db['name'] + '/' + db['endpoint'][1]
    response = requests.post(
        url,
        json={"objtype": "service_requests",
            "property_id": property_id,
            "user_id": user_id,
            "query_id": query_id,
            "query": query,
            "resolved": False
            })

    return (response.json())


@bp.route('/resolve_req', methods=['PUT'])
def resolve_servicereq():
    """
    Resolve a Service Request by Landlord.
    """

    try:

        content = request.get_json()
        property_id = content['property_id']
        tenant_id = content['tenant_id']
        user_id = content['user_id']
        query_id = content['query_id']
        resolution = content['resolution']
        res = content['resolved']

    except Exception:
        return json.dumps({"message": "error reading arguments"})

    url = db['name'] + '/' + db['endpoint'][1]

    response = requests.post(
    url,
    json={"objtype": "service_requests",
        "property_id": property_id,
        "tenant_id" : tenant_id,
        "user_id": user_id,
        "query_id": query_id,
        "resolution": resolution,
        "resolved": res
        })

    return (response.json())

@bp.route('/user_prop/<user_id>', methods=['GET'])
def view_user_property(user_id):
    """
    View user's properties.
    """
    headers = request.headers
    if 'Authorization' not in headers:
        return Response(json.dumps({"error": "missing auth"}),
                        status=400,
                        mimetype='application/json')

    try:
        # Check if user exists
        url = db['name'] + '/' + db['endpoint'][0]
        response = requests.get(url, params={"objtype": "user_details", "type": "read_user", "objkey": user_id})
        response_items = list(response.json()['Items'][0])

        # Get properties for the user
        payload={"objtype": "user_details_property", "objkey": user_id}
        url = db['name'] + '/' + db['endpoint'][0]
        response = requests.get(url, params=payload)
        return Response(json.dumps(response.json()), status=response.status_code,
                                    mimetype='application/json')

    except Exception:
        return Response(json.dumps({"error": "User ID not found, recheck and try again"}), status=404,
                mimetype='application/json')

@bp.route('list_prop/<city_id>', methods=['GET'])
def list_properties(city_id):
    """
    Get list of properties in a city.
    """
    headers = request.headers
    if 'Authorization' not in headers:
        return Response(json.dumps({"error": "missing auth"}),
                        status=400,
                        mimetype='application/json')

    try:
        payload={"objtype": "city", "objkey": city_id.title()}  # Use title to capatalize first letter of every word (for consistency)
        url = db['name'] + '/' + db['endpoint'][0]
        response = requests.get(url, params=payload)
        return Response(json.dumps(response.json()), status=response.status_code,
                                    mimetype='application/json')

    except Exception:
        return Response(json.dumps({"error": "Check the city ID and try again"}), status=404,
                mimetype='application/json')
    
@bp.route('/apply_property', methods=['POST'])
def apply_property():
    try:
        content = request.get_json()
        property_id = content['property_id']
        user_id = content['user_id']
    except Exception:
        return Response(json.dumps({"error": "error reading arguments"}), status=400,
                            mimetype='application/json') 

    # Check if property is available
    try:
        payload={"objtype": "property", "objkey": property_id}
        url = db['name'] + '/' + db['endpoint'][0]
        response = requests.get(url, params=payload)
        response_dict = response.json() 

        # Returns errors like property not found 
        if response_dict['status_code'] == 200:
            property_details = response_dict['property_details']
        else:
            return Response(json.dumps({"error":response_dict['message']}), status=400,
                            mimetype='application/json')

        # Successfully allocate property if it is available
        if (property_details['availability'] == True) or (str(property_details['availability']).lower() == "true"):
            url = db['name'] + '/' + db['endpoint'][3]
            response2 = requests.put(url,
                                    params={"objtype": "user_details_property", "objkey": user_id},
                                    json={"properties": [property_id]})
        else:
        # Throw error if property unavailable
            return Response(json.dumps({"error": "Property not available."}), status=403,
                mimetype='application/json') 

        # Change property availability flag to False if property successfully allocated
        if response2.status_code == 200:
            url = db['name'] + '/' + db['endpoint'][3]
            response3 = requests.put(url,
                                    params={"objtype": "property", "objkey": property_id},
                                    json={"availability": False})
            if response3.status_code == 200:
                return Response(json.dumps(response2.json()), status=response2.status_code,
                            mimetype='application/json')
            else:
                return Response(json.dumps(response3.json()), status=response3.status_code,
                            mimetype='application/json')
        else:
            return Response(json.dumps({"error": "Problem allocating property to tenant"}), status=400,
                mimetype='application/json')
    except Exception:
        return Response(json.dumps({"error": "Some problem occurred"}), status=400,
                            mimetype='application/json') 


@bp.route('/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    headers = request.headers
    # check header here
    if 'Authorization' not in headers:
        return Response(json.dumps({"error": "missing auth"}),
                        status=401,
                        mimetype='application/json')
    url = db['name'] + '/' + db['endpoint'][2]

    response = requests.delete(url,
                               params={"objtype": "user", "objkey": user_id})
    return (response.json())


@bp.route('/<user_id>', methods=['GET'])
def get_user(user_id):
    headers = request.headers
    # check header here
    if 'Authorization' not in headers:
        return Response(
            json.dumps({"error": "missing auth"}),
            status=401,
            mimetype='application/json')
    payload = {"objtype": "user", "objkey": user_id}
    url = db['name'] + '/' + db['endpoint'][0]
    response = requests.get(url, params=payload)
    return (response.json())


@bp.route('/login', methods=['PUT'])
def login():
    try:
        content = request.get_json()
        uid = content['uid']
    except Exception:
        return json.dumps({"message": "error reading parameters"})
    url = db['name'] + '/' + db['endpoint'][0]
    response = requests.get(url, params={"objtype": "user", "objkey": uid})
    data = response.json()
    if len(data['Items']) > 0:
        encoded = jwt.encode({'user_id': uid, 'time': time.time()},
                             'secret',
                             algorithm='HS256')
    return encoded


@bp.route('/logoff', methods=['PUT'])
def logoff():
    try:
        content = request.get_json()
        _ = content['jwt']
    except Exception:
        return json.dumps({"message": "error reading parameters"})

    return json.dumps({"message": "Successfully logged out."})


# All database calls will have this prefix.  Prometheus metric
# calls will not---they will have route '/metrics'.  This is
# the conventional organization.
app.register_blueprint(bp, url_prefix='/api/v1/property/')

if __name__ == '__main__':
    if len(sys.argv) < 2:
        logging.error("Usage: app.py <service-port>")
        sys.exit(-1)

    p = int(sys.argv[1])
    # Do not set debug=True---that will disable the Prometheus metrics
    app.run(host='0.0.0.0', port=p, threaded=True)
