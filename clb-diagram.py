import boto3
import pprint
import json
import sys
from diagrams import Cluster, Diagram
from diagrams.aws.compute import EC2
from diagrams.aws.network import ELB


def getinstancename(instanceid):
    instances=ec2.describe_instances(Filters=[
        {
            'Name': 'instance-id',
            'Values': [
                instanceid
            ]
        },
    ],)

    resultset = {}    
    for instance in instances["Reservations"]:
        for inst in instance["Instances"]:
            resultset["State"]=inst["State"]["Name"]    
            for tag in inst["Tags"]:
                if tag['Key'] == 'Name':
                    resultset["Name"]=tag['Value']
    # print (resultset)  
    return resultset
             

def getinstancehealth(lbname,instanceid):
    instancestate=elb.describe_instance_health(
            LoadBalancerName=lbname,
            Instances = [{
                'InstanceId' : instanceid
            }]
            )
    
    return instancestate['InstanceStates'][0]['State']

def describelbs():
    
    lbs = elb.describe_load_balancers(PageSize=400)

    for lb in lbs["LoadBalancerDescriptions"]:
        lbjson={}
        lbjson['Name']=lb["LoadBalancerName"]
        lbjson['HealthCheck']=lb["HealthCheck"]
        lbjson['Instances']=[]

        if len(lb["Instances"]) > 0:
            InstanceList=[]
            for instance in lb["Instances"]:
                instance.update(getinstancename(instance["InstanceId"]))
                instance['Health']=getinstancehealth(lb["LoadBalancerName"], instance["InstanceId"])
                InstanceList.append(instance)
            
            lbjson['Instances']=InstanceList

        print("\n",json.dumps(lbjson, indent=4, sort_keys=True))

        with Diagram(profile+"_CLB_"+lbjson['Name'],show=False):
                lb = ELB(lbjson['Name'])
                instance_group=[]
                for instance in lbjson['Instances']:
                    instance_group.append(EC2(instance['Name']))
                lb >> instance_group

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("-- Region Name and the Profile name is mandatory --")
        print(" Syntax: python3 ",sys.argv[0]," us-east-1 default")
        exit()
    region_name = sys.argv[1]
    profile = sys.argv[2]
    print("profilename selected:",profile)
    print("regionname selected: ",region_name)
    session = boto3.session.Session(profile_name=profile)
    elb = session.client('elb')
    ec2 = session.client('ec2')
    describelbs()