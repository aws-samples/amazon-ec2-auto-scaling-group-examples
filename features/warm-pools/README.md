# Warm Pools

This example walks you through configuring Warm Pools for an Auto Scaling Group and measuring the launch time when launching pre-warmed instances from a Warm Pool as compared to launching instances directly into the Auto Scaling Group and completing bootstrapping actions.

## Prerequisites

This example assumes that you are executing the following commands from a terminal environment w/ the aws-cli installed and with credentials properly configured. If you need help installing and configuring the aws-cli please refer to these instructions: https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html

### Deploy Example Auto Saling Group CloudFormation Template

This example requires that an Auto Scaling Group has been configured within the account you are running the example in. This example works best if this Auto Scaling Group is configured with Lifecycle Hooks to manage the lifecycle of your instances. A common example is using Life Cycle Hooks to install and start an application prior to the instance being brought in service. If you'd like a quick-start template that deploys an example Auto Scaling Group then deploy one of the following templates before proceeding.

Auto Scaling Group w/ Life Cycle Hooks controlled via Userdata

Deploy the sample CloudFormation template: [HERE](../lifecycle-hooks/userdata-managed-linux/README.md)

Auto Scaling Group w/ Life Cycle Hooks controlled via a Lambda Function

Deploy the sample CloudFormation template: [HERE](../lifecycle-hooks/lambda-managed-linux/README.md)

### Install CLI Utilities

To measure scaling speed we will run a simple Bash script that takes the response of a DescribeScalingActivities API call and calculates the duration of scaling activities. To execute this script, the following CLI utilities are required. If you're not using Homebrew, refer to the following instructions for installing these on your system.

* [jq](https://stedolan.github.io/jq/download/)
* [dateutils](http://www.fresse.org/dateutils/)

```
brew install jq
brew install dateutils
```

## Activity 1: Measure the Scaling Speed of Instances Launched Directly into an Auto Scaling Group

With our Auto Scaling Group deployed, and CLI utilities installed, we can begin our first activity. In this activity we will launch an instance directly into an Auto Scaling Group. The example Auto Scaling Groups deployed earlier use Life Cycle Hooks to manage the application installation process. 

The userdata-managed example uses a script that execute on the instance when the instance first boots, and every time the instance starts. This script detects if the application is installed, and if not, installs and starts it. If the application is already installed it ensures that it's started. Once the application is installed or started, a command is executed to complete the lifecycle action and allow the instance to transtion to the next lifecycle step.

The lambda-managed example uses a Lambda function that executes in response to EventBridge events that are generated as instances transition through their lifecycle. The Lambda function can perform different actions as the instance is first launched, launched into a warm pool, or started from a warm pool. This allows the Lambda function to perform actions such as installing an application, registering an instance with a primary node, or ensuring that an application is started prior to the instance being moved in-service.

### Step 1: Increase Desired Capacity
```
aws autoscaling set-desired-capacity --auto-scaling-group-name "Example Auto Scaling Group" --desired-capacity 1
```

### Step 2: Measure Launch Speed
```
activities=$(aws autoscaling describe-scaling-activities --auto-scaling-group-name "Example Auto Scaling Group")
for row in $(echo "${activities}" | jq -r '.Activities[] | @base64'); do
    _jq() {
     echo ${row} | base64 --decode | jq -r ${1}
    }

   start_time=$(_jq '.StartTime')
   end_time=$(_jq '.EndTime')
   activity=$(_jq '.Description')

   echo $activity Duration: $(datediff $start_time $end_time)
done
```

### Step 3: Observe Launch Duration
```
Launching a new EC2 instance: i-075fa0ad6a018cdfc Duration: 243s
```

## Activity 2: Enable Warm Pools for the Auto Scaling Group

### Step 1: Put Warm Pool Configuration
```
aws autoscaling-wp put-warm-pool --auto-scaling-group-name "Example Auto Scaling Group" --pool-state Stopped --region us-west-2
```

### Step 2: Describe Warm Pool Configuration
```
aws autoscaling-wp describe-warm-pool --auto-scaling-group-name "Example Auto Scaling Group" --region us-west-2
```

```
{
    "WarmPoolConfiguration": {
        "MinSize": 0,
        "PoolState": "Stopped"
    },
    "Instances": [
        {
            "InstanceId": "i-0ea10fdc59a07df6e",
            "InstanceType": "t2.micro",
            "AvailabilityZone": "us-west-2a",
            "LifecycleState": "Warmed:Pending",
            "HealthStatus": "Healthy",
            "LaunchTemplate": {
                "LaunchTemplateId": "lt-0356f1c452b0eb0eb",
                "LaunchTemplateName": "LaunchTemplate_O7hvkiPu9hmf",
                "Version": "1"
            }
        }
    ]
}

```
{
    "WarmPoolConfiguration": {
        "MinSize": 0,
        "PoolState": "Stopped"
    },
    "Instances": [
        {
            "InstanceId": "i-0ea10fdc59a07df6e",
            "InstanceType": "t2.micro",
            "AvailabilityZone": "us-west-2a",
            "LifecycleState": "Warmed:Pending:Wait",
            "HealthStatus": "Healthy",
            "LaunchTemplate": {
                "LaunchTemplateId": "lt-0356f1c452b0eb0eb",
                "LaunchTemplateName": "LaunchTemplate_O7hvkiPu9hmf",
                "Version": "1"
            }
        }
    ]
}
```

```
{
    "WarmPoolConfiguration": {
        "MinSize": 0,
        "PoolState": "Stopped"
    },
    "Instances": [
        {
            "InstanceId": "i-0ea10fdc59a07df6e",
            "InstanceType": "t2.micro",
            "AvailabilityZone": "us-west-2a",
            "LifecycleState": "Warmed:Pending:Proceed",
            "HealthStatus": "Healthy",
            "LaunchTemplate": {
                "LaunchTemplateId": "lt-0356f1c452b0eb0eb",
                "LaunchTemplateName": "LaunchTemplate_O7hvkiPu9hmf",
                "Version": "1"
            }
        }
    ]
}
```

```
{
    "WarmPoolConfiguration": {
        "MinSize": 0,
        "PoolState": "Stopped"
    },
    "Instances": [
        {
            "InstanceId": "i-0ea10fdc59a07df6e",
            "InstanceType": "t2.micro",
            "AvailabilityZone": "us-west-2a",
            "LifecycleState": "Warmed:Stopped",
            "HealthStatus": "Healthy",
            "LaunchTemplate": {
                "LaunchTemplateId": "lt-0356f1c452b0eb0eb",
                "LaunchTemplateName": "LaunchTemplate_O7hvkiPu9hmf",
                "Version": "1"
            }
        }
    ]
}
```

### Overve Scaling Speed into Warm Pool

```
Launching a new EC2 instance into warm pool: i-0ea10fdc59a07df6e Duration: 260s
```

## Activity 3: Measure the Scaling Speed of Instances Launched From Warm Pool into an Auto Scaling Group

### Step 1: Increase Desired Capacity
```
aws autoscaling set-desired-capacity --auto-scaling-group-name "Example Auto Scaling Group" --desired-capacity 2
```

### Step 2: Measure Launch Speed
```
activities=$(aws autoscaling describe-scaling-activities --auto-scaling-group-name "Example Auto Scaling Group")
for row in $(echo "${activities}" | jq -r '.Activities[] | @base64'); do
    _jq() {
     echo ${row} | base64 --decode | jq -r ${1}
    }

   start_time=$(_jq '.StartTime')
   end_time=$(_jq '.EndTime')
   activity=$(_jq '.Description')

   echo $activity Duration: $(datediff $start_time $end_time)
done
```

### Step 3: Obesere Warm Pool Change

```
aws autoscaling-wp describe-warm-pool --auto-scaling-group-name "Example Auto Scaling Group" --region us-west-2
```

```
{
    "WarmPoolConfiguration": {
        "MinSize": 0,
        "PoolState": "Stopped"
    },
    "Instances": []
}
```

### Step 4: Observe Launch Duration 

```
activities=$(aws autoscaling describe-scaling-activities --auto-scaling-group-name "Example Auto Scaling Group")
for row in $(echo "${activities}" | jq -r '.Activities[] | @base64'); do
    _jq() {
     echo ${row} | base64 --decode | jq -r ${1}
    }

   start_time=$(_jq '.StartTime')
   end_time=$(_jq '.EndTime')
   activity=$(_jq '.Description')

   echo $activity Duration: $(datediff $start_time $end_time)
done
```

```
Launching a new EC2 instance: i-075fa0ad6a018cdfc Duration: 243s
```

## Activity 3: Testing Scaling Speed with Scaling Policies

Delete Warm Pool
```
aws autoscaling-wp delete-warm-pool --auto-scaling-group-name "Example Auto Scaling Group" --region us-west-2
```

Set Capacity to 4
```
aws autoscaling set-desired-capacity --auto-scaling-group-name "Example Auto Scaling Group" --desired-capacity 4
```

Add our scaling policy
```
aws autoscaling put-scaling-policy --cli-input-json file://scaling-policy.json
```

Stress the application
```
aws ssm send-command --cli-input-json file://ssm-stress.json
``

Measure Scaling Time 
```

```


## Conclusion

```
Launching a new EC2 instance from warm pool: i-0ea10fdc59a07df6e Duration: 36s
Launching a new EC2 instance into warm pool: i-0ea10fdc59a07df6e Duration: 260s
Launching a new EC2 instance: i-075fa0ad6a018cdfc Duration: 243s
```

## Cleanup

