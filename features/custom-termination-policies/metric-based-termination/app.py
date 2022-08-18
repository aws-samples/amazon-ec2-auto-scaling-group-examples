#!/usr/bin/env python3

import aws_cdk as cdk

from metric_based_termination.metric_based_termination_stack import MetricBasedTerminationStack


app = cdk.App()

MetricBasedTerminationStack(app, "MetricBasedTerminationStack")

app.synth()
