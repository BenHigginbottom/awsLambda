import boto3  
from datetime import datetime, timedelta
import logging
import re

region = "eu-west-1"  

cloudwatch = boto3.client("cloudwatch", region_name=region)  
ec2 = boto3.resource("ec2", region_name=region)
sns = boto3.resource('sns')

platform_endpoint = sns.PlatformEndpoint('[SNS-ARN-HERE]')
today = datetime.now() + timedelta(days=1) # today + 1 because we want all of today  
two_weeks = timedelta(days=14)  
start_date = today - two_weeks

logger = logging.getLogger()
logger.setLevel(logging.WARNING)

def get_available_volumes():  
    available_volumes = ec2.volumes.filter(
        Filters=[{'Name': 'status', 'Values': ['available']}]
    )
    return available_volumes

def get_metrics(volume_id):  
    """Get volume idle time on an individual volume over `start_date`
       to today"""
    metrics = cloudwatch.get_metric_statistics(
        Namespace='AWS/EBS',
        MetricName='VolumeIdleTime',
        Dimensions=[{'Name': 'VolumeId', 'Value': volume_id}],
        Period=3600,  # every hour
        StartTime=start_date,
        EndTime=today,
        Statistics=['Minimum'],
        Unit='Seconds'
    )
    return metrics['Datapoints']

def is_candidate(volume_id):  
    """Make sure the volume has not been used in the past two weeks"""
    metrics = get_metrics(volume_id)
    if len(metrics):
        for metric in metrics:
            # idle time is 5 minute interval aggregate so we use
            # 299 seconds to test if we're lower than that
            if metric['Minimum'] < 299:
                return False
    # if the volume had no metrics lower than 299 it's probably not
    # actually being used for anything so we can include it as
    # a candidate for deletion
    return True


def lambda_handler(event, context):

    available_volumes = get_available_volumes()  
    
    candidate_volumes = [  
        volume
        for volume in available_volumes
        if is_candidate(volume.volume_id)
    ]

    if 'delete' in event: 
    # delete the unused volumes
    # WARNING -- THIS DELETES DATA
        for candidate in candidate_volumes:  
            candidate.delete()
    else:
        #Build a report
        OrphanedVolumes = "The Following EBS Volumes are Orphaned: \n"
        x = 0

        for candidate in candidate_volumes:
            OrphanedVolumes = OrphanedVolumes + "- " +str(candidate)
            x = x + 1

        if x == 0:
            print "No Volumes to Delete"
        else:
            report = platform_endpoint.publish(
                Message=OrphanedVolumes,
                Subject='Orphaned Volume Report: ' +str(today),
                MessageStructure='string',
            )

            print OrphanedVolumes




    instances = ec2.instances.all()  
    my_images = ec2.images.filter(Owners=["ACCOUNT-ID-HERE"])  
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
                OldImages = OldImages + "- " +str(image)
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

    return 'AWSTidy Run'
