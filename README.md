# Splunk-API-Scripts
A few scripts for interacting with Splunk API and HTTP Event Collector

For the Lambda function, you need to pass in a dict that looks like this:

{
    "events":[
        "tadablah".
        "Another Event Line blah"
    ],
    "opts":{
        "indexer":"splunk-hec-endpoint.example.com",
        "index":"scratch_index",
        "token":"<HEC Token Here>",
        "sourcetype":"garbage"
    }
}
