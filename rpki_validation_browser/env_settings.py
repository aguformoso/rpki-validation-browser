"""Settings file that overrides configs
with environment variable values

env_settings = settings + env

"""

from .settings import *

# default configs for testing
# through containers

for k, v in DATABASES['default'].items():

    os_k = f"DJANGO_DB_{k}"

    if os_k not in os.environ:
        continue

    DATABASES['default'][k] = os.environ[os_k]
