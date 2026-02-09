import datetime
import logging
import resend

from app.config import Settings
from app.utils.database.db import get_dog_walkers_for_today, get_email_list
from apscheduler.schedulers.background import BackgroundScheduler


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Notifications")

def get_html_template(walkers : dict) -> str:
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

def send_daily_email():
    walkers = get_dog_walkers_for_today()
    email_list = get_email_list()
    email_template : resend.Emails.SendParams = {
        "from" : "Notifications <notifications@dempseypalaciotascon.com>",
        "to" : email_list,
        "subject" : f"Luka Walkers - {datetime.date.today()}",
        "html" : get_html_template(walkers)
    }
    email: resend.Emails.SendResponse = resend.Emails.send(email_template)
    logger.info("Email Sent")

def start_notifications_scheduler(settings : Settings):
    resend.api_key = settings.resend_api_key
    scheduler = BackgroundScheduler()
    scheduler.add_job(send_daily_email, "cron", hour=22, minute=21)
    scheduler.start()
    
