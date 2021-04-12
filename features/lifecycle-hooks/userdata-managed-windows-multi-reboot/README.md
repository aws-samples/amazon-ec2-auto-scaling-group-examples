# Auto Scaling Group Lifecycle Hooks Example - User Data Managed Windows Multi Reboot

This example solution deploys an Auto Scaling group within a VPC. A lifecycle hook is enabled for the Auto Scaling group and a userdata executeds during instance startup. The userdata script installs an application if it's not installed and completes the lifecycle hook action. If the application is already installed, the userdata script starts the appliction and completes the lifecycle hook action. The userdata script is configured to execute during every instance startup, so bootstrap actions can complete when the instance is initially launched and when restarted from a stopped state. This example demonstrates how you could handle a scenario where multiple reboots were required to install and configure an application before bringing it into service.

## Getting Started

We recommend deploying the following [Example AWS Cloud9 Environment](/environment/README.md) to get started quickly with this example. Otherwise, you can attempt to run this example using your own environment with the following prerequisites installed.

### Prerequisites

* [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html) installed and configured with Administrator credentials.

## Deployment Steps

Once you've deployed and accessed the [Example AWS Cloud9 Environment](/environment/README.md) execute the following steps from within the Example AWS Cloud9 Environment to deploy this example.

1. Change directories to this example.

```bash
cd amazon-ec2-auto-scaling-group-examples/features/lifecycle-hooks/userdata-managed-windows-multi-reboot
```

2. Deploy the CloudFormation Stack. You will need to replace `REPLACE_THIS_WITH_YOUR_KEY_PAIR_NAME` with the name of an SSH key in the region you are deploying the example to.

```bash
aws cloudformation deploy \
    --template-file template.yaml \
    --stack-name lifecycle-hook-example \
    --capabilities CAPABILITY_IAM \
    --parameter-overrides \
        InstanceKeyPair=REPLACE_THIS_WITH_YOUR_KEY_PAIR_NAME
```

## Clean Up

Delete the CloudFormation Stack

```bash
aws cloudformation delete-stack --stack-name lifecycle-hook-example
```
