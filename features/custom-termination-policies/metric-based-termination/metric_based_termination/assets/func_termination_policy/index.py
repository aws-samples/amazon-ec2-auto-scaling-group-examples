import boto3
import datetime
import os

# Available metrics: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/viewing_metrics_with_cloudwatch.html

METRIC_NAME = os.getenv('METRIC_NAME')                      # Metric of which to retrieve data
METRIC_THRESHOLD = float(os.getenv('METRIC_THRESHOLD'))     # Value below which an instance is considered idle
METRIC_STAT = os.getenv('METRIC_STAT')                      # Statistic to use when retrieving CloudWatch metric data
METRIC_TIME_WINDOW_IN_MINUTES = int(                        # Time window for retrieving CloudWatch metric data
    os.getenv('METRIC_TIME_WINDOW_IN_MINUTES')
)

METRICS = [
    METRIC_NAME
]


def generate_time_window():
    """Generates a start time, end time and period for retrieving CloudWatch metrics
    """

    end_time = datetime.datetime.now()
    start_time = end_time - datetime.timedelta(minutes=METRIC_TIME_WINDOW_IN_MINUTES)

    # Calculate the number of seconds in the time widow and use it as period to retrieve only one sample
    period = int((end_time - start_time).total_seconds())

    return start_time, end_time, period


def get_metric_data(instances, start_time, end_time, period):
    """Retrieves CloudWatch metric data

    Keyword arguments:
    instances -- list with instance information
    start_time -- time stamp that determines the first data point to return
    end_time -- time stamp that determines the last data point to return
    period -- the granularity of the returned data points
    """

    client = boto3.client('cloudwatch')
    paginator = client.get_paginator('get_metric_data')

    # Hold the metrics for each instance in the form of:
    # + instanceId1
    #   + metricName1: 0
    #   + metricName2: 0
    # ...
    metric_data = {instance['InstanceId']: {metric_name: 0 for metric_name in METRICS} for instance in instances}

    # List that contains one entry per instance and metric used to retrieve CloudWatch metric data
    metric_data_queries = [
        {
            'Id': '{}{}'.format(instance['InstanceId'].replace('-', '_'), metric_name),
            'MetricStat': {
                'Metric': {
                    'Namespace': 'AWS/EC2',
                    'MetricName': metric_name,
                    'Dimensions': [
                        {
                            'Name': 'InstanceId',
                            'Value': instance['InstanceId']
                        }
                    ]
                },
                'Stat': METRIC_STAT,
                'Period': period
            },
            'ReturnData': True,
            'Label': '{}_{}'.format(instance['InstanceId'], metric_name)
        } for instance in instances for metric_name in METRICS
    ]

    response = paginator.paginate(
        MetricDataQueries=metric_data_queries,
        StartTime=start_time,
        EndTime=end_time
    )

    # Process the retrieved metrics and add them to the metric_data dictionary
    for page in response:
        for result in page['MetricDataResults']:
            instance_id = result['Label'].split('_')[0]
            metric_name = result['Label'].split('_')[1]

            if result['Values']:
                metric_data[instance_id][metric_name] = result['Values'][0]

            # Update the list of instances to include the retrieved metrics
            for instance in instances:
                if instance['InstanceId'] == instance_id:
                    instance.update({'Metrics': metric_data[instance_id]})


def should_terminate_instance(instance, capacities):
    """Returns whether an instance should be selected for termination
    considering an even balancing across AZs

    Keyword arguments:
    instance -- dictionary with instance data
    capacities -- dictionary with the suggested number of instances to terminate per availability zone
    """

    return instance['Metrics'][METRIC_NAME] < METRIC_THRESHOLD and capacities[instance['AvailabilityZone']] > 0


def instances_sorting_func(instance):
    """Implements the instances sorting logic using CloudWatch metric data

    Keyword arguments:
    instance -- dictionary with instance data
    """

    return instance['Metrics'][METRIC_NAME]


def lambda_handler(event, context):
    # Generate a time window for retrieving CloudWatch metric data
    start_time, end_time, period = generate_time_window()

    print('Received instances: ', event['Instances'])

    # Build a dictionary with the form {AvailabilityZone: capacity}
    capacities = {capacity['AvailabilityZone']: capacity['Capacity'] for capacity in event['CapacityToTerminate']}
    instances = event['Instances']
    instances_to_terminate = []

    # Get CloudWatch metric data for every instance in the generated time window
    # This method will add a `Metrics` property to every dictionary in the instances variable
    get_metric_data(instances, start_time, end_time, period)

    # Sort the instances in ascending order by their metric values (idle instances first)
    instances.sort(key=instances_sorting_func)

    # Select instances for termination using capacity information and the retrieved CloudWatch metric data
    for instance in instances:
        if should_terminate_instance(instance, capacities):
            instances_to_terminate.append(instance['InstanceId'])
            capacities[instance['AvailabilityZone']] -= 1

    print('Selected instances: {}'.format(', '.join(instances_to_terminate)))

    return {
        'InstanceIDs': instances_to_terminate
    }
