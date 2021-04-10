# Auto Scaling Group Lifecycle Hooks Example - Lambda Managed Windows

This example solution deploys an Auto Scaling group within a VPC. A lifecycle hook is enabled for the Auto Scaling group and a Lambda Function invokes in response to Lifecycle Action Events. The Lambda function uses AWS Systems Manager to install a sample application onto instances launched into the Auto Scaling group as they are Launched.

## Deployment

### Prerequisites

Note: For easiest deployment, create a Cloud9 instance and use the provided environment to deploy the function.

* AWS CLI already configured with Administrator permission
* [Python 3 installed](https://www.python.org/downloads/)
* [Docker installed](https://www.docker.com/community-edition)
* [SAM CLI installed](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)

### Deployment Steps

Once you've installed the requirements listed above, open a terminal sesssion as you'll need to run through a few commands to deploy the solution.

First, we need a `S3 bucket` where we can upload our Lambda functions packaged as ZIP before we deploy anything - If you don't have a S3 bucket to store code artifacts then this is a good time to create one:

```bash
aws s3 mb s3://BUCKET_NAME
```

Clone the repository.

```
git clone https://github.com/aws-samples/amazon-ec2-auto-scaling-group-examples.git
```

Change directories to this example.

```
cd amazon-ec2-auto-scaling-group-examples/features/lifecycle-hooks/lambda-managed-windows
```

Build the solution.

```
sam build --use-container
```

Package the solution.

```
sam package \
    --output-template-file packaged.yaml \
    --s3-bucket REPLACE_THIS_WITH_YOUR_S3_BUCKET_NAME
```

Deploy the solution
```
sam deploy \
    --template-file packaged.yaml \
    --stack-name lifecycle-hook-example \
    --capabilities CAPABILITY_IAM \
    --parameter-overrides \
        InstanceKeyPair=REPLACE_THIS_WITH_YOUR_KEY_PAIR_NAME  
```

## Clean Up

Delete the stack.

```
aws cloudformation delete-stack --stack-name lifecycle-hook-example
```
