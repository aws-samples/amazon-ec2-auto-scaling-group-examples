# Faster Scaling with EC2 Auto Scaling

This repository contains a sample AWS CloudFormation template to demonstrate how to scale with sub-minute alarms using EC2 Auto Scaling target tracking scaling policies in its own Virtual Private Cloud (VPC) consisting of:

* An AWS Systems Manager (SSM) parameter holding a Unified Cloudwatch (CW) Agent configuration for reporting a custom CPUUtilization metric at a 10 seconds interval to a Cloudwatch FasterScalingDemo namespace
* An IAM Role and corresponding IAM Instance Profile with permissions to put CW metrics and retrieve SSM parameters
* A Security Group (SG) with rules allowing for ingress of TCP traffic on port 443 from the VPC's Cidr and on port 22 from the EC2 Instance Connect rage for the region.
* An EC2 Launch Template (LT) hosting the base configuration for the EC2 instance
* An EC2 Auto Scaling group using Graviton-based EC2 instances running Amazon Linux 2003
* A Target Tracking scaling policy set to scale on the custom CPUUtilization metric

## Adapting to your environment:
Consider if any of the following adaptations need to be made to the template before using in your environment:

* Update the launch template for your use case/application (e.g. using your custom AMI, or adapting the UserData script to install different software).
* Add a Load Balancer to the EC2 Auto Scaling group.
* Use a different metric that's meaningful to your application. Keeping in mind the considerations for [metrics that work with Target Tracking](https://docs.aws.amazon.com/autoscaling/ec2/userguide/as-scaling-target-tracking.html#target-tracking-considerations).
* Adapt the IAM Role's permissions and Security Group rules according to your organization's requirements.


## Using this Sample
### Deploying
* Navigate to the [Cloud Formation Console](https://us-east-1.console.aws.amazon.com/cloudformation/) in the us-east-1 (N. Virginia) region.
* Click the Create Stack button and select "With existing resources (import resources)" and follow the steps to upload the the `FasterScalingCFN.yml` template.
* When specifying Stack details, give the stack a name such as `FasterScalingDemo` and adapt any entries as needed.
* Be sure to perform this operation with an IAM User that has permissions 

### Deletening/Cleaning-up
* Navigate to the [Cloud Formation Console](https://us-east-1.console.aws.amazon.com/cloudformation/) in the us-east-1 (N. Virginia) region.
* Select the Stack you deployed on the previous step and hit the "Delete" button.


## Notes
- This sample can be deployed on other AWS Regions, make sure to adapt the stack details accordingly, like AMI and the ranges for EC2 Instance Connect.
- This sample deploys resources in a public subnet with public IP addresses to allow them to update packages from online repositories. They are not accessible externally by default. If you need to connect to the instances make sure to use [EC2 Instance Connect](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-connect-methods.html#ec2-instance-connect-connecting-console).
- This sample creates resources that incur charges to your AWS Account. Be sure to clean-up and delete the resources when not in use.

---
For more information, see [Faster Scaling with EC2 Auto Scaling](https://aws.amazon.com/blogs/compute/faster-scaling-with-amazon-ec2-auto-scaling-target-tracking/).