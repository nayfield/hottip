#!/usr/bin//env python

from flask import Flask, request
import requests
import json
import sys

app = Flask(__name__)

def msg_process(msg):
    for k in msg.keys():
        sys.stdout.write(k+" : "+str(msg[k])+'\n')
    atts = k['MessageAttributes']
    site = atts['Tracker']['Value']
    tid = atts['Id']['Value']
    topic = atts['Topic']['Value']
    rcmd = ['./torload', site, tid, topic ]
    retval = subprocess.call(rcmd)

@app.route('/signalserver', methods = ['POST'])
def sns():

    hdr = request.headers.get('X-Amz-Sns-Message-Type')

    if hdr:
        js = json.loads(request.get_data())
        if hdr == 'SubscriptionConfirmation' and 'SubscribeURL' in js:
            r = requests.get(js['SubscribeURL'])

        if hdr == 'Notification':
            msg_process(js)

    return 'OK\n'

# TODO remove eventually if running as flask run
if __name__ == '__main__':
    app.run(
        host = "0.0.0.0",
        port = 31630,
        debug = False
    )

