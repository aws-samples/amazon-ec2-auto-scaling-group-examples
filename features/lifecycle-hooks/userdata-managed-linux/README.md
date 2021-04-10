# Auto Scaling Group Lifecycle Hooks Example - User Data Managed Linux

This example solution deploys an Auto Scaling group within a VPC. A lifecycle hook is enabled for the Auto Scaling group and a userdata executeds during instance startup. The userdata script installs an application if it's not installed and completes the lifecycle hook action. If the application is already installed, the userdata script starts the appliction and completes the lifecycle hook action. The userdata script is configured to execute during every instance startup, so bootstrap actions can complete when the instance is initially launched and when restarted from a stopped state.

## Deployment

Clone the repository.

```
git clone https://github.com/aws-samples/amazon-ec2-auto-scaling-group-examples.git
```

Change directories to this example.

```
cd amazon-ec2-auto-scaling-group-examples/features/lifecycle-hooks/userdata-managed-linux
```

Deploy the CloudFormation Stack

```
aws cloudformation deploy \
    --template-file template.yaml \
    --stack-name lifecycle-hook-example \
    --capabilities CAPABILITY_IAM \
    --parameter-overrides \
        InstanceKeyPair=REPLACE_THIS_WITH_YOUR_KEY_PAIR_NAME
```

## Clean Up

Delete the CloudFormation Stack

```
aws cloudformation delete-stack --stack-name lifecycle-hook-example
```
