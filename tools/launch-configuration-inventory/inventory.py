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
import logging
import sys
import csv
import argparse
import os

from botocore.exceptions import ClientError
from botocore.exceptions import ProfileNotFound

# Defaults 
default_output_file = "launch_configurations.csv"
default_error_file = "errors.csv"
default_entire_org  = False
default_aws_profile = 'default'

# Arguments
parser = argparse.ArgumentParser(description='Generate an inventory of Launch Configurations.')
parser.add_argument("-p", "--profile", help='Use a specific AWS config profile', default=default_aws_profile)
parser.add_argument("-f", "--file", help="Directs the output to a file of your choice", default=default_output_file)
parser.add_argument("-e", "--errorfile", help="Directs the output to a file of your choice", default=default_error_file)
parser.add_argument("-o","--organization",help="Scan all accounts in current organization.", action='store_true')
parser.add_argument("-r","--role",help="Role that will be assumed in accounts for inventory.")
parser.set_defaults(org=False)
args = parser.parse_args()

if args.organization and (args.role is None):
    parser.error("--organization requires --role")

# Logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Globals
errors = []

# Client
if os.environ['AWS_EXECUTION_ENV'] == 'CloudShell':

    try:
        session = boto3.Session(profile_name=args.profile)
        sts=session.client('sts')

    except Exception as e:
        message = 'Could not load credentials: {} : {}'.format(args.profile, e)
        logger.error(message)
    
else:

    try:
        session = boto3.Session(profile_name=args.profile)
        sts=session.client('sts')

    except ProfileNotFound as e:
        message = 'Could not load profile: {} : {}'.format(args.profile, e)
        logger.error(message)

# Paginates Responses from API Calls
def paginate(method, **kwargs):
    client = method.__self__

    try:
        paginator = client.get_paginator(method.__name__)
        for page in paginator.paginate(**kwargs).result_key_iters():
            for item in page:
                yield item

    except ClientError as e:
        message = 'Error describing instances: {}'.format(e)
        logger.error(message)
        raise Exception(message)

# Gets a List of Accounts in Organization
def get_organization_accounts():
    logger.info("Getting a list of accounts in this organization.")

    accounts = []

    organizations = session.client('organizations')

    response = paginate(organizations.list_accounts)
    for account in response:
        accounts.append(account)

    return accounts

# Gets Regions Enabled for Account
def get_regions(account, **credentials):
    logger.info('Getting a list of regions enabled for account {}.'.format(account['Id']))

    regions = []

    try:
        ec2 = boto3.client('ec2',
            **credentials)

        response = ec2.describe_regions(
            AllRegions=False
            )

        for region in response['Regions']:
            regions.append(region['RegionName'])

    except ClientError as e:
        message = 'Error getting list of regions: {}'.format(e)
        logger.error(message)
        errors.append({
                        'account' : account['Id'],
                        'message' : message
                    })
    
    return regions 

# Gets Launch Configurations in Account and Region
def get_launch_configurations(account, region, **credentials):
    logger.info('Getting Launch Configurations for Region: {}'.format(region)) 

    launch_configurations = []

    try: 
        autoscaling = boto3.client('autoscaling', region_name=region, **credentials)

        response = paginate(autoscaling.describe_launch_configurations)
        
        for launch_configuration in response:
            launch_configurations.append(launch_configuration['LaunchConfigurationName'])

        return {
            'account_id'             : account['Id'],
            'account_name'           : account['Name'],
            'region'                : region,
            'count'                 : len(launch_configurations),
            'launch_configuratons'  : launch_configurations
        }

    except ClientError as e:
        message = 'Error getting list of launch configurations: {}'.format(e)
        logger.error(message)
        errors.append({
                        'account' : account['Id'],
                        'message' : message
                    })

    return {}

# Writes an Inventory File of Launch Configurations
def write_inventory_file(inventory):

    logger.info('Saving results to output file: {}'.format(args.file))

    data_file = open(args.file, 'w', newline='')
    csv_writer = csv.writer(data_file)
    
    count = 0
    for data in inventory:
        if count == 0:
            header = data.keys()
            csv_writer.writerow(header)
            count += 1
        csv_writer.writerow(data.values())
    
    data_file.close()

    return

# Writes an Error File of Any Errors
def write_error_file(errors):

    logger.info('Saving errors to error file: {}'.format(args.errorfile))

    data_file = open(args.errorfile, 'w', newline='')
    csv_writer = csv.writer(data_file)
    
    count = 0
    for data in errors:
        if count == 0:
            header = data.keys()
            csv_writer.writerow(header)
            count += 1
        csv_writer.writerow(data.values())
    
    data_file.close()

    return

# Outputs Summary of Inventory
def write_summary(inventory):

    launch_configurations = 0
    accounts = []
    regions = []

    for item in inventory:
        launch_configurations = launch_configurations + item['count']
        if item['account_id'] not in accounts: accounts.append(item['account_id'])
        if item['region'] not in regions: regions.append(item['region'])

    logger.info('You have {} launch configurations across {} accounts and {} regions.'.format(launch_configurations, len(accounts), len(regions)))

    return

def main():

    inventory = []

    # If Inventorying Entire Organization 
    if args.organization is True:

        # Get a List of Accounts in Organization
        accounts = get_organization_accounts()

        # For Each Account, Attempt to Assume Role and Get Launch Configurations
        for account in accounts:
            credentials = {}
            logger.info('Getting launch configurations in account: {}'.format(account['Id']))

            try: 

                # Setup Session in Account
                role_arn = 'arn:aws:iam::{}:role/{}'.format(account['Id'], args.role)
                logger.info('Attempting to assume role: {}'.format(role_arn))
                response = sts.assume_role(
                    RoleArn=role_arn,
                    RoleSessionName='session{}'.format(account['Id'])
                )

                # Get Credentials From Session
                credentials = {
                    'aws_access_key_id'     : response["Credentials"]["AccessKeyId"],
                    'aws_secret_access_key' : response["Credentials"]["SecretAccessKey"],
                    'aws_session_token'     : response["Credentials"]["SessionToken"],
                }

                # Get List of Regions Enabled for Account
                regions = get_regions(account, **credentials)

                # For Each Region Get Launch Configurations
                for region in regions:
                    response = get_launch_configurations(account, region, **credentials)
                    inventory.append(response)

            # Catch and Store Errors
            except ClientError as e:
                    message = 'Error setting up session with account: {}'.format(e)
                    logger.error(message)
                    errors.append({
                        'account' : account['Id'],
                        'message' : message
                    })

    # If Not Inventorying Entire Organization    
    else: 

        # Get Configured Account Id
        account = {
         'Name' :  '',
         'Id'   :  sts.get_caller_identity().get('Account')
        }

        # Get Credentials From Session
        session_credentials = session.get_credentials() 
        credentials = {
            'aws_access_key_id'     : session_credentials.access_key,
            'aws_secret_access_key' : session_credentials.secret_key,
        }
        
        # Get List of Regions Enabled for Account
        regions = get_regions(account, **credentials)

        # For Each Region Get Launch Configurations
        for region in regions:
            response = get_launch_configurations(account, region, **credentials)
            inventory.append(response)

    # Write Outputs
    write_inventory_file(inventory)
    write_summary(inventory)
    if len(errors) > 0: write_error_file(errors)
    return inventory

if __name__ == "__main__":
    main()