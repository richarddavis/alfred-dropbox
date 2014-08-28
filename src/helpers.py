import json
import hashlib
from workflow import Workflow, PasswordNotFound
from dropbox import client, rest

wf = Workflow()


def get_resource(uid, path):
    cached_resource = wf.cached_data(get_hash(uid, path), max_age = 0)
    hash_value = hash_value['hash'] if 'hash' in cached_resource else None
    access_tokens = json.loads(wf.get_password('dropbox_access_tokens'))
    api_client = client.DropboxClient(access_tokens[uid])
    try:
        resp = api_client.metadata(path, hash=hash_value, file_limit=1000)
        if 'contents' in resp:
            return resp['contents']
        else:
            return resp
    except rest.ErrorResponse, e:
        if e.status == '304':
            return cached_resource
        elif e.status == '404':
            return []
        else:
            wf.logger.debug(e)


def get_hash(uid, path):
    return "_".join([uid, hashlib.md5(path).hexdigest()])


def get_account_info():
    output = []
    for access_token in json.loads(wf.get_password('dropbox_access_tokens')).values():
        api_client = client.DropboxClient(access_token)
        output.append(api_client.account_info())
    return output


def uid_exists(uid, accounts):
    for account in accounts:
        try:
            if account['uid'] == int(uid):
                return True
        except ValueError:
            return False
    return False
