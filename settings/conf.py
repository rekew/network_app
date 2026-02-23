# Python modules
from decouple import config

# ----------------------------------------------
# Env id
#
ENV_POSSIBLE_OPTIONS = (
    "local",
    "prod",
)

ENV_ID = config("LUMI_ENV_ID", cast=str, default="local")
SECRET_KEY = config("LUMI_SECRET_KEY", cast=str, default="local")
