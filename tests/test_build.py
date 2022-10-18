import pytest

from breathing_cat import build


def test_construct_intersphinx_mapping_config():
    # empty:
    assert build._construct_intersphinx_mapping_config({}) == "{}"

    # single
    cfg = build._construct_intersphinx_mapping_config({"foo": "https://foo.bar"})
    assert cfg == "{'foo': ('https://foo.bar', None)}"

    # multi
    cfg = build._construct_intersphinx_mapping_config(
        {"foo": "https://foo.bar", "bar": {"target": "bar.com", "inventory": "bar.inv"}}
    )
    assert cfg == "{'foo': ('https://foo.bar', None), 'bar': ('bar.com', 'bar.inv')}"

    # type checks
    with pytest.raises(AssertionError):
        build._construct_intersphinx_mapping_config({42: "foo"})
    with pytest.raises(AssertionError):
        build._construct_intersphinx_mapping_config({"foo": 42})
    with pytest.raises(AssertionError):
        build._construct_intersphinx_mapping_config(
            {"foo": {"target": 13, "inventory": "inv"}}
        )
    with pytest.raises(AssertionError):
        build._construct_intersphinx_mapping_config(
            {"foo": {"target": "url", "inventory": 42}}
        )
