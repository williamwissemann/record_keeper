import record_keeper


def test___init__():
    """check record-keeper exposes a version attribute."""
    assert hasattr(record_keeper, "__version__")
    assert isinstance(record_keeper.__version__, str)
