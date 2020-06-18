import pytest

from bmu_balancer.utils import KeyStore
from tests.factories import AssetFactory


@pytest.fixture
def key_store() -> KeyStore:
    return KeyStore(
        keys=["slug", "capacity"],
        objects=[
            AssetFactory(slug="One", capacity=0),
            AssetFactory(slug="Two", capacity=0),
            AssetFactory(slug="Three", capacity=0),
        ]
    )


def test_key_store__get_one_or_none__none(key_store: KeyStore):
    output = key_store.get_one_or_none(slug="Other")
    assert key_store.cache == {}
    assert output is None


def test_key_store__get_one_or_none(key_store: KeyStore):
    output = key_store.get_one_or_none(slug="One")
    assert output is not None
    assert output.slug == "One"
    assert key_store.cache[("One", None,)] == [output]


def test_key_store__get(key_store: KeyStore):
    output = key_store.get(slug="One")
    assert len(output) == 1
    assert output[0].slug == "One"
    assert key_store.cache[("One", None,)] == output

    output = key_store.get(capacity=0)
    assert len(output) == 3
    assert len(key_store.cache) == 2
