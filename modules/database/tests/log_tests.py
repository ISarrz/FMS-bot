import pytest
from modules.database.log.log import Log


@pytest.fixture(autouse=True)
def clear_database():
    for log in Log.all():
        log.delete()

def test_core_functionality():
    val1 = "log1"
    val2 = "log2"
    Log.insert(val1)
    Log.insert(val2)
    print()

    for log in Log.all():
        print(log.value)

