import boto3
import pprint
region_name = "us-east-1"
profile = "prod"
session = boto3.session.Session(profile_name=profile)
elb = session.client('elbv2')
ec2 = session.client('ec2')

# paginator = elb.get_paginator('describe_load_balancers')
# for response in paginator.paginate():
#     pprint.pprint(response, width=1)


def gettargetgroups(arn):
    tgs=elb.describe_target_groups(LoadBalancerArn=arn)
    tgstring=[]
    for tg in tgs["TargetGroups"]:
        tgstring.append(tg["TargetGroupName"])
    return tgstring

def gettargetgrouparns(arn):
    tgs=elb.describe_target_groups(LoadBalancerArn=arn)
    tgarns=[]
    for tg in tgs["TargetGroups"]:
        tgarns.append(tg["TargetGroupArn"])
    return tgarns

# def getinstancenames(instanceids):
#     # print ("what is",type(instanceid))
#     instances=ec2.describe_instances(InstanceIds=instanceids)
#     for instance in instances["Reservations"]:
#         for inst in instance["Instances"]:
#             for tag in inst["Tags"]:
#                 if tag['Key'] == 'Name':
#                     return (tag['Value'])

def getinstancename(instanceid):
    instances=ec2.describe_instances(Filters=[
        {
            'Name': 'instance-id',
            'Values': [
                instanceid
            ]
        },
    ],)
    for instance in instances["Reservations"]:
        for inst in instance["Instances"]:
            for tag in inst["Tags"]:
                if tag['Key'] == 'Name':
                    return (tag['Value'])

    
def gettargethealth(arn):
    inss=elb.describe_target_health(TargetGroupArn=arn)
    instanceids=[]
    for ins in inss["TargetHealthDescriptions"]:
        ins["Name"]=getinstancename(ins['Target']['Id'])
        instanceids.append(ins['Target']['Id'])
        print (ins)
    # getinstancenames(instanceids)



lbs = elb.describe_load_balancers(PageSize=400)


for lb in lbs["LoadBalancers"]:
    print("\n"*2)
    print ("-"*6)
    print("Name:",lb["LoadBalancerName"])
    print("Type:",lb["Type"])
    print("Arn:",lb["LoadBalancerArn"])
    print("TargetGroups:",str(gettargetgroups(lb["LoadBalancerArn"])))

    for tgs in gettargetgrouparns(lb["LoadBalancerArn"]):
        gettargethealth(tgs)
    

