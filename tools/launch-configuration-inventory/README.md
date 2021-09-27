# Launch Configuration Inventory Script

This example script demonstrates how you can use AWS APIs to create an inventory of Launch Configurations in an AWS account across all regions active for that account. 

## Running the Script

The simplest way to run this script is to copy it into an AWS CloudShell environment. 

1. Access an [AWS CloudShell Environment](https://docs.aws.amazon.com/cloudshell/latest/userguide/working-with-cloudshell.html)
2. Copy inventory.py to your local environment.
```
curl -O "https://raw.githubusercontent.com/horsfieldsa/amazon-ec2-auto-scaling-group-examples/launch-configuration-inventory/tools/launch-configuration-inventory/inventory.py"
```
3. Execute the script with the following optional arguments. Ommitting all arguments will inventory a single account using the configured credentials in your default profile.

```
usage: inventory.py [-h] [-p PROFILE] [-f FILE] [-e ERRORFILE] [-o] [-r ROLE]

Generate an inventory of Launch Configurations.

optional arguments:
  -h, --help            show this help message and exit
  -p PROFILE, --profile PROFILE
                        Use a specific AWS config profile
  -f FILE, --file FILE  Directs the output to a file of your choice
  -e ERRORFILE, --errorfile ERRORFILE
                        Directs the output to a file of your choice
  -o, --organization    Scan all accounts in current organization.
  -r ROLE, --role ROLE  Role that will be assumed in accounts for inventory.
```

## Examples

Inventories all accounts in the current Organization using the a role named OrganizationAccountAccessRole
```
python3 inventory.py -o -r OrganizationAccountAccessRole
```


## Required Permissions

* ec2:DescribeRegions
* organiztions:ListAccounts
* autoscaling:DescribeLaunchConfigurations
* sts:AssumeRole