"""[General Configuration Params]
"""
from os import environ, path
from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))


class Config(object):
    disable_Logging = False if environ.get('disableLogging') is None else environ.get('disableLogging').casefold() == "true".casefold()
    namespace = environ.get('NAMESPACE') or "master"
    base_calculation_endpoint = environ.get('baseCalculationEndpoint') or "http://localhost:44359"
    fan_out = environ.get('fanOut') or False
