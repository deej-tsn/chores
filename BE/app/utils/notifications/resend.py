import datetime
import logging
import resend

from app.config import Settings
from app.utils.database.db import get_dog_walkers_for_today, get_email_list
from apscheduler.schedulers.background import BackgroundScheduler


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Notifications")

base_email_template : resend.Emails.SendParams = {
    "from" : "Notifications <notifications@dempseypalaciotascon.com>",
    "subject": f"Luka Walkers - {datetime.date.today()}",
}

def get_html_template(walkers : dict) -> str:
    walkers = "".join(
        f"<li><strong>{time}</strong>: {person}</li>" 
        for time, person in walkers.items()
    )

    email_template_html = f"""
        <p>Today's dog walkers:</p>
        <ul>
            {walkers}
        </ul>
    """

    return email_template_html

def send_daily_email():
    walkers = get_dog_walkers_for_today()
    email_list = get_email_list()
    email_template = base_email_template.copy()
    email_template["to"] = email_list
    email_template['html'] = get_html_template(walkers)
    email: resend.Emails.SendResponse = resend.Emails.send(email_template)
    logger.info("Email Sent")

def start_notifications_scheduler(settings : Settings):
    resend.api_key = settings.resend_api_key
    scheduler = BackgroundScheduler()
    scheduler.add_job(send_daily_email, "cron", hour=9, minute=0)
    scheduler.start()
    
