from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_public_intake_page_links_to_issue_form() -> None:
    html = (ROOT / "snapshot-intake.html").read_text(encoding="utf-8")
    assert "提交第二份真實 NBA 賠率快照" in html
    assert "issues/new?template=second-snapshot.yml" in html
    assert "odds-hub-validate-intake" in html
    assert "readyForImport = true" in html


def test_issue_form_requires_observation_time_and_safety_confirmations() -> None:
    form = (ROOT / ".github" / "ISSUE_TEMPLATE" / "second-snapshot.yml").read_text(
        encoding="utf-8"
    )
    assert "True observed_at" in form
    assert "matchups.json and straight.json" in form
    assert "authorization headers" in form
    assert "required: true" in form


def test_metadata_template_has_required_fields() -> None:
    template = (
        ROOT / "data" / "templates" / "second-snapshot" / "metadata.json"
    ).read_text(encoding="utf-8")
    assert '"observedAt"' in template
    assert '"sourceId"' in template
    assert '"bookmakerId"' in template
