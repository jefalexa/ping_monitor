import subprocess
import time
import datetime
from twilio.rest import Client
from twilio_info import *
import logging 
import google.cloud.logging

# Setup Logging
file_name = ("Ping Test")
logger = logging.getLogger(__name__)
logging.basicConfig(format="%(filename)s:%(lineno)s - %(funcName)s() %(message)s")
logger.setLevel(logging.INFO)

auth_file = "VirtualToolbox-5f6ecffdcf58.json"

client = google.cloud.logging.Client.from_service_account_json(auth_file)
client.setup_logging()


# Setup Twilio

client = Client(twilio_sid, twilio_auth_token)

def send_alert(msg):
    dtnow = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d %H:%M")
    msg_body = "{}:  {}".format(dtnow, msg)
    try:
        logger.error(msg_body)
        message = client.messages.create(body=msg_body,from_=phone_num_from,to=phone_num_to)
        time.sleep(30)
        logger.info("Attemped to send alert text.  Status:  {}".format(message.status))
    except:
        logger.critical("Attemped to send alert text.  Status:  Failed")
 

# Setup Ping script

def ping_addr(address):
    try:
        res = subprocess.call(['ping', '-c', '3', address])
    except:
        res = 99
    dtnow = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d %H:%M")
    if res == 0:
        print ("{} - ping to {} OK".format(dtnow, address))
    elif res == 2:
        print ("{} - no response from {}".format(dtnow, address))
    else:
        print ("{} - ping to {} failed!".format(dtnow, address))
    return(res)
    
    
def main():    
    while True:
        alert_count = 0

        while alert_count < 4:
            status = ping_addr(address)
            count = 0

            while (status != 0)&(count<5):
                dtnow = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d %H:%M")
                print("{} - Ping failed, backoff and retry".format(dtnow))
                time.sleep(3)
                status = ping_addr(address)
                count += 1

            if status != 0:
                send_alert("Host {} is down!".format(address))
                alert_count += 1

            time.sleep(30)

        if alert_count >= 4:
            dtnow = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d %H:%M")
            print("{} - Exceeded alert count, backing off for 24 hours".format(dtnow))
            #time.sleep(24*60*60)
            time.sleep(60)
            count = 0
            alert_count = 0

logger.info("Starting Ping Test")

address = "10.0.2.183"
main()