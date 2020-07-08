# ping_monitor

## Add Twilio Info
Use twilio_info_example.py to create twilio_info.py
Include in it your Twilio API credentials and the phone numbers the text message will be to/from.  

## Install PIP
python3 -m virtualenv env
source env/bin/activate
pip install -r requirements.txt 

## Run the script as a service
sudo cp ping_test.service /etc/systemd/system/
sudo systemctl start ping_test.service 
sudo systemctl enable ping_test.service 