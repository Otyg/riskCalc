import decimal
import json


class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj,'to_dict'):
            return obj.to_dict()
        else:
            return json.JSONEncoder.default(self, obj)