import requests

from api.APIConfig import APIConfig

from api.thirdparty.UnipileService import UnipileService


global G

G = dict()

def get_unipile():
    global G

    UNIPILE_CONFIG = APIConfig.get("Unipile")

    unipile = G.get("UNIPILE_SERVICE", None)

    if unipile is None:
        unipile = G["UNIPILE_SERVICE"] = UnipileService(
            authorization_key=UNIPILE_CONFIG["AuthorizationKey"],
            subdomain=UNIPILE_CONFIG["Subdomain"],
            port=UNIPILE_CONFIG["Port"]
        )

    return unipile
