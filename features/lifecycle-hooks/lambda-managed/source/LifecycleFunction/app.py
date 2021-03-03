# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this
# software and associated documentation files (the "Software"), to deal in the Software
# without restriction, including without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import boto3
import os
import json
import logging

from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

client = boto3.client('autoscaling')

def send_lifecycle_action(event, result):
    try:
        response = client.complete_lifecycle_action(
            LifecycleHookName=event['detail']['LifecycleHookName'],
            AutoScalingGroupName=event['detail']['AutoScalingGroupName'],
            LifecycleActionToken=event['detail']['LifecycleActionToken'],
            LifecycleActionResult=result,
            InstanceId=event['detail']['EC2InstanceId']
        )

        logger.info(response)
    except ClientError as e:
        message = 'Error completing lifecycle action: {}'.format(e)
        logger.error(message)
        raise Exception(message)
    
    return

def lambda_handler(event, context):

    logger.info(event)

    # If Instance is Launching into AutoScalingGroup
    if event['detail']['Origin'] == 'EC2' and event['detail']['Destination'] == 'AutoScalingGroup':
        logger.info('Instance Launched Into AutoScalingGroup')
        # Add Custom Actions Here
        send_lifecycle_action(event, 'CONTINUE')
        logger.info('Execution Complete')
        return

    # If Instance is Launching into WarmPool
    if event['detail']['Origin'] == 'EC2' and event['detail']['Destination'] == 'WarmPool':
        logger.info('Instance Launched into WarmPool')
        # Add Custom Actions Here
        send_lifecycle_action(event, 'CONTINUE')
        logger.info('Execution Complete')
        return

    # If Instance is Moving into ASG from WarmPool
    if event['detail']['Origin'] == 'WarmPool' and event['detail']['Destination'] == 'AutoScalingGroup':
        logger.info('Instance Moved from WarmPool to AutoScalingGroup')
        # Add Custom Actions Here
        send_lifecycle_action(event, 'CONTINUE')
        logger.info('Execution Complete')
        return

    # Else
    logger.info('An unhandled lifecycle action occured, abandoning.')
    # Add Custom Actions Here
    send_lifecycle_action(event, 'ABANDON')
    logger.info('Execution Complete')

    # End
    return
    