#!/usr/bin/env python3

import json
import subprocess



def get_tors_tags():
    """ return json of minimal client state"""
    fields = ['hash', 'custom_getter', 'custom_1' ]
    rcmd = ["rtcontrol", '-q', '--json', '*', '-o' + ','.join(fields)]
    cout = subprocess.check_output(rcmd)
    return json.loads(cout)


needstag = {}

for t in get_tors_tags():
    if t['custom_getter']:
        if t['custom_getter'] != t['custom_1']:
            if t['custom_1']:
                print(t['custom_getter'],"will override",t['custom_1'])
            if t['custom_getter'] not in needstag:
                needstag[t['custom_getter']] = []
            needstag[t['custom_getter']].append(t['hash'])


for tag in needstag.keys():
    print(tag, len(needstag[tag]))
    # Just go all in
    rcmd = ['rtcontrol', '-qohash', 'custom_getter='+tag, '--custom=1='+tag]
    subprocess.check_output(rcmd)
