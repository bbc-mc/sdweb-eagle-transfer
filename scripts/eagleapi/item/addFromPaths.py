# seealso: https://api.eagle.cool/item/add-from-paths
#
import requests
import os


class EAGLE_ITEM ():
    def __init__(self, filefullpath, filename="", website="", tags:list=[], annotation=""):
        """_summary_

        Args:
            filefullpath (_type_): _description_
            filename (str, optional): _description_. Defaults to "".
            website (str, optional): _description_. Defaults to "".
            tags (list, optional): _description_. Defaults to [].
            annotation (str, optional): _description_. Defaults to "".
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

def add_from_paths(files:list[EAGLE_ITEM], folderId=None, server_url="http://localhost", port=41595, step=None):
    """EAGLE API:/api/item/addFromPaths

    Args:
        path: Required, the path of the local files.
        name: Required, the name of images to be added.
        website: The Address of the source of the images.
        annotation: The annotation for the images.
        tags: Tags for the images.
        folderId: If this parameter is defined, the image will be added to the corresponding folder.
        step: interval image num of doing POST. Defaults is None (disabled)

    Returns:
        Response: return of requests.post
    """
    step = int(step)
    API_URL = f"{server_url}:{port}/api/item/addFromPaths"

    def _init_data():
        _data = {"items": []}
        if folderId and folderId != "":
            _data.update({"folderId": folderId})
        return _data

    r_posts = []
    data = _init_data()
    for _index, _item in enumerate(files):
        _data = _item.output_data()
        if _data:
            data["items"].append(_data)
        if step and step > 0:
            if (_index - (_index // step) * step) == 0:
                r_posts += requests.post(API_URL, json=data)
                data = _init_data()
    if (len(data["items"]) > 0) or (not step or step <= 0):
        r_posts += requests.post(API_URL, json=data)

    return r_posts
