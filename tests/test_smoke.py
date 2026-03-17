from fastapi.testclient import TestClient

from sqlite_browser.app import create_app


def test_root_page_renders_empty_shell() -> None:
    client = TestClient(create_app())

    response = client.get("/")

    assert response.status_code == 200
    assert 'data-testid="app-shell"' in response.text
    assert 'data-testid="current-db-label">No database loaded<' in response.text
    assert 'data-testid="open-file-button"' in response.text
    assert 'data-testid="theme-toggle"' in response.text
    assert 'data-testid="explorer-pane"' in response.text
    assert 'data-testid="table-list"' in response.text
    assert 'data-testid="data-pane"' in response.text
    assert 'data-testid="selected-table-title">No table selected<' in response.text
    assert 'data-testid="data-grid"' in response.text
    assert 'data-testid="data-grid-header"' in response.text
    assert 'data-testid="data-grid-body"' in response.text
    assert 'data-testid="empty-state"' in response.text
    assert 'data-testid="error-banner"' in response.text
    assert 'data-testid="loading-indicator"' in response.text
    assert 'data-testid="pane-splitter"' in response.text
