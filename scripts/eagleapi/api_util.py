
# util for /api/folder/list
def findFolderByID(r_posts, target_id):
    return findFolderByName(r_posts, target_id, findByID=True)

def findFolderByName(r_posts, target_name, findByID=False):
    _ret = []
    if not target_name or target_name == "" or not r_posts:
        return None
    _all_folder = getAllFolder(r_posts)
    for _data in _all_folder:
        if (findByID and _data.get("id", "") == target_name) or (_data.get("name", "") == target_name):
            _ret = _data
            break
    return _ret

def getAllFolder(r_posts):
    """ get dict of {"folderId": _data, ..."""
    def dig_folder(data, dig_count, dig_limit=10):
        dig_count+=1
        if(dig_count>dig_limit):
            return []
        _ret = [data]
        if "children" in data and len(data["children"]) > 0:
            for _child in data["children"]:
                _ret += dig_folder(_child, dig_count)
        return _ret
    _ret = []
    if not r_posts:
        return None
    _posts = r_posts.json()
    if not _posts or "status" not in _posts or _posts["status"] != "success":
        return None
    if "data" in _posts and len(_posts["data"]) > 0:
        for _data in _posts["data"]:
            _ret += dig_folder(_data, 0)
    return _ret
