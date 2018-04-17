import base64
from musq_modules import abstract
import logging
import time
import httplib2
try:
    from urllib.parse import urlencode
except ImportError: # Python 2
    from urllib import urlencode

class mm_sms_gateway(abstract.mm_abstract):
    def __init__(self):
        self.internal_name = "SMS gateway"
        self.cooldown = 10
        self.last_sent_ts = 0

    def on_message_received(self, topic, trigger_topic, message, config_line):
        message = message.payload.decode('UTF-8')

        n = PlivoSMSGateway()
        n.configure(self.settings.get("api_key"), self.settings.get("api_secret"))
        sender = self.settings.get("from") or "MUSQ"
        if self.settings.get("no_musq_prefix") is None:
            message = "MUSQ: " + message

        if time.time() - self.last_sent_ts >= self.cooldown:
            n.send_message(self.settings.get("phone_to"), message, sender)
        else:
            logging.warning("Not sending SMS for %s (%s), cooldown reached (last SMS sent %s)" %  ( self.instance_name, self.internal_name, self.last_sent_ts ))

    def link(self, musq_instance, settings):
        super(mm_sms_gateway, self).link(musq_instance, settings)
        logging.debug("SMS gateway (%s) linked!", self.my_id)
        self.cooldown = self.settings.get("cooldown") or 10

"""
url calls:
 - nexmo:               https://rest.nexmo.com/sms/xml?api_key=xxxxx&api_secret=xxxxxx&from=senderID&to=destination_number&text=messagebody
        For type=unicode message body should be also UTF8 encoded (URL and UTF8)
        http://www.string-functions.com/urlencode.aspx
 - twilio:      ok but weird with their outbound sms rules
 - plivo:
 - synch        ok, works
 - bandwidth.com
"""

class SMSGateway():
    api_key = ""
    api_secret = ""
    def __init__(self):
        """
        :return:nothing
        """

    def configure(self, api_key, api_secret):
        """
        :param api_key: api key
        :param api_secret: api secret, sometimes used
        :return:
        """

    def send_message(self, to, message, sender):
        """
        :param to: sms destination number
        :param message: sms message to send
        :param sender: sms origin. supports alphanumeric senders, de
        :return:
        """

class NexmoSMSGateway(SMSGateway):
    def __init__(self):
        super(NexmoSMSGateway, self).__init__()

    def configure(self, api_key, api_secret):
        """
        :param api_key: api key
        :param api_secret: api secret, sometimes used
        :return:
        """
        self.api_key = api_key
        self.api_secret = api_secret

    def send_message(self, to, message, sender):
        """
    curl -X "POST" "https://rest.nexmo.com/sms/json" \
      -d "from=Acme Inc" \
      -d "text=A text message sent using the Nexmo SMS API" \
      -d "to=TO_NUMBER" \
      -d "api_key=NEXMO_API_KEY" \
      -d "api_secret=NEXMO_API_SECRET"
        """
        h = httplib2.Http()
        data = {"api_key": self.api_key, "api_secret": self.api_secret, "text": message, "to": to, "from": sender}
        data = urlencode(data)
        headers_in = {'Content-type': 'application/x-www-form-urlencoded'}
        method = "POST"
        url = "https://rest.nexmo.com/sms/json"
        (headers_out, content) = h.request(url, method=method, body=data, headers=headers_in)
        logging.info(headers_out)
        logging.info(content)

class SinchSMSGateway(SMSGateway):
    def __init__(self):
        super(SinchSMSGateway, self).__init__()

    def configure(self, api_key, api_secret):
        """
        :param api_key: api key
        :param api_secret: api secret, sometimes used
        :return:
        """
        self.api_key = api_key
        self.api_secret = api_secret

    def send_message(self, to, message, sender):
        """
        curl --user "applicationyour_app_key:your_app_secret" --data '{"message":"your_message"}'
        -H 'Content-Type: application/json' https://messagingapi.sinch.com/v1/sms/the_phone_number
        """
        h = httplib2.Http()
        data = {"message": message}
        if sender is not None:
            data["from"] = sender
        import json
        data = json.dumps(data, separators=(',', ':'))
        # auth = "application\\" + self.api_key + ':' + self.api_secret
        # auth = base64.encodebytes(bytes(auth, "UTF-8")).decode("UTF-8")
        h.add_credentials("application\\" + self.api_key, self.api_secret)
        headers_in = {'Content-type': 'application/json'}
        method = "POST"
        url = "https://messagingapi.sinch.com/v1/sms/" + str(to)
        (headers_out, content) = h.request(url, method=method, body=data, headers=headers_in)
        logging.info(headers_out)
        logging.info(content)

class PlivoSMSGateway(SMSGateway):
    def __init__(self):
        super(PlivoSMSGateway, self).__init__()

    def configure(self, api_key, api_secret):
        """
        :param api_key: api key
        :param api_secret: api secret, sometimes used
        :return:
        """
        self.api_key = api_key
        self.api_secret = api_secret

    def send_message(self, to, message, sender):
        """
            curl -i --user AUTH_ID:AUTH_TOKEN \
            -H "Content-Type: application/json" \
            -d '{"src": "1111111111","dst": "2222222222", "text": "Hi, text from Plivo"}' \
            https://api.plivo.com/v1/Account/{auth_id}/Message/
        """

        h = httplib2.Http()
        data = {"text": message, "dst": to, "src": sender}
        data = urlencode(data)
        headers_in = {'Content-type': 'application/x-www-form-urlencoded'}
        h.add_credentials(self.api_key, self.api_secret)
        method = "POST"
        url = "https://api.plivo.com/v1/Account/" + self.api_key + "/Message/"
        (headers_out, content) = h.request(url, method=method, body=data, headers=headers_in)
        logging.info(headers_out)
        logging.info(content)


class TwilioSMSGateway(SMSGateway):
    def __init__(self):
        super(TwilioSMSGateway, self).__init__()

    def configure(self, api_key, api_secret):
        """
        :param api_key: account sid, in twillio speak
        :param api_secret: auth token
        :return:
        """
        self.api_key = api_key
        self.api_secret = api_secret

    def send_message(self, to, message, sender):
        """
    curl -X POST -F "Body=Hi there, your new phone number is working." \
    -F "From=${available_number}" -F "To=+15555555555" \
    "https://api.twilio.com/2010-04-01/Accounts/${account_sid}/Messages" \
    -u "${account_sid}:${auth_token}"
        """

        h = httplib2.Http()
        data = {"Body": message, "From": sender, "To": to }
        h.add_credentials(self.api_key, self.api_secret)
        method = "POST"
        url = "https://api.twilio.com/2010-04-01/Accounts/" + self.api_key + "/Messages"
        content_type, data_out = self.encode_multipart_formdata_fields(data, None)
        headers_in = {'Content-type': content_type}
        (headers_out, content) = h.request(url, method=method, body=data_out, headers=headers_in)
        logging.info(headers_out)
        logging.info(content)

        from xml.dom import minidom
        xmldoc = minidom.parseString(content.decode("UTF-8"))
        # print(xmldoc)

    def encode_multipart_formdata_fields(self, fields):
        """
        fields is a sequence of (name, value) elements for regular form fields.
        files is a sequence of (name, filename, value) elements for data to be uploaded as files
        Return (content_type, body) ready for httplib.HTTP instance
        """

        import os
        import binascii
        boundry = (binascii.b2a_hex(os.urandom(15)).decode("UTF-8"))
        crlf = '\r\n'
        L = []
        for (key, value) in fields.items():
            L.append('--' + boundry)
            L.append('Content-Disposition: form-data; name="%s"' % key)
            L.append('')
            L.append(str(value))
        L.append('--' + boundry + '--')
        L.append('')
        body = crlf.join(L)
        content_type = 'multipart/form-data; boundary=%s' % boundry
        return content_type, body