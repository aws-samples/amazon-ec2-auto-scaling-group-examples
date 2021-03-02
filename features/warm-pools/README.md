# Warm Pools

## Prerequisites

Deploy CF template
```

```

Install CLI Utilities

```
brew install jq
brew install dateutils
```

## Test Scaling Speed

### Increase Desired Capacity
```
aws autoscaling set-desired-capacity --auto-scaling-group-name myEC2Workshop --desired-capacity 1
```

### Measure Launch Speed
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

## Configure Warm Pool
```
aws autoscaling-wp put-warm-pool --auto-scaling-group-name "Example Auto Scaling Group" --pool-state Stopped --region us-west-2 --min-size 2
```

```
aws autoscaling-wp describe-warm-pool --auto-scaling-group-name "Example Auto Scaling Group" --region us-west-2
```

## Retest Scaling Speed

### Increase Desired Capacity
```
aws autoscaling set-desired-capacity --auto-scaling-group-name myEC2Workshop --desired-capacity 2
```

### Measure Launch Speed
```
activities=$(aws autoscaling describe-scaling-activities --auto-scaling-group-name myEC2Workshop)
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

## Cleanup

