# seealso: https://api.eagle.cool/item/add-from-path
# seealso: https://api.eagle.cool/item/add-from-paths
#
import requests
import os


class EAGLE_ITEM_PATH:
    def __init__(self, filefullpath, filename="", website="", tags:list=[], annotation=""):
        """Data container for addFromPath, addFromPaths

        Args:
            filefullpath : Required, full path of the local files.
            filename     : (option), name of image to be added.
            website      : (option), address of the source of the image.
            tags (list)  : (option), tags for the image.
            annotation   : (option), annotation for the image.
        """
        self.filefullpath = filefullpath
        self.filename = filename
        self.website = website
        self.tags = tags
        self.annotation = annotation

    def output_data(self):
        _data = {
                "path": self.filefullpath,
                "name": os.path.splitext(os.path.basename(self.filefullpath))[0] if (self.filename == None or self.filename == "") else self.filename
            }
        if self.website and self.website != "":
            _data.update({"": self.website})
        if self.tags and len(self.tags) > 0:
            _data.update({"tags": self.tags})
        if self.annotation and self.annotation != "":
            _data.update({"annotation": self.annotation})
        return _data


def add_from_paths(files:list[EAGLE_ITEM_PATH], folderId=None, server_url="http://localhost", port=41595, step=None):
    """EAGLE API:/api/item/addFromPaths

    Method: POST

    Args:
        path: Required, the path of the local files.
        name: Required, the name of images to be added.
        website: The Address of the source of the images.
        annotation: The annotation for the images.
        tags: Tags for the images.
        folderId: If this parameter is defined, the image will be added to the corresponding folder.
        step: interval image num of doing POST. Defaults is None (disabled)

    Returns:
        Response: return of requests.posts
    """
    API_URL = f"{server_url}:{port}/api/item/addFromPaths"

    if step:
        step = int(step)

    def _init_data():
        _data = {"items": []}
        if folderId and folderId != "":
            _data.update({"folderId": folderId})
        return _data

    r_posts = []
    data = _init_data()
    for _index, _item in enumerate(files):
        _item:EAGLE_ITEM_PATH = _item
        _data = _item.output_data()
        if _data:
            data["items"].append(_data)
        if step and step > 0:
            if ((_index + 1) - ((_index + 1) // step) * step) == 0:
                _ret = requests.post(API_URL, json=data)
                try:
                    r_posts.append(_ret.json())
                except:
                    r_posts.append(_ret)
                data = _init_data()
    if (len(data["items"]) > 0) or (not step or step <= 0):
        _ret = requests.post(API_URL, json=data)
        try:
            r_posts.append(_ret.json())
        except:
            r_posts.append(_ret)

    return [ x for x in r_posts if x != "" ]
