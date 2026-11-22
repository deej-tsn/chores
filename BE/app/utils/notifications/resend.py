import datetime
import logging
import resend

from app.config import Settings
from app.utils.database.db import (
    get_dog_walkers_for_today,
    get_email_list,
    get_fortnight_start,
    get_home_chore_roster,
    get_last_monday,
)
from apscheduler.schedulers.background import BackgroundScheduler


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Notifications")

def get_sunday_email_html_template() -> str:
    return """
        <p>Hi everyone,</p>

        <p>This is a friendly reminder to please enter your dog walking times for the upcoming week.</p>

        <p>Submitting your availability ahead of time helps keep the schedule organized and avoids any last-minute issues.</p>

        <p>Thanks so much! 🐾</p>
    """

def get_daily_email_html_template(walkers : dict) -> str:
    order_dict = {"Morning" : 0, "Evening" : 1}
    walkers = "".join(
        f"<li><strong>{time}</strong>: {person}</li>" 
        for time, person in sorted(walkers.items(), key=lambda pair : order_dict.get(pair[0]))
    )

    email_template_html = f"""
        <p>Today's dog walkers:</p>
        <ul>
            {walkers}
        </ul>
    """
    return email_template_html

def get_home_chores_email_html_template(
    roster: dict[str, list[str]], period_start: datetime.date
) -> str:
    if not roster:
        return "<p>No home chores are scheduled for the next fortnight.</p>"

    items = "".join(
        f"<li><strong>{chore}</strong>: {', '.join(owners) if owners else 'Unassigned'}</li>"
        for chore, owners in roster.items()
    )

    return f"""
        <p>Home chores for the fortnight starting {period_start}:</p>
        <ul>
            {items}
        </ul>
    """

def is_fortnight_start(day: datetime.date) -> bool:
    return get_fortnight_start(day) == day

def next_home_chores_period(today: datetime.date) -> datetime.date | None:
    """Monday that starts the next fortnight, or None when the coming week is off."""
    next_monday = get_last_monday(today) + datetime.timedelta(weeks=1)
    return next_monday if is_fortnight_start(next_monday) else None

def send_home_chores_email():
    period_start = next_home_chores_period(datetime.date.today())
    # Home chores run every other week, so the weekly job is a no-op on alt weeks.
    if period_start is None:
        return

    roster = get_home_chore_roster(period_start)
    email_list = get_email_list()
    email_template: resend.Emails.SendParams = {
        "from": "Notifications <notifications@dempseypalaciotascon.com>",
        "to": email_list,
        "subject": f"Home Chores - w/c {period_start}",
        "html": get_home_chores_email_html_template(roster, period_start),
    }
    resend.Emails.send(email_template)
    logger.info("Home chores email sent")

def send_daily_dog_walkers_email():
    walkers = get_dog_walkers_for_today()
    email_list = get_email_list()
    email_template : resend.Emails.SendParams = {
        "from" : "Notifications <notifications@dempseypalaciotascon.com>",
        "to" : email_list,
        "subject" : f"Luka Walkers - {datetime.date.today()}",
        "html" : get_daily_email_html_template(walkers)
    }
    email: resend.Emails.SendResponse = resend.Emails.send(email_template)
    logger.info("Email Sent")

def send_sunday_email():
    email_list = get_email_list()
    email_template: resend.Emails.SendParams = {
        "from": "Notifications <notifications@dempseypalaciotascon.com>",
        "to": email_list,
        "subject": "Reminder: Enter Your Dog Walking Times for This Week",
        "html": get_sunday_email_html_template()
    }
    email: resend.Emails.SendResponse = resend.Emails.send(email_template)
    logger.info("Sunday reminder email sent")


def start_notifications_scheduler(settings : Settings):
    resend.api_key = settings.resend_api_key
    scheduler = BackgroundScheduler()
    
    # Daily dog-walking summary (every day)
    scheduler.add_job(
        send_daily_dog_walkers_email,
        "cron",
        hour=9,
        minute=0
    )

    # Sunday reminder to fill in next week's dog rota
    scheduler.add_job(
        send_sunday_email,
        "cron",
        day_of_week="sun",
        hour=21,
        minute=0
    )

    # Home chores: weekly trigger, the job itself no-ops on the off week
    scheduler.add_job(
        send_home_chores_email,
        "cron",
        day_of_week="sun",
        hour=21,
        minute=5
    )

    scheduler.start()
    
