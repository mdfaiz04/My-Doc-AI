import json
from django.contrib.auth.hashers import make_password, check_password
from bson.objectid import ObjectId

def json_req(request):
    try:
        return json.loads(request.body.decode())
    except:
        return {}
        
def to_id(obj):
    return str(obj["_id"]) if "_id" in obj else None
