#!/usr/bin/python3

import csv
import hashlib
import json
import os
import shutil
import requests

TEAMS_PATH = 'data/late_teams.tsv'

TEMPLATE = ''

def sendEmail(email, data):
    if email.endswith('@perpendicular.institute') or email.strip() == 'IGNORE' or not email.strip():
        return
    print('Sending %s to %s' % (data, email))
    result = requests.post("https://api.mailgun.net/v3/yewlabs.org/messages",
		           auth=("api", "<API_KEY>"),
		           data={
                               "from": "Yew Labs <hq@yewlabs.org>",
			       "to": email,
			       "subject": "[MIT Mystery Hunt] MYST 2021 Kickoff and Final Logistics",
			       "template": TEMPLATE,
			       "h:X-Mailgun-Variables": json.dumps(data),
                               "h:Reply-To": "puzzle@mit.edu",
                           })
    if result.status_code != 200:
        print(result.body)
def massSendEmail():
    if not TEMPLATE:
        print("Set a template")
        return
    with open(TEAMS_PATH) as f:
        reader = csv.reader(f, delimiter="\t")
        next(reader)
        for teamInfo in reader:
            if len(teamInfo) == 0:
                continue
            username = teamInfo[1]
            name = teamInfo[2]
            password = teamInfo[3]
            email = teamInfo[4]
            phone = teamInfo[6]
            size = teamInfo[7]
            captain_email = teamInfo[5]
            data = {
                'team_username': username,
                'team_name': name,
                'team_password': password,
                'team_email': email,
                'team_phone': phone,
                'team_size': size
            }
            sendEmail(email, data)
            if captain_email != email:
                sendEmail(captain_email, data)

massSendEmail()
