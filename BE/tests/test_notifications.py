"""Tests for the home-chores email.

The fortnightly reminder is scheduled weekly and no-ops on the off week, so the
interesting part is the date decision — kept in pure functions specifically so it
can be tested without freezing the clock.
"""

import datetime

import pytest

from app.utils.database.db import FORTNIGHT_ANCHOR
from app.utils.notifications import resend as resend_module


def days(n: int) -> datetime.date:
    return FORTNIGHT_ANCHOR + datetime.timedelta(days=n)


@pytest.mark.parametrize(
    "day, expected",
    [
        (days(0), True),    # anchor Monday
        (days(7), False),   # off week
        (days(13), False),  # last day of the anchor fortnight
        (days(14), True),   # next fortnight
        (days(13 + 14), False),
    ],
)
def test_is_fortnight_start(day: datetime.date, expected: bool):
    assert resend_module.is_fortnight_start(day) is expected


def test_next_period_is_the_anchor_week():
    # The Sunday before the anchor fortnight: tomorrow starts a new period.
    assert resend_module.next_home_chores_period(days(-1)) == FORTNIGHT_ANCHOR


def test_next_period_is_none_on_the_off_week():
    # The Sunday before the off week: tomorrow is a Monday that starts nothing.
    assert resend_module.next_home_chores_period(days(6)) is None


def test_email_template_marks_unassigned_chores():
    html = resend_module.get_home_chores_email_html_template(
        {"Clean the house": ["Alice", "Bob"], "Grocery shopping": []},
        FORTNIGHT_ANCHOR,
    )

    assert "Clean the house" in html
    assert "Alice, Bob" in html
    assert "Unassigned" in html


class _FakeEmails:
    sent: list = []

    @classmethod
    def send(cls, params):
        cls.sent.append(params)
        return {"id": "fake"}


class _FakeResend:
    Emails = _FakeEmails
    api_key = "test"


def test_send_home_chores_email_skips_the_off_week(monkeypatch):
    monkeypatch.setattr(resend_module, "next_home_chores_period", lambda today: None)
    monkeypatch.setattr(resend_module, "resend", _FakeResend)
    _FakeEmails.sent = []

    resend_module.send_home_chores_email()

    assert _FakeEmails.sent == []


def test_send_home_chores_email_sends_on_a_fortnight_start(monkeypatch):
    monkeypatch.setattr(
        resend_module, "next_home_chores_period", lambda today: FORTNIGHT_ANCHOR
    )
    monkeypatch.setattr(
        resend_module, "get_home_chore_roster", lambda period: {"Clean the house": []}
    )
    monkeypatch.setattr(resend_module, "get_email_list", lambda: ["a@example.com"])
    monkeypatch.setattr(resend_module, "resend", _FakeResend)
    _FakeEmails.sent = []

    resend_module.send_home_chores_email()

    assert len(_FakeEmails.sent) == 1
    assert _FakeEmails.sent[0]["to"] == ["a@example.com"]
