from main import add, greet


def test_add_logs_and_returns(capsys):
    result = add(2, 3)

    assert result == 5

    output = capsys.readouterr().out
    assert "Starting..." in output
    assert "Finished." in output


def test_greet_uppercase():
    assert greet("alex") == "HELLO ALEX"
