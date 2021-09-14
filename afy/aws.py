import boto3
import random
import time
import yaml

client = boto3.client("ec2")

tag_value = 'avatarify' +  str(random.randint(0,10000))

def start_remote():
    
    print("daveisgay")
    with open('config.yaml', 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    print(config)

    run_instances_response = client.run_instances(
    ImageId=config['image_id'],
    InstanceType=config['instance_type'],
    MinCount=1,
    MaxCount=1,
    UserData='#!/bin/bash -v\ncd /home/ubuntu/avatarify\nbash run.sh --docker --is-worker &\n',
    NetworkInterfaces=[{'AssociatePublicIpAddress': True, 'DeviceIndex':0, 'SubnetId': config['subnet_id'], 'Groups':[config['security_group']]}],
    TagSpecifications=[
        {
            'ResourceType': 'instance',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': tag_value
                }
            ]
        },
    ])

    # Sleep until associated public dns
    time.sleep(2)

    describe_instances_response = client.describe_instances(
        Filters=[
            {
                'Name': 'tag:Name',
                'Values': [
                    tag_value,
                ]
            },
        ]
    )

    dns_name = describe_instances_response['Reservations'][0]['Instances'][0]['NetworkInterfaces'][0]['Association']['PublicDnsName']
    instance_id = run_instances_response['Instances'][0]['InstanceId']

    d = dict()
    d['in_addr'] = "tcp://" + dns_name + ":5557"
    d['out_addr'] = "tcp://" + dns_name + ":5558"
    d['public_dns'] = dns_name
    d['instance_id'] = instance_id

    return d

def terminate_remote(instance_id):
    client.terminate_instances(InstanceIds=[instance_id])