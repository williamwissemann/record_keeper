import pytest

from record_keeper.utilities.message import parser

test_data = []
test_ids = []

# single commands
test_data.append(
    ("!roll", {"cmd": "roll", "args": [], "date": "2021-02-24T20:54:12.890895+00:00"})
)
test_ids.append(("just roll"))

# command with args
test_data.append(
    (
        "!roll 20 20 note:aNote date:2021-02-24",
        {
            "cmd": "roll",
            "note": "aNote",
            "date": "2021-02-24 00:00:00",
            "args": ["20", "20"],
        },
    )
)
test_ids.append(("roll 20"))

# command missing prefix
test_data.append(("roll 20 note:aNote date:2021-02-24", None))
test_ids.append(("whiff a roll"))

# command with bad date
test_data.append(("!roll date:-02-24", "not an accepted date format"))
test_ids.append(("malformed date"))

# command with bad date
test_data.append(("!roll note:a a:a:", "malformed command"))
test_ids.append(("malformed command"))


@pytest.mark.parametrize("message, expected", test_data, ids=test_ids)
def test_prase(message, expected):
    try:
        parsed = parser(message)
        if expected and isinstance(expected, dict):
            assert parsed.get("cmd") == expected.get("cmd")
        else:
            assert parsed == expected
    except ValueError as e:
        assert str(e) == expected
