import json

from settings import SESSION_CACHE
from utils import get_now_str


def get_new_session():
    return {
        "start": get_now_str(),
        "total": 0,
        "actions": {},
        "outcomes": {},
    }


def get_sessions():
    if SESSION_CACHE.exists():
        with open(SESSION_CACHE) as open_file:
            sessions = json.load(open_file)
    else:
        sessions = []
    return sessions


def store_session(session):
    # log stop session
    session["stop"] = get_now_str()

    # get existing sessions
    sessions = get_sessions()

    # add new session
    sessions.append(session)

    # store all sessions
    with open(SESSION_CACHE, "w") as open_file:
        json.dump(sessions, open_file, indent=4)
