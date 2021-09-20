# Launch Configuration Inventory Script

This example script demonstrates how you can use AWS APIs to create an inventory of Launch Configurations in an AWS account across all regions active for that account. 

## Running the Script

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