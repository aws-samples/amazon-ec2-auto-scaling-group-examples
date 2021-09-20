# Launch Configuration Inventory Script

This example script demonstrates how you can use AWS APIs to create an inventory of Launch Configurations in an AWS account across all regions active for that account. 

## Running the Script

The simplest way to run this script is to copy it into an AWS CloudShell environment. 

1. Access an [AWS CloudShell Environment](https://docs.aws.amazon.com/cloudshell/latest/userguide/working-with-cloudshell.html)
2. Copy inventory.py to your local environment.
```
curl -O "https://raw.githubusercontent.com/horsfieldsa/amazon-ec2-auto-scaling-group-examples/launch-configuration-inventory/tools/launch-configuration-inventory/inventory.py"
```

### Prerequisites

* An installed and configured AWS CLI
* Python3 
* Boto3

### Required Permissions

* DescribeRegions
* 


### Running

Run the following command to execute the script. This command will output a file named launched_configurations.csv that contains a list of all launch configurations in the AWS account 

`python3 inventory.py`