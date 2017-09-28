
import boto3  
from datetime import datetime, timedelta
import logging
import re

region = "eu-west-1"  

cloudwatch = boto3.client("cloudwatch", region_name=region)  
ec2 = boto3.resource("ec2", region_name=region)
sns = boto3.resource('sns')

platform_endpoint = sns.PlatformEndpoint('[arn:aws:sns:eu-west-1:051785622050:AWSTidy]')
today = datetime.now() + timedelta(days=1) # today + 1 because we want all of today  
two_weeks = timedelta(days=14)  
start_date = today - two_weeks

logger = logging.getLogger()
logger.setLevel(logging.WARNING)


def lambda_handler(event, context):

    instances = ec2.instances.all()  
    my_images = ec2.images.filter(Owners=["051785622050"])  
    # anything that's running or stopped we want to keep the AMI
    good_images = set([instance.image_id for instance in ec2.instances.all()])  
    # build a dictionary of all the images that aren't in good_images
    my_images_dict = {image.id: image for image in my_images if image.id not in good_images}  
    # now lets deregister all the AMIs older than two weeks
    if 'delete' in event:
        for image in image.values():  
            created_date = datetime.strptime(
                image.creation_date, "%Y-%m-%dT%H:%M:%S.000Z")
            if created_date < two_weeks_ago:
                image.deregister()
    else:
        #Build a report
        OldImages = "The Following AMI's are unused for 2 weeks: \n"
        x = 0

        for image in image.values():  
            created_date = datetime.strptime(
                image.creation_date, "%Y-%m-%dT%H:%M:%S.000Z")
            if created_date < two_weeks_ago:
                OldImages = OldImages + "- "  + str(image) + "\n"
                x = x + 1

        if x == 0:
            print "No AMI's to Delete"
        else:
            report = platform_endpoint.publish(
                Message=OldImages,
                Subject='Old AMI Report: ' +str(today),
                MessageStructure='string',
            )

            print OldImages

    return "AWSTidy AMIs Run"
