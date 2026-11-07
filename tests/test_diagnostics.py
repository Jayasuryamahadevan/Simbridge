from simbridge.diagnostics import run_probe


def test_missing_command_is_reported_without_execution(monkeypatch) -> None:
    monkeypatch.setattr("simbridge.diagnostics.shutil.which", lambda _: None)
    result = run_probe(("not-a-real-simbridge-command", "--version"))

    assert result.available is False
    assert result.exit_code is None
    assert "not found" in result.error
