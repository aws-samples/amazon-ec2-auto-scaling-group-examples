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

from botocore.exceptions import ClientError

# Defaults 
default_output_file = "inventory.csv"
default_aws_profile = 'default'

# Arguments
parser = argparse.ArgumentParser(description='Generate an inventory of Launch Configurations.')
parser.add_argument("-f",  "--file",          help="Directs the output to a file of your choice", default=default_output_file)
parser.add_argument("-o",  "--org",           help="Scan all accounts in current organization.", action='store_true')
parser.add_argument("-p",  "--profile",       help='Use a specific AWS config profile, defaults to default profile.')
parser.add_argument("-or", "--org_role_name", help="Name of role that will be assumed to make API calls in Org accounts, required for Org.")
parser.add_argument("-r",  "--role_arn",      help="Arn of role that will be assumed to make API calls instead of profile credentials.")
parser.add_argument("-i",  "--in_use",        help="Inventories only the launch configurations that are currently in-use.", action='store_true')

parser.set_defaults(org=False)
parser.set_defaults(in_use=False)
args = parser.parse_args()

if args.org and (args.org_role_name is None):
    parser.error("--org requires --org_role_name")

# Logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Get and Return Credentials for Organization Role
def get_credentials_for_role(role_arn, credentials):

    logger.info('Attempting to assume role: {}'.format(role_arn))

    try:
        sts = None
        if credentials: 
            sts = boto3.client('sts', **credentials)
        else:
            sts = boto3.client('sts')

        response = sts.assume_role(
                    RoleArn=role_arn,
                    RoleSessionName="RoleAssume"
                )

        # Get Credentials From Session
        credentials = {
            'aws_access_key_id'     : response["Credentials"]["AccessKeyId"],
            'aws_secret_access_key' : response["Credentials"]["SecretAccessKey"],
            'aws_session_token'     : response["Credentials"]["SessionToken"],
        }

        return credentials

    except Exception as e:
        message = 'Could not assume role: {} : {}'.format(role_arn, e)
        logger.error(message)
        return None

# Get and Return Credentials for Provided AWS Profile
def get_credentials_for_profile(profile_name):
    logger.info('Attempting to get credentials for profile: {}'.format(profile_name))

    try:
        session = boto3.Session(profile_name=profile_name)
        session_credentials = session.get_credentials() 
        credentials = {
            'aws_access_key_id'     : session_credentials.access_key,
            'aws_secret_access_key' : session_credentials.secret_key
        }
        return credentials

    except Exception as e:
        message = 'Could not load profile: {} : {}'.format(profile_name, e)
        logger.error(message)
        return None

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
def get_organization_accounts(credentials):
    logger.info("Getting a list of accounts in this organization.")

    accounts = []
    try:
        organizations = boto3.client('organizations', **credentials)
        response = paginate(organizations.list_accounts)

        for account in response:
            accounts.append(account)

        return accounts

    except ClientError as e:
        message = 'Error getting a list of accounts in the organization: {}'.format(e)
        logger.error(message)

    return accounts

# Gets Regions Enabled for Account
def get_regions(account_id, credentials):
    logger.info('Getting a list of regions enabled for account {}.'.format(account_id))

    regions = []
    try:
        ec2 = boto3.client('ec2', **credentials)

        response = ec2.describe_regions(
            AllRegions=False
            )

        for region in response['Regions']:
            regions.append(region['RegionName'])

    except ClientError as e:
        message = 'Error getting list of regions: {}'.format(e)
        logger.error(message)
    
    return regions 

# Gets Launch Configurations in Account and Region
def get_launch_configurations(account_id, region, credentials):
    logger.info('Getting Launch Configurations for Region: {}'.format(region)) 

    launch_configurations = []
    try: 
        autoscaling = boto3.client('autoscaling', region_name=region, **credentials)

        response = paginate(autoscaling.describe_launch_configurations)
        
        for launch_configuration in response:
            launch_configurations.append(launch_configuration['LaunchConfigurationName'])

        return {
            'account_id'            : account_id,
            'region'                : region,
            'count'                 : len(launch_configurations),
            'launch_configuratons'  : launch_configurations
        }

    except ClientError as e:
        message = 'Error getting list of launch configurations: {}'.format(e)
        logger.error(message)

    return {}

# Gets Launch Configurations In-Use in Account and Region
def get_launch_configurations_in_use(account_id, region, credentials):
    logger.info('Getting Launch Configurations In-Use for Region: {}'.format(region)) 

    launch_configurations = []
    try: 
        autoscaling = boto3.client('autoscaling', region_name=region, **credentials)

        response = paginate(autoscaling.describe_auto_scaling_groups)
        
        for auto_scaling_group in response:
            if 'LaunchConfigurationName' in auto_scaling_group:
                launch_configurations.append({
                    'auto_scaling_group'   : auto_scaling_group['AutoScalingGroupName'],
                    'launch_configuration' : auto_scaling_group['LaunchConfigurationName']
                    })

        return {
            'account_id'            : account_id,
            'region'                : region,
            'count'                 : len(launch_configurations),
            'launch_configuratons'  : launch_configurations
        }

    except ClientError as e:
        message = 'Error getting list of launch configurations: {}'.format(e)
        logger.error(message)

    return {}


# Writes an Inventory File of Launch Configurations
def write_inventory_file(file, inventory):
    logger.info('Saving results to output file: {}'.format(file))

    data_file = open(file, 'w', newline='')
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
    profile_name = args.profile
    role_arn = args.role_arn
    org_role_name = args.org_role_name
    inventory_file = args.file

    # Get Credentials From Profile or Environment
    credentials = None   
    if role_arn:
        credentials = get_credentials_for_role(role_arn, None)
    elif profile_name:
        credentials = get_credentials_for_profile(profile_name)
    else:
        session = boto3.Session()
        session_credentials = session.get_credentials() 
        credentials = {
            'aws_access_key_id'     : session_credentials.access_key,
            'aws_secret_access_key' : session_credentials.secret_key
        }
        if hasattr(session_credentials, 'token'):
            credentials['aws_session_token'] = session_credentials.token

    if credentials is not None:

        # Inventorying Entire Organization
        if args.org is True:
            accounts = get_organization_accounts(credentials)

            # For Each Account, Attempt to Assume Role and Get Launch Configurations
            for account in accounts:
                account_id = account['Id']
                logger.info('Inventorying account: {}'.format(account_id))

                try: 
                    # Setup Session in Account
                    role_arn = 'arn:aws:iam::{}:role/{}'.format(account_id, org_role_name)
                    logger.info('Getting credentials to inventory account: {}'.format(account_id))
                    role_credentials = get_credentials_for_role(role_arn, credentials)

                    if role_credentials is not None:

                        # Get List of Regions Enabled for Account
                        regions = get_regions(account_id, role_credentials)

                        # For Each Region Get Launch Configurations
                        for region in regions:
                            if args.in_use:
                                response = get_launch_configurations_in_use(account_id, region, role_credentials)
                                inventory.append(response)
                            else:
                                response = get_launch_configurations(account_id, region, role_credentials)
                                inventory.append(response)

                # Catch and Store Errors
                except ClientError as e:
                        message = 'Error setting up session with account: {}'.format(e)
                        logger.error(message)

        # Inventorying Single Account
        if args.org is False:

            try: 
                account_id = boto3.client('sts', **credentials).get_caller_identity().get('Account')

                logger.info('Getting inventory for account {}:'.format(account_id))

                regions = get_regions(account_id, credentials)

                # For Each Region Get Launch Configurations
                for region in regions:
                    if args.in_use:
                        response = get_launch_configurations_in_use(account_id, region, credentials)
                        inventory.append(response)
                    else:
                        response = get_launch_configurations(account_id, region, credentials)
                        inventory.append(response)

            except ClientError as e:
                    message = 'Error getting inventory, check your credential configuration or try with the -r argument: {}'.format(e)
                    logger.error(message)


        # Write Outputs
        write_inventory_file(inventory_file, inventory)
        write_summary(inventory)
        return inventory

    else:
        logger.error("No credentials to perform inventory.")
        return None

if __name__ == "__main__":
    main()
