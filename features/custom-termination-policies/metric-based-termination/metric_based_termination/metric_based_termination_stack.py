from aws_cdk import (
    CfnParameter,
    Duration,
    Stack,
    aws_ec2 as ec2,
    aws_ssm as ssm,
    aws_lambda as _lambda,
    aws_iam as iam,
    aws_autoscaling as asg,
    Fn
)
from constructs import Construct

import yaml


class MetricBasedTerminationStack(Stack):
    def _create_vpc(self):
        return ec2.Vpc(self, "Vpc",
                       subnet_configuration=[
                           ec2.SubnetConfiguration(
                               cidr_mask=24,
                               name="StressSubnetConfiguration",
                               subnet_type=ec2.SubnetType.PUBLIC
                           )
                       ])

    def _create_launch_template(self, vpc):
        # IAM role to associate with the instance profile that is used by instances
        instance_role = iam.Role(self, 'StressInstanceRole',
                                 assumed_by=iam.ServicePrincipal('ec2.amazonaws.com'),
                                 role_name='StressInstanceRole',
                                 managed_policies=[
                                     iam.ManagedPolicy.from_managed_policy_arn(
                                         self,
                                         'AmazonSSMManagedInstanceCore',
                                         'arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore'
                                     )
                                 ])

        # Security group where the instances will be placed
        security_group = ec2.SecurityGroup(self, 'SecurityGroup',
                                           security_group_name="StressSecurityGroup",
                                           allow_all_outbound=True,
                                           vpc=vpc)

        # Read the UserData from the txt file
        with open('metric_based_termination/assets/user_data.txt') as fd:
            user_data = fd.read()

        return ec2.LaunchTemplate(self, 'LaunchTemplate',
                                  launch_template_name="StressLaunchTemplate",
                                  security_group=security_group,
                                  user_data=ec2.UserData.custom(user_data),
                                  role=instance_role,
                                  machine_image=ec2.MachineImage.latest_amazon_linux())

    def _create_ssm_document(self):
        # Read the document data from the yaml file
        with open('metric_based_termination/assets/stress_document.yml') as fd:
            content = fd.read()

        return ssm.CfnDocument(self, "Document",
                               name='StressDocument',
                               document_type='Command',
                               content=yaml.safe_load(content))

    def _create_ssm_association(self, document, launch_template):
        ssm.CfnAssociation(self, 'DocumentAssociation',
                           name=document.name,
                           association_name='StressAssociation',
                           targets=[
                               ssm.CfnAssociation.TargetProperty(key='tag:aws:ec2launchtemplate:id',
                                                                 values=[
                                                                     launch_template.launch_template_id
                                                                 ])
                           ])

    def _create_termination_function(self):
        # Create the Lambda function that implements the custom termination policy
        function = _lambda.Function(self, 'Function',
                                    runtime=_lambda.Runtime.PYTHON_3_9,
                                    function_name='customTerminationPolicy',
                                    code=_lambda.Code.from_asset('metric_based_termination/assets/func_termination_policy'),
                                    timeout=Duration.minutes(5),
                                    handler='index.lambda_handler',
                                    environment={'METRIC_NAME': 'CPUUtilization',
                                                 'METRIC_THRESHOLD': '3',
                                                 'METRIC_STAT': 'Minimum',
                                                 'METRIC_TIME_WINDOW_IN_MINUTES': '5'}
                                    )

        # Grant the function permission to retrieve CloudWatch metrics
        function.add_to_role_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            resources=['*'],
            actions=['cloudwatch:GetMetricData',
                     'logs:CreateLogGroup',
                     'logs:CreateLogStream',
                     'logs:PutLogEvents']
        ))

        # Grant the function permission to update the ASG
        function.add_to_role_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=['autoscaling:UpdateAutoScalingGroup'],
            resources=['*']
        ))

        # Grant the EC2 ASG service-linked role permission to execute the function
        principal = iam.ServicePrincipal(Fn.sub("arn:aws:iam::${AWS::AccountId}:role/aws-service-role/autoscaling.amazonaws.com/AWSServiceRoleForAutoScaling"))
        function.grant_invoke(principal)

        return function

    def _create_asg(self, launch_template, termination_function, vpc):
        # Define ASG configuration parameters
        asg_name = CfnParameter(self, "ASGName", type='String', description="ASG Name", default='Example ASG')
        min_capacity = CfnParameter(self, "MinCapacity", type='Number', description="Minimum capacity", default='1')
        max_capacity = CfnParameter(self, "MaxCapacity", type='Number', description="Maximum capacity", default='6')
        desired_cap = CfnParameter(self, "DesiredCapacity", type='Number', description="Desired capacity", default='2')

        # Override the configuration of the Launch Template using Attribute Based Selection (ABS)
        launch_template_property = asg.CfnAutoScalingGroup.LaunchTemplateProperty(
            launch_template_specification=asg.CfnAutoScalingGroup.LaunchTemplateSpecificationProperty(
                launch_template_id=launch_template.launch_template_id,
                version=launch_template.version_number
            ),
            overrides=[asg.CfnAutoScalingGroup.LaunchTemplateOverridesProperty(
                instance_requirements=asg.CfnAutoScalingGroup.InstanceRequirementsProperty(
                    memory_mib=asg.CfnAutoScalingGroup.MemoryMiBRequestProperty(
                        max=8192,
                        min=0
                    ),
                    v_cpu_count=asg.CfnAutoScalingGroup.VCpuCountRequestProperty(
                        max=6,
                        min=1
                    )
                )
            )]
        )

        # Create the ASG
        l1_asg = asg.CfnAutoScalingGroup(
            self, 'ASG',
            auto_scaling_group_name=asg_name.value_as_string,
            max_size=max_capacity.value_as_string,
            min_size=min_capacity.value_as_string,
            desired_capacity=desired_cap.value_as_string,
            capacity_rebalance=True,
            termination_policies=[termination_function.function_arn],
            vpc_zone_identifier=vpc.select_subnets().subnet_ids,
            mixed_instances_policy=asg.CfnAutoScalingGroup.MixedInstancesPolicyProperty(
                launch_template=launch_template_property,
                instances_distribution=asg.CfnAutoScalingGroup.InstancesDistributionProperty(
                    on_demand_allocation_strategy="lowest-price",
                    spot_allocation_strategy="capacity-optimized"
                )
            ))

        # Set a CPU based target tracking scaling policy for the ASG
        scaling_policy = asg.CfnScalingPolicy(
            self, 'ScalingPolicy',
            auto_scaling_group_name=l1_asg.auto_scaling_group_name,
            policy_type='TargetTrackingScaling',
            target_tracking_configuration=asg.CfnScalingPolicy.TargetTrackingConfigurationProperty(
                target_value=50,
                disable_scale_in=False,
                predefined_metric_specification=asg.CfnScalingPolicy.PredefinedMetricSpecificationProperty(
                    predefined_metric_type='ASGAverageCPUUtilization'
                )
            ))
        scaling_policy.node.add_dependency(l1_asg)

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create a VPC where new instances will be deployed and a Launch Template that uses it
        vpc = self._create_vpc()
        launch_template = self._create_launch_template(vpc)

        # Create the SSM document and associate it with the instances launched using the Launch Template
        document = self._create_ssm_document()
        self._create_ssm_association(document, launch_template)

        # Create the custom termination policy using a Lambda function and an ASG that uses it
        termination_function = self._create_termination_function()
        self._create_asg(launch_template, termination_function, vpc)
