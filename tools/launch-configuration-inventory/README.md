# Launch Configuration Inventory Script

This example script demonstrates how you can use AWS APIs to create an inventory of Launch Configurations in a single AWS account, or an entire [AWS Organization](https://aws.amazon.com/organizations/). 

## Running the Script in AWS CloudShell

The simplest way to run this script is to copy it into an [AWS CloudShell](https://aws.amazon.com/cloudshell/) environment and execute it. 

1. Access an [AWS CloudShell Environment](https://docs.aws.amazon.com/cloudshell/latest/userguide/working-with-cloudshell.html)
2. Copy inventory.py to your local environment.
```
curl -O "https://raw.githubusercontent.com/aws-samples/amazon-ec2-auto-scaling-group-examples/main/tools/launch-configuration-inventory/inventory.py"
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
  -i, --in_use          Inventories only the launch configurations that are currently in-use.
```

## Script Output

The script will output details as it performs the inventory. You can use these details to review and monitor progress.

```
# python3 inventory.py -r arn:aws:iam::ACCOUNT_ID:role/OrganizationAccountAccessRole
2021-09-28 11:27:59,886 - INFO - Attempting to assume role: arn:aws:iam::ACCOUNT_ID:role/OrganizationAccountAccessRole
2021-09-28 11:27:59,900 - INFO - Found credentials in shared credentials file: ~/.aws/credentials
2021-09-28 11:28:00,900 - INFO - Getting inventory for account ACCOUNT_ID:
2021-09-28 11:28:00,900 - INFO - Getting a list of regions enabled for account ACCOUNT_ID.
2021-09-28 11:28:01,135 - INFO - Getting Launch Configurations for Region: eu-north-1
2021-09-28 11:28:02,096 - INFO - Getting Launch Configurations for Region: ap-south-1
2021-09-28 11:28:03,366 - INFO - Getting Launch Configurations for Region: eu-west-3
2021-09-28 11:28:04,221 - INFO - Getting Launch Configurations for Region: eu-west-2
2021-09-28 11:28:04,987 - INFO - Getting Launch Configurations for Region: eu-west-1
2021-09-28 11:28:05,821 - INFO - Getting Launch Configurations for Region: ap-northeast-3
2021-09-28 11:28:06,475 - INFO - Getting Launch Configurations for Region: ap-northeast-2
2021-09-28 11:28:07,201 - INFO - Getting Launch Configurations for Region: ap-northeast-1
2021-09-28 11:28:07,859 - INFO - Getting Launch Configurations for Region: sa-east-1
2021-09-28 11:28:08,830 - INFO - Getting Launch Configurations for Region: ca-central-1
2021-09-28 11:28:09,388 - INFO - Getting Launch Configurations for Region: ap-southeast-1
2021-09-28 11:28:10,457 - INFO - Getting Launch Configurations for Region: ap-southeast-2
2021-09-28 11:28:11,262 - INFO - Getting Launch Configurations for Region: eu-central-1
2021-09-28 11:28:12,338 - INFO - Getting Launch Configurations for Region: us-east-1
2021-09-28 11:28:13,195 - INFO - Getting Launch Configurations for Region: us-east-2
2021-09-28 11:28:14,226 - INFO - Getting Launch Configurations for Region: us-west-1
2021-09-28 11:28:14,879 - INFO - Getting Launch Configurations for Region: us-west-2
2021-09-28 11:28:15,592 - INFO - Saving results to output file: inventory.csv
2021-09-28 11:28:15,593 - INFO - You have 3 launch configurations across 1 accounts and 17 regions.
```

## Errors

If the script encounters any exceptions they will be logged to the output as errors. In most cases the inventory will continue to run (this is useful if you have a role with access to most, but not all, accounts in an Organization).

```
python3 inventory.py -r arn:aws:iam::ACCOUNT_ID:role/OrganizationAccountAccessRole -o -or OrganizationAccountAccessRole
2021-09-28 11:54:31,881 - INFO - Attempting to assume role: arn:aws:iam::ACCOUNT_ID:role/OrganizationAccountAccessRole
2021-09-28 11:54:31,904 - INFO - Found credentials in shared credentials file: ~/.aws/credentials
2021-09-28 11:54:32,392 - INFO - Getting a list of accounts in this organization.
2021-09-28 11:54:33,145 - INFO - Inventorying account: SECOND_ACCOUNT_ID
2021-09-28 11:54:33,145 - INFO - Getting credentials to inventory account: SECOND_ACCOUNT_ID
2021-09-28 11:54:33,145 - INFO - Attempting to assume role: arn:aws:iam::SECOND_ACCOUNT_ID:role/OrganizationAccountAccessRole
2021-09-28 11:54:33,584 - INFO - Getting a list of regions enabled for account SECOND_ACCOUNT_ID.
2021-09-28 11:54:33,810 - ERROR - Error getting list of regions: An error occurred (UnauthorizedOperation) when calling the DescribeRegions operation: You are not authorized to perform this operation.
```

## Output File

The inventory outputs to a file named `inventory.csv` by default. You can redirect this to another file by using the -f argument.

```
account_id,region,count,launch_configuratons
ACCOUNT_ID,eu-north-1,0,[]
ACCOUNT_ID,ap-south-1,0,[]
ACCOUNT_ID,eu-west-3,0,[]
ACCOUNT_ID,eu-west-2,0,[]
ACCOUNT_ID,eu-west-1,0,[]
ACCOUNT_ID,ap-northeast-3,0,[]
ACCOUNT_ID,ap-northeast-2,0,[]
ACCOUNT_ID,ap-northeast-1,0,[]
ACCOUNT_ID,sa-east-1,0,[]
ACCOUNT_ID,ca-central-1,0,[]
ACCOUNT_ID,ap-southeast-1,0,[]
ACCOUNT_ID,ap-southeast-2,0,[]
ACCOUNT_ID,eu-central-1,0,[]
ACCOUNT_ID,us-east-1,0,[]
ACCOUNT_ID,us-east-2,0,[]
ACCOUNT_ID,us-west-1,0,[]
ACCOUNT_ID,us-west-2,3,"['ExampleOne', 'ExampleTwo', 'test']"
```

## Examples

Performs an inventory using the configured credentials in your default profile.
```
python3 inventory.py
```

Performs an inventory of in-use launch configurations using the configured credentials in your default profile. **Note: In-use means that they are actively associated with an Auto Scaling group.**
```
python3 inventory.py -i
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

| Argument      | Permissions                                              |
|---            |---                                                       | 
| NONE          | **Profile Credentials Require**                          |
|               | - ec2:DescribeRegions                                    |
|               | - autoscaling:DescribeLaunchConfigurations               |
|               |                                                          |
| -r ROLE_ARN   | **Profile Credentials Require**                          |
|               | - sts:AssumeRole (for ROLE_ARN)                          |
|               | **ROLE_ARN Requires**                                    |
|               | - ec2:DescribeRegions                                    |
|               | - autoscaling:DescribeLaunchConfigurations               |
|               | - autoscaling:DescribeAutoScalingGroups                  |
|               | - organizations:ListAccounts                             |
|               | - sts:AssumeRole (for ROLE_NAME if using -o and -or)     |
|               |                                                          |
| -o            | **Profile Credentials Require**                          |
|               | - sts:AssumeRole(for ROLE_NAME or ROLE_ARN if using -r)  |
|               | - organizations:ListAccounts (if not using -r)           |
|               |                                                          |
| -or ROLE_NAME | **Profile Credentials Require**                          |
|               | - sts:AssumeRole(for ROLE_NAME)                          |
|               | **ROLE_NAME Requires**                                   |
|               | - ec2:DescribeRegions                                    |
|               | - autoscaling:DescribeLaunchConfigurations               |
|               |                                                          |
| -i            | **Profile Credentials Require**                          |
|               | - autoscaling:DescribeAutoScalingGroups (if not using -r)|
|               | **ROLE_NAME Requires**                                   |
|               | - autoscaling:DescribeAutoScalingGroups                  |