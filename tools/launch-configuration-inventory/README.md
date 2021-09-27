# Launch Configuration Inventory Script

This example script demonstrates how you can use AWS APIs to create an inventory of Launch Configurations in a single AWS account, or an entire AWS Organization. 

## Running the Script

The simplest way to run this script is to copy it into an AWS CloudShell environment and execute it. 

1. Access an [AWS CloudShell Environment](https://docs.aws.amazon.com/cloudshell/latest/userguide/working-with-cloudshell.html)
2. Copy inventory.py to your local environment.
```
curl -O "https://raw.githubusercontent.com/horsfieldsa/amazon-ec2-auto-scaling-group-examples/launch-configuration-inventory/tools/launch-configuration-inventory/inventory.py"
```
3. Execute the script with the following arguments. See the examples below for some suggestions. For a CloudShell environment you should use the -r argument to specific a ROLE to assume, ie: `python3 inventory.py -r arn:aws:iam::[ACCOUNT_ID]:role/[ROLE_NAME]`

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

### If you are inventorying a single account and are not using the -r argument then your profile credentials need.

* ec2:DescribeRegions
* autoscaling:DescribeLaunchConfigurations

### If you are inventorying a single account and using the -r argument then your profile credentials need.

* sts:AssumeRole (For the role specified with the argument -r ROLE_ARN)

and the role you are assuming with the -r ROLE_ARN argument needs:

* ec2:DescribeRegions
* autoscaling:DescribeLaunchConfigurations

### If you are inventorying all accounts in an organization and are not using the -r argument then your profile credentials need.

* sts:AssumeRole  (For the role specified with the argument -or ROLE_NAME)
* organizations:ListAccounts

and the role you are assuming in each account using -or ORG_ROLE_NAME needs:

* ec2:DescribeRegions
* autoscaling:DescribeLaunchConfigurations

### If you are inventorying all accounts in an organization and using the -r argument then your profile credentials need.

* sts:AssumeRole (For the role specified with the argument -r ROLE_ARN)

and the role you are assuming with the -r ROLE_ARN argument needs:

* sts:AssumeRole (For the role specified with the argument -or ORG_ROLE_NAME)
* organizations:ListAccounts

and the role you are assuming in each account using -or ORG_ROLE_NAME needs:

* ec2:DescribeRegions
* autoscaling:DescribeLaunchConfigurations