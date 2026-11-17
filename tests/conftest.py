import os
import tempfile

import pytest

# Исходная база ПР7 для тестов собирается из JSON во временном файле,
# поэтому data/petfeed.sqlite при запуске pytest не меняется.
_TEST_DB = os.path.join(tempfile.mkdtemp(), "petfeed_test.sqlite")
os.environ["PETFEED_DB"] = _TEST_DB

from db import import_json  # noqa: E402

import_json.main()


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    """Тестовая база Django заполняется тем же скриптом переноса,
    что и рабочая (один раз на весь запуск тестов)."""
    from db import import_sqlite_to_orm

    with django_db_blocker.unblock():
        import_sqlite_to_orm.main()
