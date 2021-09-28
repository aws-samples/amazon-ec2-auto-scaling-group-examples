# Launch Configuration Inventory Script

This example script demonstrates how you can use AWS APIs to create an inventory of Launch Configurations in a single AWS account, or an entire [AWS Organization](https://aws.amazon.com/organizations/). 

## Running the Script in AWS CloudShell

The simplest way to run this script is to copy it into an [AWS CloudShell](https://aws.amazon.com/cloudshell/) environment and execute it. 

1. Access an [AWS CloudShell Environment](https://docs.aws.amazon.com/cloudshell/latest/userguide/working-with-cloudshell.html)
2. Copy inventory.py to your local environment.
```
curl -O "https://raw.githubusercontent.com/horsfieldsa/amazon-ec2-auto-scaling-group-examples/launch-configuration-inventory/tools/launch-configuration-inventory/inventory.py"
```
3. Execute the script with the below arguments. See the examples below for some suggestions. For a CloudShell environment you should use the -r ROLE_ARN argument to specific a role to assume, ie: `python3 inventory.py -r arn:aws:iam::[ACCOUNT_ID]:role/[ROLE_NAME]` as the script currently does not support CloudShell's inherited credentials.

## Running the Script Locally

If you want to run this script locally, you will need to ensure you have the following installed and configured.

* [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html) installed and configured with the required credentials and permissions (see below).
* [Python 3 installed](https://www.python.org/downloads/)

## Script Syntax and Arguments

```
usage: inventory.py [-h] [-f FILE] [-o] [-p PROFILE] [-or ORG_ROLE_NAME] [-r ROLE_ARN]

Generate an inventory of Launch Configurations.

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  Directs the output to a file of your choice
  -o, --org             Scan all accounts in current organization.
  -p PROFILE, --profile PROFILE
                        Use a specific AWS config profile, defaults to default profile.
  -or ORG_ROLE_NAME, --org_role_name ORG_ROLE_NAME
                        Name of role that will be assumed to make API calls in Org accounts, required for Org.
  -r ROLE_ARN, --role_arn ROLE_ARN
                        Arn of role that will be assumed to make API calls instead of profile credentials.
```

## Examples

Performs an inventory using the configured credentials in your default profile.
```
python3 inventory.py
```

Performs an inventory using the configured credentials in a profile named PROFILE_NAME.
```
python3 inventory.py -p PROFILE_NAME
```

Performs an inventory of an account by assuming the provided role ARN.
```
python3 inventory.py -r arn:aws:iam::ACCOUNT_ID:role/ROLE_NAME
```

Performs an inventory of all accounts in an AWS Organization by assuming the provided role ARN to get a list of accounts and then assumes a role named ORG_ROLE_NAME in each account in the organization.
```
python3 inventory.py -o -or ORG_ROLE_NAME -r arn:aws:iam::ACCOUNT_ID:role/ROLE_NAME
```

## Required Permissions

If you need help configuring your AWS CLI profile credentials to be able to assume a role, we suggest this [knowledge center article](https://aws.amazon.com/premiumsupport/knowledge-center/iam-assume-role-cli/).

| Argument      | Permissions                                             |
|---            |---                                                      | 
| NONE          | **Profile Credentials Require**                         |
|               | - ec2:DescribeRegions                                   |
|               | - autoscaling:DescribeLaunchConfigurations              |
|               |                                                         |
| -r ROLE_ARN   | **Profile Credentials Require**                         |
|               | - sts:AssumeRole (for ROLE_ARN)                         |
|               | **ROLE_ARN Requires**                                   |
|               | - ec2:DescribeRegions                                   |
|               | - autoscaling:DescribeLaunchConfigurations              |
|               | - organizations:ListAccounts                            |
|               | - sts:AssumeRole (for ROLE_NAME if using -o and -or)    |
|               |                                                         |
| -o            | **Profile Credentials Require**                         |
|               | - sts:AssumeRole(for ROLE_NAME or ROLE_ARN if using -r) |
|               | - organizations:ListAccounts (if not using -r)          |
|               |                                                         |
| -or ROLE_NAME | **Profile Credentials Require**                         |
|               | - sts:AssumeRole(for ROLE_NAME)                         |
|               | **ROLE_NAME Requires**                                  |
|               | - ec2:DescribeRegions                                   |
|               | - autoscaling:DescribeLaunchConfigurations              |
