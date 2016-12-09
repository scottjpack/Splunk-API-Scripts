import re
import logging
import json
import socket
import time
import urllib2

_max_content_bytes = 100000
http_event_collector_SSL_verify = True
http_event_collector_debug = True

log = logging.getLogger(__name__)

def lambda_handler(event, context):
    # event needs to have an opts dictionary with indexer, token, index, and sourcetype, 
    opts = event['opts']
    print "Send %s events to %s" % (len(event['events']), opts['indexer'])
    print opts
    send_splunk(event['events'], opts)

def send_splunk(events, opts, index_override=None, sourcetype_override=None):
  #Get Splunk Options
  logging.info("Options: %s" % json.dumps(opts))
  http_event_collector_key = opts['token']
  http_event_collector_host = opts['indexer']
  #Set up the collector
  splunk_event = http_event_collector(http_event_collector_key, http_event_collector_host)

  #init the payload
  payload = {}

  for event in events:
    #Set up the event metadata
    if index_override is None:
      payload.update({"index":opts['index']})
    else:
      payload.update({"index":index_override})
    if sourcetype_override is None:
      payload.update({"sourcetype":opts['sourcetype']})
    else:
      payload.update({"index":sourcetype_override})

    #Add the event
    payload.update({"event":event})
    #fire it off
    splunk_event.batchEvent(payload)
  splunk_event.flushBatch()


class http_event_collector:

    def __init__(self,token,http_event_server,host="",http_event_port='8088',http_event_server_ssl=True,max_bytes=_max_content_bytes):
        self.token = token
        self.batchEvents = []
        self.maxByteLength = max_bytes
        self.currentByteLength = 0

        # Set host to specified value or default to localhostname if no value provided
        if host:
            self.host = host
        else:
            self.host = socket.gethostname()

        # Build and set server_uri for http event collector
        # Defaults to SSL if flag not passed
        # Defaults to port 8088 if port not passed

        if http_event_server_ssl:
            buildURI = ['https://']
        else:
            buildURI = ['http://']
        for i in [http_event_server,':',http_event_port,'/services/collector/event']:
            buildURI.append(i)
        self.server_uri = "".join(buildURI)


    def sendEvent(self,payload,eventtime=""):
        # Method to immediately send an event to the http event collector

        # If eventtime in epoch not passed as optional argument use current system time in epoch
        if not eventtime:
            eventtime = str(int(time.time()))

        # Fill in local hostname if not manually populated
        if 'host' not in payload:
            payload.update({"host":self.host})

        # Update time value on payload if need to use system time
        data = {"time":eventtime}
        data.update(payload)

        # send event to http event collector
        request = urllib2.Request(self.server_uri)
        request.add_header("Authorization", "Splunk " + self.token)
        request.add_data(json.dumps(data))    
        response = urllib2.urlopen(request)   
        print response.read()
        
    def batchEvent(self,payload,eventtime=""):
        # Method to store the event in a batch to flush later

        # Fill in local hostname if not manually populated
        if 'host' not in payload:
            payload.update({"host":self.host})

        payloadLength = len(json.dumps(payload))

        if (self.currentByteLength+payloadLength) > self.maxByteLength:
            self.flushBatch()
            # Print debug info if flag set
            if http_event_collector_debug:
                print "auto flushing"
        else:
            self.currentByteLength=self.currentByteLength+payloadLength

        # If eventtime in epoch not passed as optional argument use current system time in epoch
        if not eventtime:
            eventtime = str(int(time.time()))

        # Update time value on payload if need to use system time
        data = {"time":eventtime}
        data.update(payload)
        self.batchEvents.append(json.dumps(data))

    def flushBatch(self):
        # Method to flush the batch list of events

        if len(self.batchEvents) > 0:
            
            request = urllib2.Request(self.server_uri)
            request.add_header("Authorization", "Splunk " + self.token)
            request.add_data(" ".join(self.batchEvents))    
            response = urllib2.urlopen(request)    
            print response.read()
        
        self.batchEvents = []
        self.currentByteLength = 0
