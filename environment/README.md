# Amazon EC2 Auto Scaling Group Examples Environment

## Overview

Deploy this environment if you want an AWS Cloud9 Environment pre-configured to run the examples contained in this repository.

## Deployment

This stack will deploy an AWS Cloud9 Environment running on a t3.small instance in your default VPC. If you've removed or changed your default VPC then you may run into issues running this environment. You will be charged for running this environment based on AWS Cloud9 [pricing](https://aws.amazon.com/cloud9/pricing/).

1. Click the Launch Stack button below to deploy this environment. 
2. Switch your region if necessary. 
3. Follow the instructions to deploy the CloudFormation template. This template does not require any parameters. 
4. Complete the post deployment tasks below after the stack has been deployed. 

[![Launch Stack](https://cdn.rawgit.com/buildkite/cloudformation-launch-stack-button-svg/master/launch-stack.svg)](https://console.aws.amazon.com/cloudformation/home?region=us-west-2#/stacks/new?stackName=AutoScalingGroupExampleEnvironment&templateURL=https://amazon-ec2-auto-scaling-group-examples.s3-us-west-2.amazonaws.com/environment.yaml)

## Post Deployment

1. Open Cloud9 in the region you deployed the CloudFormation template.
2. Select "Your Environments" from the menu on the left side of the page.
3. Locate the environment with a name starting with "AutoScalingGroupExampleEnvironment" and click Open IDE.
4. When the environment launches for the first time, this repository will be cloned into ~/environment.
5. Change directories to ~/environment/amazon-ec2-auto-scaling-group-examples/environment.

```bash
cd ~/environment/amazon-ec2-auto-scaling-group-examples/environment
```
6. Run the configuration script to configure the environment. This script will take several minutes to complete.

```bash
sh configure.sh
```

7. After the script has completed, OPEN A NEW TERMINAL SESSION from the Menu Bar by navigating to Window, New Terminal. 
8. Close all other open terminal sessions.
9. You are now ready to use the examples in this repository. Each example has a README file that contains further instructions.

## Clean Up

1. Navigate to CloudFormation in the AWS console and delete the example stack. If you have a configured AWS CLI environment, and used the default stack name when launching the stack, you can delete it with the following command.

```bash
aws cloudformation delete-stack --stack-name AutoScalingGroupExampleEnvironment
```
