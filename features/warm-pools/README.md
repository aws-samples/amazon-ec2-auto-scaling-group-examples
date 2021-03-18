# Warm Pools

This example walks you through configuring Warm Pools for an Auto Scaling Group and measuring the launch time when launching pre-initialized instances from a Warm Pool as compared to launching instances directly into the Auto Scaling group and completing bootstrapping actions.

## Prerequisites

This example assumes that you are executing the following commands from a terminal environment w/ the aws-cli installed and with credentials properly configured. If you need help installing and configuring the aws-cli please refer to these instructions: https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html

### Deploy Example Auto Saling Group CloudFormation Template

This example requires that an Auto Scaling group has been configured within the account you are running the example in. This example works best if this Auto Scaling group is configured with lifecycle hooks to manage the lifecycle of your instances. A common example is using life cycle Hooks to install and start an application prior to the instance being brought in service. You can use one of the following templates to deploy an example Auto Scaling group for use with this walk through.

Auto Scaling group w/ Life Cycle Hooks controlled via Userdata

Deploy the sample CloudFormation template: [HERE](../lifecycle-hooks/userdata-managed-linux/README.md)

Auto Scaling group w/ Life Cycle Hooks controlled via a Lambda Function

Deploy the sample CloudFormation template: [HERE](../lifecycle-hooks/lambda-managed-linux/README.md)

### Install CLI Utilities

To measure scaling speed we will run a simple Bash script that takes the response of a DescribeScalingActivities API call and calculates the duration of scaling activities. To execute this script, the following CLI utilities are required. If you're not using Homebrew, refer to the following instructions for installing these on your system.

* [jq](https://stedolan.github.io/jq/download/)
* [dateutils](http://www.fresse.org/dateutils/)

```
brew install jq
brew install dateutils
```

## Activity 1: Measure the Launch Speed of Instances Launched Directly into an Auto Scaling Group

With our Auto Scaling group deployed, and CLI utilities installed, we can begin our first activity. In this activity we will launch an instance directly into an Auto Scaling group. The example Auto Scaling groups deployed earlier use lifecycle hooks to manage the application installation process. 

The userdata managed example uses a script that execute on the instance when the instance first boots, and every time the instance starts. This script detects if the application is installed, and if not, installs and starts it. If the application is already installed it ensures that it's started. Once the application is installed or started, a command is executed to complete the lifecycle action and allow the instance to transtion to the next lifecycle step.

The lambda managed example uses a Lambda function that executes in response to Amazon EventBridge events that are generated as instances transition through their lifecycle. The Lambda function can perform different actions as the instance is first launched, launched into a warm pool, or started from a warm pool. This allows the Lambda function to perform actions such as installing an application, registering an instance with a primary node, or ensuring that an application is started prior to the instance being moved in-service.

### Step 1: Increase Desired Capacity

Set the desired capacity of the Auto Scaling group to 1 to launch an instance directly into the Auto Scaling group. 

```
aws autoscaling set-desired-capacity --auto-scaling-group-name "Example Auto Scaling Group" --desired-capacity 1
```

### Step 2: Measure Launch Speed

Now, let's measure the launch speed of the instance.

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

Because the instance launched directly into the Auto Scaling group, all initialization actions needed to complete to prepare the instance to be placed in-service. From the results below we can see that these actions took a long time to complete, delaying how quickly our Auto Scaling group can scale.

```
Launching a new EC2 instance: i-075fa0ad6a018cdfc Duration: 243s
```

## Activity 2: Enable Warm Pools for the Auto Scaling Group

Let's add a Warm Pool to our Auto Scaling group so we can pre-initialize our instances so that they can be brought into service more rapidly.

### Step 1: Put Warm Pool Configuration

We can add a Warm Pool to our Auto Scaling group with a PutWarmPool API call. We will keep our Warm Pool instances in a stopped state after they have completed their initialization actions. We will omit the optional Warm Pool sizing parameters (--min-size and --max-group-prepared-capacity) meaning our Warm Pool will have a minimum size of 0 and a maximum repared capacity equal to the max size of the Auto Scaling group. The maximum prepared capacity will include instances launched into the Auto Scaling group, and instances launched into the Warm Pool. If you deployed one of the example Auto Scaling groups, this will be set to 2 as a default.

```
aws autoscaling-wp put-warm-pool --auto-scaling-group-name "Example Auto Scaling Group" --pool-state Stopped --region us-west-2
```

### Step 2: Describe Warm Pool Configuration

By using a DescribeWarmPool API call, we can now see that one instance was launched into our Warm Pool. This is because our Warm Pool's maximum prepared capacity is equal to the Auto Scaling group max size. Since we have one instance already in service, only one additional instance was launched into the Warm Pool to equal the maximum prepared capacity of 2.

```
aws autoscaling-wp describe-warm-pool --auto-scaling-group-name "Example Auto Scaling Group" --region us-west-2
```

When an instance is launched into a Warm Pool it will transition through lifecycle states, with Warmed:Pending.

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

If a lifecycle hook is configured, the instance can wait in a Warmed:Pending:Wait state until initialization actions are completed.

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

After initialization actions are completed, and the lifecycle hook is sent a CONTINUE signal, the instance will move to a Warmed:Pending:Proceed state.

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

Since we configured instances in our Warm Pool to be stopped after initialization, the instance launch will complete with the instance in a Warmed:Stopped state. The instance is now pre-initialized and ready to be launched into the Auto Scaling group as additional capacity is needed.

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

### Observe Launch Speed into Warm Pool

Now let's see how long it took to launch the instance into the Warm Pool.

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

As you can see from the following results, launching an instance into a Warm Pool took a similar length of time to launching an instance directly into the Auto Scaling group.

```
Launching a new EC2 instance into warm pool: i-0ea10fdc59a07df6e Duration: 260s
```

## Activity 3: Measure the Launch Speed of Instances Launched From Warm Pool into an Auto Scaling group

Now that we have pre-initialized instance in the Warm Pool, we can scale our Auto Scaling group and launch the pre-initialized instance rather than launching a new instance that has not been pre-initialized.

### Step 1: Increase Desired Capacity

Let's increase the desired capacity of our Auto Scaling group to 2.

```
aws autoscaling set-desired-capacity --auto-scaling-group-name "Example Auto Scaling Group" --desired-capacity 2
```

### Step 2: Observe Warm Pool Change

Now, let's describe our Warm Pool and observe any changes. As you can see below, the instance we previously launched is no longer in our Warm Pool. This is beause it was launched from the Warm Pool, into the Auto Scaling group in response to our increase in desired capacity.

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

### Step 3: Measure Launch Speed

We can now measure the launch speed of the instance from the Warm Pool to the Auto Scaling group.

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

As you can see from the following results, because our instance was pre-initialized our launch was duration was significantly reduced. This means we can now more rapidly place instances into service in response to load placed on our workload by launching pre-initialized instances from the Warm Pool.

```
Launching a new EC2 instance from warm pool: i-0ea10fdc59a07df6e Duration: 36s
```

## Cleanup

Follow the clean-up instructions for the stack you deployed.

* [Auto Scaling Group w/ Life Cycle Hooks controlled via Userdata](../lifecycle-hooks/userdata-managed-linux/README.md)
* [Auto Scaling Group w/ Life Cycle Hooks controlled via a Lambda Function](../lifecycle-hooks/lambda-managed-linux/README.md)