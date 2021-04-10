# Auto Scaling Group Lifecycle Hooks Example - Lambda Managed Windows

This example solution deploys an Auto Scaling group within a VPC. A lifecycle hook is enabled for the Auto Scaling group and a Lambda Function invokes in response to Lifecycle Action Events. The Lambda function uses AWS Systems Manager to install a sample application onto instances launched into the Auto Scaling group as they are Launched.

## Deployment

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
