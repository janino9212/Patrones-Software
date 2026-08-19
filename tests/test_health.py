from src.shared.health import system_status


def test_system_status_returns_ok():
    result = system_status()

    assert result["status"] == "ok"
    assert "system" in result
