import boto3
import datetime
import os

# Values below which an instance is considered idle
CPU_PERCENTAGE_THRESHOLD = float(os.getenv('CPU_PERCENTAGE_THRESHOLD'))
NETWORK_OUT_BYTES = float(os.getenv('NETWORK_OUT_BYTES'))
NETWORK_IN_BYTES = float(os.getenv('NETWORK_IN_BYTES'))

# Statistic to use when retrieving CloudWatch metric data
METRIC_STAT = os.getenv('METRIC_STAT')

# Time window for retrieving CloudWatch metric data
METRIC_TIME_WINDOW_IN_MINUTES = int(os.getenv('METRIC_TIME_WINDOW_IN_MINUTES'))

# Metrics to retrieve from each instance
# #Available metrics: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/viewing_metrics_with_cloudwatch.html
METRICS = [
    'CPUUtilization',
    'NetworkOut',
    'NetworkIn'
]


def generate_time_window():
    """Generates a start time, end time and period for retriving CloudWatch metrics.
    """

    end_time = datetime.datetime.now()
    start_time = end_time - datetime.timedelta(minutes=METRIC_TIME_WINDOW_IN_MINUTES)

    # Calculate the number of seconds in the time widow and use it as period to retrieve only one sample
    period = int((end_time - start_time).total_seconds())

    return start_time, end_time, period


def get_metric_data(instances, start_time, end_time, period):
    """Retrieves CloudWatch metrics.

    Keyword arguments:
    instances -- list of instances of which to retrieve the metrics
    start_time -- time stamp that determines the first data point to return
    end_time -- time stamp that determines the last data point to return
    period -- the granularity of the returned data points
    """

    client = boto3.client('cloudwatch')
    paginator = client.get_paginator('get_metric_data')

    # Hold the metrics for each instance in the form of:
    # + instanceId1
    #   + metricName1: metricValue1
    #   + metricName2: metricValue2
    # ...
    metric_data = {instance_id: {metric_name: 0 for metric_name in METRICS} for instance_id in instances}

    # List that contains one entry per instance and metric
    metric_data_queries = [
        {
            'Id': '{}{}'.format(instance_id.replace('-', '_'), metric_name),
            'MetricStat': {
                'Metric': {
                    'Namespace': 'AWS/EC2',
                    'MetricName': metric_name,
                    'Dimensions': [
                        {
                            'Name': 'InstanceId',
                            'Value': instance_id
                        }
                    ]
                },
                'Stat': METRIC_STAT,
                'Period': period
            },
            'ReturnData': True,
            'Label': '{}_{}'.format(instance_id, metric_name)
        } for instance_id in instances for metric_name in METRICS
    ]

    response = paginator.paginate(
        MetricDataQueries=metric_data_queries,
        StartTime=start_time,
        EndTime=end_time
    )

    for page in response:
        for result in page['MetricDataResults']:
            instance_id = result['Label'].split('_')[0]
            metric_name = result['Label'].split('_')[1]

            if result['Values']:
                metric_data[instance_id][metric_name] = result['Values'][0]

    return metric_data


def should_terminate_instance(metrics):
    """Returns whether an instance should be selected for termination

    Keyword arguments:
    metrics -- dictionary with metrics
    """

    return metrics['CPUUtilization'] < CPU_PERCENTAGE_THRESHOLD and \
           metrics['NetworkOut'] < NETWORK_OUT_BYTES and \
           metrics['NetworkIn'] < NETWORK_IN_BYTES


def lambda_handler(event, context):
    # Generate a time window for retrieving CloudWatch metric data
    start_time, end_time, period = generate_time_window()

    # Extract instance IDs
    instances = [instance['InstanceId'] for instance in event['Instances']]
    print('Received instances: {}'.format(', '.join(instances)))

    # Get CloudWatch metric data for every instance in the generated time window
    metric_data = get_metric_data(instances, start_time, end_time, period)

    # Select instances for termination using the retrieved CloudWatch metric data
    instances = [instance_id for instance_id, metrics in metric_data.items() if should_terminate_instance(metrics)]
    print('Selected instances: {}'.format(', '.join(instances)))

    return {
        'InstanceIDs': instances
    }
