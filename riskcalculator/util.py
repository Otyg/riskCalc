#
# MIT License
#
# Copyright (c) 2025 Martin Vesterlund
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import decimal
import json

from otyg_risk_base.montecarlo import MonteCarloRange

def reduce_decimal_places(value:MonteCarloRange=None, ndigits:int=5) -> MonteCarloRange:
    return MonteCarloRange(min=round(value.min, ndigits), probable=round(value.probable, ndigits), max=round(value.max, ndigits))

def montecarlorange_from_dict(values:dict=None):
    if isinstance(values, dict):
        return MonteCarloRange(min=values['min'], probable=values['probable'], max=values['max'])
    else:
        return values

class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj,'to_dict'):
            return obj.to_dict()
        else:
            return json.JSONEncoder.default(self, obj)

def freeze(x):
    if isinstance(x, dict):
        return frozenset((k, freeze(v)) for k, v in x.items())
    if isinstance(x, (list, tuple)):
        return tuple(freeze(i) for i in x)
    if isinstance(x, set):
        return frozenset(freeze(i) for i in x)
    return x
