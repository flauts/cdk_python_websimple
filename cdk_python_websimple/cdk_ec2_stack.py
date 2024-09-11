from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_s3 as s3,
    aws_iam as iam,
    CfnOutput,
)
from constructs import Construct

class CdkEc2Stack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Use existing VPC
        vpc = ec2.Vpc.from_lookup(
            self, 'vpc',
            vpc_id='vpc-00efc54137e6a9ef2'
        )

        # Use existing bucket
        existing_bucket_name = "cf-templates-iw9mos24h2jo-us-east-1"
        bucket = s3.Bucket.from_bucket_name(self, "ExistingBucket", existing_bucket_name)

        # Use existing security group
        sec_group = ec2.SecurityGroup.from_security_group_id(
            self, 'launch-wizard-1', 'sg-0c77723568ab75889')

        # Use existing key pair
        key_pair = ec2.KeyPair.from_key_pair_name(self, "ExistingKeyPair", "vockey")

        # Use the LabRole
        lab_role = iam.Role.from_role_arn(self, "LabRole", "arn:aws:iam::172067734210:role/LabRole")

        # Create User Data Script
        user_data = ec2.UserData.for_linux()
        user_data.add_commands(
            "apt update",
            "apt install -y apache2 git",
            "git clone https://github.com/flauts/websimple.git /var/www/html/websimple"
        )

        # Create EC2 instance
        instance = ec2.Instance(
            self,
            "mv-cdk",
            instance_type=ec2.InstanceType("t2.micro"),
            machine_image=ec2.MachineImage.generic_linux({"us-east-1": "ami-0aa28dab1f2852040"}),
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            security_group=sec_group,
            key_pair=key_pair,
            user_data=user_data,
            role=lab_role,  # Use LabRole for the instance
        )

        # Output Instance ID and Public IP
        CfnOutput(self, "InstanceId", value=instance.instance_id)
        CfnOutput(self, "InstancePublicIP", value=instance.instance_public_ip)
        CfnOutput(self, "websimpleURL", value=f"http://{instance.instance_public_ip}/websimple")