import pytest

from bmu_balancer.operations.key_store import KeyStore
from tests.factories import AssetFactory


@pytest.fixture
def key_store() -> KeyStore:
    return KeyStore(
        keys=["name", "capacity"],
        objects=[
            AssetFactory(name="One", capacity=0),
            AssetFactory(name="Two", capacity=0),
            AssetFactory(name="Three", capacity=0),
        ]
    )


def test_key_store__get_one_or_none__none(key_store: KeyStore):
    output = key_store.get_one_or_none(name="Other")
    assert key_store._cache == {}
    assert output is None


def test_key_store__get_one_or_none(key_store: KeyStore):
    output = key_store.get_one_or_none(name="One")
    assert output is not None
    assert output.name == "One"
    assert key_store._cache[("One", None,)] == [output]


def test_key_store__get(key_store: KeyStore):
    output = key_store.get(name="One")
    assert len(output) == 1
    assert output[0].name == "One"
    assert key_store._cache[("One", None,)] == output

    output = key_store.get(capacity=0)
    assert len(output) == 3
    assert len(key_store._cache) == 2
