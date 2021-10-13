# Custom Termination Policy Example: Quick Start Example

This example template demonstrates how to create a [custom termination policy](https://docs.aws.amazon.com/autoscaling/ec2/userguide/lambda-custom-termination-policy.html) for an EC2 Auto Scaling group. This example stack will create an Auto Scaling group in a new VPC configured with a custom termination policy using an AWS Lambda function that Amazon EC2 Auto Scaling invokes in response to certain events. The Lambda function processes the information in the input data sent by Amazon EC2 Auto Scaling and returns a list of instances that are ready to terminate. This example returns all instances as candidates for termination, and can be customized as needed.

## Getting Started

We recommend deploying the following [Example AWS Cloud9 Environment](/environment/README.md) to get started quickly with this example. Otherwise, you can attempt to run this example using your own environment with the following prerequisites installed.

### Prerequisites

* [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html) installed and configured with Administrator credentials.

## Deployment Steps

Once you've deployed and accessed the [Example AWS Cloud9 Environment](/environment/README.md) execute the following steps from within the Example AWS Cloud9 Environment to deploy this example.

1. Change directories to this example.

```bash
cd ~/environment/amazon-ec2-auto-scaling-group-examples/features/custom-termination-policies/quick-start-example
```

2. Deploy the CloudFormation Stack. You will need to replace `REPLACE_THIS_WITH_YOUR_KEY_PAIR_NAME` with the name of an SSH key in the region you are deploying the example to.

```bash
aws cloudformation deploy \
    --template-file template.yaml \
    --stack-name custom-termination-policy-example \
    --capabilities CAPABILITY_IAM \
    --parameter-overrides \
        InstanceKeyPair=REPLACE_THIS_WITH_YOUR_KEY_PAIR_NAME
```

## Clean Up

Delete the CloudFormation Stack

```bash
aws cloudformation delete-stack --stack-name custom-termination-policy-example
```