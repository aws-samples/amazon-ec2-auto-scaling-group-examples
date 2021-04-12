# Auto Scaling Group Lifecycle Hooks Example - Lambda Managed Windows

This example solution deploys an Auto Scaling group within a VPC. A lifecycle hook is enabled for the Auto Scaling group and a Lambda Function invokes in response to Lifecycle Action Events. The Lambda function uses AWS Systems Manager to install a sample application onto instances in the Auto Scaling group as they are Launched.

## Getting Started

We recommend deploying the following [Example AWS Cloud9 Environment](/environment/README.md) to get started quickly with this example. Otherwise, you can attempt to run this example using your own environment with the following prerequisites installed.

### Prerequisites

* [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html) installed and configured with Administrator credentials.
* [Python 3 installed](https://www.python.org/downloads/)
* [Docker installed](https://www.docker.com/community-edition)
* [SAM CLI installed](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)

## Deployment Steps

Once you've deployed and accessed the [Example AWS Cloud9 Environment](/environment/README.md) execute the following steps from within the Example AWS Cloud9 Environment to deploy this example.

1. Create a `S3 bucket` where we can upload our packaged Lambda functions for deployment.

```bash
aws s3 mb s3://BUCKET_NAME
```

2. Change directories to this example.

```bash
cd amazon-ec2-auto-scaling-group-examples/features/lifecycle-hooks/lambda-managed-windows
```

3. Build the solution.

```bash
sam build --use-container
```

5. Package the solution. You will need to replace `REPLACE_THIS_WITH_YOUR_S3_BUCKET_NAME` with the name of the S3 bucket created in the first step.

```bash
sam package \
    --output-template-file packaged.yaml \
    --s3-bucket REPLACE_THIS_WITH_YOUR_S3_BUCKET_NAME
```

6. Deploy the solution. You will need to replace `REPLACE_THIS_WITH_YOUR_KEY_PAIR_NAME` with the name of an SSH key in the region you are deploying the example to.

```bash
sam deploy \
    --template-file packaged.yaml \
    --stack-name lifecycle-hook-example \
    --capabilities CAPABILITY_IAM \
    --parameter-overrides \
        InstanceKeyPair=REPLACE_THIS_WITH_YOUR_KEY_PAIR_NAME  
```

## Clean Up

1. Delete the stack.

```bash
aws cloudformation delete-stack --stack-name lifecycle-hook-example
```