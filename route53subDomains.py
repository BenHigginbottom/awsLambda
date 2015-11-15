#provide event passing 4 items
#action CREATE or DELETE 
#subDomain, name of domain to add to domain
#IP, address of the new entry
#record, CNAME or A - default to A


import boto3
import json
import re

r53client = boto3.client('route53')

hostedZoneId = 'FOO'

domain = 'BAR'


#format of the input subdomain, ip, record
def lambda_handler (event, context):

  #print("event: " + json.dumps(event, indent=2))
 
 #Mandatory Event Inputs
  if 'action' in event:
    evaction = event['action']
  else:
    return { "Value Error" : "Missing Action" }
  
  if 'subDomain' in event:
    newDomain = event['subDomain'] + domain
  else:
    return { "Value Error" : "Subdomain Missing" }
  
  #NOTE, if CNAME then IP must be a FQDN - set exception if not CNAME then IP = an IP?
  if 'IP' in event:
    ip = event['IP']
  else:
    return { "Value Error" : "IP or FQDN Missing" }

#Optional or forced set inputs

  if 'record' in event:
    recordType = event['record']
  else:
    #if were not deliberately passing a CNAME, set to A
    recordType = 'A'

  if 'awsRegion' in event:
    if awsRegion == "US":
      ctryCode = {'ContinentCode':'US'}
    elif awsRegion == "AP":
      ctryCode = {'ContinentCode':'AS'}
    elif awsRegion == "EU":
      ctryCode = {'ContinentCode':'EU'}
    else:
      return { "Value Error : AWS Region not recognised"}
  else:
    #Default to UK
    ctryCode = {'CountryCode':'GB'}

  if 'TTL' in event:
    ttl = event['TTL']
  else:
    ttl = 600

  #Make sure that the domain doesnt already exist
  if evaction == 'CREATE':
      rrs = r53client.list_resource_record_sets(HostedZoneId = hostedZoneId)['ResourceRecordSets']
      for recordSet in rrs:
        if recordSet['Name'] == newDomain:
          return { "Value Error": "Domain {} already exists".format(newDomain)}
        else:
          pass

  #Ensure that for an A record we are passing an IP

  if recordType == 'CNAME':
    if re.match(r'^((\d{1,2}|1\d{2}|2[0-4]\d|25[0-5])\.){3}(\d{1,2}|1\d{2}|2[0-4]\d|25[0-5])$', ip):
      return { "Value Error" : "You are passing an IP for a CNAME Record"}
    else:
        pass

  
  r53response = r53client.change_resource_record_sets(
    HostedZoneId = hostedZoneId,
    ChangeBatch={
        'Comment': 'Lambda Updated Record',
        'Changes': [
            {
                'Action': evaction,
                'ResourceRecordSet': {
                    'Name': newDomain,
                    'Type': recordType,
                    'SetIdentifier': 'test',
                    'GeoLocation': ctryCode,
                    'TTL': ttl,
                    'ResourceRecords': [
                        {
                            'Value': ip
                        },
                    ],
                }
            },
        ]
    }
  )

  return { 'Success' : '{}'.format(r53response)}