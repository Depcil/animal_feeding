import os
import tempfile

import django
from django.test.utils import setup_test_environment

# Тесты работают с временной базой, построенной из JSON-файлов проекта,
# поэтому основная data/petfeed.sqlite при запуске pytest не меняется.
_TEST_DB = os.path.join(tempfile.mkdtemp(), "petfeed_test.sqlite")
os.environ["PETFEED_DB"] = _TEST_DB

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "petfeed.settings")
django.setup()
setup_test_environment()

from db import import_json  # noqa: E402

import_json.main()
