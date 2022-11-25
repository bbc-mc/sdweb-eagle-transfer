# seealso: https://api.eagle.cool/application/info
#
import requests

def info(server_url="http://localhost", port=41595):
    """EAGLE API:/api/library/info

    Returns:
        Response: return of requests.post
    """

    API_URL = f"{server_url}:{port}/api/application/info"

    res = requests.get(API_URL)

    return res
