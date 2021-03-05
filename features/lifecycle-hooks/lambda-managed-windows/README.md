# Auto Scaling Group Lifecycle Hooks Example - User Data Managed

## Deployment

## Clean Up

Example Launch Event
```
[INFO]	2021-03-02T20:40:55.89Z	5e0d845f-d11b-4d92-be3c-b81e8dc921bf	{'version': '0', 'id': '8eba620d-3bc6-0798-8765-e154561683a3', 'detail-type': 'EC2 Instance-launch Lifecycle Action', 'source': 'aws.autoscaling', 'account': '174570359254', 'time': '2021-03-02T20:40:54Z', 'region': 'us-west-2', 'resources': ['arn:aws:autoscaling:us-west-2:174570359254:autoScalingGroup:5b64870a-2427-4c84-8b13-1e12b4a0a28f:autoScalingGroupName/Example Auto Scaling Group'], 'detail': {'LifecycleActionToken': 'a756db24-25a2-45ee-b3fd-f69187545064', 'AutoScalingGroupName': 'Example Auto Scaling Group', 'LifecycleHookName': 'app-install-hook', 'EC2InstanceId': 'i-08bb85942547fea52', 'LifecycleTransition': 'autoscaling:EC2_INSTANCE_LAUNCHING', 'Origin': 'EC2', 'Destination': 'AutoScalingGroup'}}
```

Example Warm Pool Launch Event
```
[INFO]	2021-03-02T20:43:39.375Z	23bd0ed7-8b6a-4503-a7a6-c7f4c39c5179	{'version': '0', 'id': 'ed9fa7e5-d2cc-57c1-0161-0e2cda690e15', 'detail-type': 'EC2 Instance-launch Lifecycle Action', 'source': 'aws.autoscaling', 'account': '174570359254', 'time': '2021-03-02T20:43:39Z', 'region': 'us-west-2', 'resources': ['arn:aws:autoscaling:us-west-2:174570359254:autoScalingGroup:5b64870a-2427-4c84-8b13-1e12b4a0a28f:autoScalingGroupName/Example Auto Scaling Group'], 'detail': {'LifecycleActionToken': '247c983b-8f19-408d-894c-7c065ba40405', 'AutoScalingGroupName': 'Example Auto Scaling Group', 'LifecycleHookName': 'app-install-hook', 'EC2InstanceId': 'i-098eadadb4312906e', 'LifecycleTransition': 'autoscaling:EC2_INSTANCE_LAUNCHING', 'Origin': 'EC2', 'Destination': 'WarmPool'}}
```

Example Launch From Warm Pool
```
[INFO]	2021-03-02T20:46:22.633Z	913ca024-3739-46b2-9008-967abe7aabd5	{'version': '0', 'id': '22c76915-84ee-a131-7f2e-f1bad99180d8', 'detail-type': 'EC2 Instance-launch Lifecycle Action', 'source': 'aws.autoscaling', 'account': '174570359254', 'time': '2021-03-02T20:46:22Z', 'region': 'us-west-2', 'resources': ['arn:aws:autoscaling:us-west-2:174570359254:autoScalingGroup:5b64870a-2427-4c84-8b13-1e12b4a0a28f:autoScalingGroupName/Example Auto Scaling Group'], 'detail': {'LifecycleActionToken': 'eea5ce6e-5b75-4f67-bf78-af0cb3dd75b6', 'AutoScalingGroupName': 'Example Auto Scaling Group', 'LifecycleHookName': 'app-install-hook', 'EC2InstanceId': 'i-098eadadb4312906e', 'LifecycleTransition': 'autoscaling:EC2_INSTANCE_LAUNCHING', 'Origin': 'WarmPool', 'Destination': 'AutoScalingGroup'}}
```