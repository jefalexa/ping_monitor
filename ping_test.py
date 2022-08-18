import subprocess
import time
import datetime
from twilio.rest import Client
from twilio_info import *
import logging 
import google.cloud.logging
import re


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

def ping_addr(ip_address):
    try:
        res = subprocess.call(['ping', '-c', '3', ip_address])
    except:
        res = 99
    dtnow = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d %H:%M")
    if res == 0:
        print ("{} - ping to {} OK".format(dtnow, ip_address))
    elif res == 2:
        print ("{} - no response from {}".format(dtnow, ip_address))
    else:
        print ("{} - ping to {} failed!".format(dtnow, ip_address))
    return(res)
    

def ping_sweep(subnet):
    for x in range(1, 255):
        ip_address = f"{subnet}{x}"
        print(ip_address)
        subprocess.call(['ping', '-w', '0.1', '-c', '1', ip_address])
    return    

class address:
    def __init__(self, ip_address, mac_address):
        self.call_count = 0
        self.ip_address = ip_address
        self.mac_address = mac_address
        if not self.verify_address(ip_address, mac_address):
            self.ip_address = self.find_ip_address(mac_address, subnet)
    
    def find_mac_address(self, ip_address):
        ping_addr(ip_address)
        pid = subprocess.Popen(["arp", "-n", ip_address], stdout=subprocess.PIPE)
        s = pid.communicate()[0]
        results = re.search(r"(([a-f\d]{1,2}\:){5}[a-f\d]{1,2})", str(s))
        if results:
            mac = results.groups()[0]
        else:
            mac = ''
        return(mac)

    def find_ip_address(self, mac_address, subnet):
        ping_sweep(subnet)
        pid = subprocess.Popen(["arp", "-an"], stdout=subprocess.PIPE)
        s = pid.communicate()[0]
        results = re.search(f"\(([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\) at {mac_address.lower()}", str(s).lower())
        if results:
            ip_address = results[1]
        else:
            ip_address = ''
        return(ip_address)

    def verify_address(self, ip_address, mac_address):
        mac_address2 = self.find_mac_address(ip_address)
        return(mac_address.lower() == mac_address2.lower())
    
    def get_ip_address(self):
        self.call_count += 1
        if self.call_count > 10:
            self.__init__(self.ip_address, self.mac_address)
        return(self.ip_address)
    
def main(ip_address, mac_address, device_name):    
    addr = address(ip_address, mac_address)
    alert_active = False
    while True:
        alert_count = 0

        while alert_count < 4:
            status = ping_addr(addr.get_ip_address())
            count = 0
            
            if (alert_active)&(status == 0):
                dtnow = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d %H:%M")
                print("{} - Host back up".format(dtnow))
                send_alert("{} has been restored!".format(device_name))
                alert_active = False
                

            while (status != 0)&(count<5):
                dtnow = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d %H:%M")
                print("{} - Ping failed, backoff and retry".format(dtnow))
                time.sleep(3)
                status = ping_addr(ip_address)
                count += 1

            if status != 0:
                send_alert("{} monitor is not responding!".format(device_name))
                alert_count += 1
                alert_active = True

            time.sleep(30)

        if alert_count >= 4:
            dtnow = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d %H:%M")
            print("{} - Exceeded alert count, backing off for 4 hours".format(dtnow))
            time.sleep(4*60*60)
            count = 0
            alert_count = 0

logger.info("Starting Ping Test")



ip_address = "10.0.2.217"
subnet = '10.0.2.'
mac_address = '58:EF:68:EA:54:2D'
device_name = 'Freezer'

main(ip_address, mac_address, device_name)
