#!/usr/bin/python
import time
import json
import base64
import urllib2
import xml.etree.ElementTree as ET
import splunk_creds


scheduled_searches = splunk_creds.scheduled_searches
username = splunk_creds.username
password = splunk_creds.password
splunk_url = splunk_creds.splunk_url


def authenticate():
    data = "username=%s&password=%s" % (username, password)
    request = urllib2.Request("%s/services/auth/login" % splunk_url, data=data)
    base64string = base64.encodestring("%s:%s" % (username, password))
    request.add_header("Authorization","Basic %s " % base64string)
    result = urllib2.urlopen(request)
    return result.read()

def splunk_request(query):
    request = urllib2.Request("%s/%s" % (splunk_url, query))
    base64string = base64.encodestring("%s:%s" % (username, password))
    request.add_header("Authorization","Basic %s " % base64string)
    result = urllib2.urlopen(request)
    return result.read()

def get_recent_search(xml_result):
    root = ET.fromstring(xml_result)


def get_sched_results(scheduled_search):
        j = splunk_request("/services/saved/searches/%s/history?output_mode=json" % scheduled_search)
        j = json.loads(j)

        job_link = ""
        date = time.strptime("1 Jan 00", "%d %b %y")
        for e in j['entry']:
            t = e['published']
            t = t[:-6]
            t = time.strptime(t, "%Y-%m-%dT%H:%M:%S")
            if t > date:
                date = t
                job_link = e['links']['alternate']

        res = splunk_request("%s?output_mode=json" % job_link)
        res = json.loads(res)
        events_link = res['entry'][0]['links']['results']
        events = splunk_request("%s?output_mode=json" % events_link)
        events = json.loads(events)
        return events

def main():
    for search in scheduled_searches:
        print get_sched_results(search)


main()
