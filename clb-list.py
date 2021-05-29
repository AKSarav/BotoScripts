import boto3
import pprint
region_name = "us-east-1"
profile = "prod"
session = boto3.session.Session(profile_name=profile)
elb = session.client('elb')
ec2 = session.client('ec2')


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

lbs = elb.describe_load_balancers(PageSize=400)

for lb in lbs["LoadBalancerDescriptions"]:
    print("\n"*2)
    print ("-"*6)
    print("Name:",lb["LoadBalancerName"])
    print("HealthCheck:",lb["HealthCheck"])
    print("Instance Info:")
    if len(lb["Instances"]) > 0:
        for instance in lb["Instances"]:
            instance.update(getinstancename(instance["InstanceId"]))
            instance['Health']=getinstancehealth(lb["LoadBalancerName"], instance["InstanceId"])
            print (instance)
    else:
        print("Instance List is Empty, Or no Instance is mapped")
    