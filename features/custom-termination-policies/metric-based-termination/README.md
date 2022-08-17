# Custom Termination Policy Example: Using CloudWatch metric data to select instances for termination

This example template demonstrates how to create a [custom termination policy](https://docs.aws.amazon.com/autoscaling/ec2/userguide/lambda-custom-termination-policy.html) for an EC2 Auto Scaling group that uses CloudWatch metric data to select idle instances for termination. The stack will deploy the following resources:

- A VPC that spans the whole region
- A Lambda function that implements the logic of the custom termination policy and defines environment variables for specifying threshold values for the CloudWatch metrics
- An Auto Scaling Group that uses attribute-based instance type selection (ABS) with a target tracking scaling policy, where the target metric is the average CPU consumption
- A Launch Template that defines the AMI to use when procuring capacity in the Auto Scaling Group
- A Systems Manager Document that executes [stress-ng](https://wiki.ubuntu.com/Kernel/Reference/stress-ng) within a shell script
- A State Manager association that applies the SSM Document to all the instances in the ASG

The diagram below shows the architecture that will be deployed:

## Architecture diagram

![Architecture diagram](images/architecture.png)

The Lambda function is invoked by Amazon EC2 Auto Scaling in response to certain events. It processes the information in the input data sent by Amazon EC2 Auto Scaling and returns a list of instances that are ready to terminate. This example returns all instances whose average CPU utilization is below 50% during 5 minutes. To do this, the function performs an API call to retrieve metric data from Amazon CloudWatch. The state diagram below depicts the execution flow of the Lambda function:

![Execution flow](images/lambda.png)

## Expected outcome

Once the stack is deployed, the following events will take place:

1. As many instances as specified in the parameter **DesiredCapacity** are launched to meet the initial demand for the ASG
2. The State Manager Association is automatically applied, increasing the CPU usage of the instances in the ASG
3. The dynamic scaling policy is triggered, since the target 50% of CPU usage is no longer met
4. The desired capacity of the ASG is increased to meet the new demand, and new instances are launched to procure more capacity
5. Some minutes after the State Manager Association is applied, the scale-in event is triggered invoking the Lambda function
6. The Lambda function selects instances for termination and the desired capacity of the ASG is updated accordingly

Some tips:

- You can verify the execution of the Lambda Function by:
  - Navigating to the [Lambda console](https://console.aws.amazon.com/lambda)
  - Selecting the function **customTerminationPolicy**
  - Selecting the **Monitor** tab and scrolling down to **Recent invocations**
- You can apply the State Manager Association whenever you want by:
  - Navigating to the [State Manager console](https://console.aws.amazon.com/systems-manager/state-manager)
  - Ticking the Association whose Document name is **Stress** and selecting **Apply association now**

## Deployment instructions

The following steps assume that you have Python and [venv](https://docs.python.org/3/library/venv.html) installed in your local machine.

### 1. Cloning the repository

Navigate to the directory in your machine where you want the repository to be cloned and execute the following command:

```bash
git clone https://github.com/aws-samples/amazon-ec2-auto-scaling-group-examples.git
```

### 2. Creating a virtual environment and installing project dependencies

After cloning this repository, navigate to the `features/custom-termination-policies/metric-based-termination` directory, and execute the following commands:

#### 2.1 Creating the virtual environment

```python
python3 -m venv .venv
```

#### 2.2 Installing project dependencies in the virtual environment

```python
source .venv/bin/activate
python -m pip install -r requirements.txt
```

### 3. Bootstrapping your AWS account

Deploying AWS CDK apps into an AWS environment may require that you provision resources the AWS CDK needs to perform the deployment. These resources include an Amazon S3 bucket for storing files and IAM roles that grant permissions needed to perform deployments. Execute the following command to bootstrap your environment:

```bash
cdk bootstrap
```

You can read more about this process [here](https://docs.aws.amazon.com/cdk/v2/guide/bootstrapping.html).

### 4. Deploying using CDK

When deploying you can optionally specify the value for these parameters:

- **ASGName**: name of the Auto Scaling group. The default value is `Example ASG`
- **MinCapacity**: minimum capacity that the Auto Scaling group has to procure. The default value is `1`
- **MaxCapacity**: maximum capacity that the Auto Scaling group has to procure. The default value is `6`
- **DesiredCapacity**: initial capacity that the Auto Scaling group has to procure. The default is `2`

```bash
cdk deploy --parameters ASGName=<str value> --parameters MinCapacity=<int value> --parameters MaxCapacity=<int value> --parameters DesiredCapacity=<int value>
```

If you don't want to provide a value for any of those parameters you can simply execute the following command:

```bash
cdk deploy
```

The deployment process will take roughly **5 minutes** to complete.

### 5. Cleaning up

To delete all the resources created by CDK:

1. Navigate to the **CloudFormation** section in the AWS console.
2. Select the stack named **MetricBasedTerminationStack** and click on **Delete**.