import json

from unipath import Path


PROJECT_DIR = Path(__file__).absolute().parent
DATA_DIR = Path(PROJECT_DIR.parent, "data")
SESSION_CACHE = Path(DATA_DIR, "session_cache.json")


BASE_URL = "https://www.trevorwatson.info/api"


# get secrets from json file
with open(Path(PROJECT_DIR.parent, "secrets/secrets.json")) as f:
    secrets = json.loads(f.read())

def get_secrets(setting, secrets=secrets):
    """Get setting variable or return exception"""
    try:
        return secrets[setting]
    except KeyError:
        error_msg = "Set the {0} enviroment variable".format(setting)
        raise ImproperlyConfigured


API_KEY = get_secrets("API_KEY")
