import boto3
import random
import time
import subprocess

client = boto3.client("ec2")

tag_value = 'avatarify' +  str(random.randint(0,10000))

def start_remote():
    
    print("daveisgay")

    run_instances_response = client.run_instances(
    ImageId='ami-0d42ecea54593b8de',
    InstanceType='g4dn.xlarge',
    MinCount=1,
    MaxCount=1,
    UserData='#!/bin/bash -v\ncd /home/ubuntu/avatarify\nbash run.sh --docker --is-worker &\n',
    NetworkInterfaces=[{'AssociatePublicIpAddress': True, 'DeviceIndex':0, 'SubnetId': 'subnet-0b9d05d227fc94298', 'Groups':['sg-0461794c3fc706e1d']}],
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
    # instance_id = run_instances_response['Reservations'][0]['Instances'][0]['InstanceId']

    d = dict()
    d['in_addr'] = "tcp://" + dns_name + ":5557"
    d['out_addr'] = "tcp://" + dns_name + ":5558"
    d['public_dns'] = dns_name
    # d['instance_id'] = instance_id

    return d

def terminate_remote():
    client.terminate_instances(InstanceIds=[instance_id])