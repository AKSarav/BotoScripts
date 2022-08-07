import boto3
import pprint
import sys
import json

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
    # print("arn",arn)
    inss=elb.describe_target_health(TargetGroupArn=arn)
    instanceids=[]
    result=[]
    for ins in inss["TargetHealthDescriptions"]:
        ins["Name"]=getinstancename(ins['Target']['Id'])
        instanceids.append(ins['Target']['Id'])
        result.append(ins)
    return result

def describelbs():
    lbs = elb.describe_load_balancers(PageSize=400)
    for lb in lbs["LoadBalancers"]:
        lbjson={}
        lbjson['Name']=lb["LoadBalancerName"]
        lbjson['Type']=lb["Type"]
        lbjson['TG']=gettargetgrouparns(lb["LoadBalancerArn"])
        lbjson['TGData']=[]

        TGLIST=[]
        if len(lbjson["TG"]) > 0:
            for tgs in lbjson['TG']:
                TGD={}
                TGD['Name']=tgs.split("/")[1]
                tgh=gettargethealth(tgs)
                if len(tgh) > 0:
                    TGD['Instances']=tgh
                else:
                    TGD['Instances']=""
                TGLIST.append(TGD)
                
            lbjson['TGData'] = TGLIST
        
        print("\n",json.dumps(lbjson, indent=4, sort_keys=True))        

        

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("-- Region Name and the Profile name is mandatory --")
        print(" Syntax: python3 clb-list-json.py us-east-1 default")
        exit()
    region_name = sys.argv[1]
    profile = sys.argv[2]
    session = boto3.session.Session(profile_name=profile)
    elb = session.client('elbv2')
    ec2 = session.client('ec2')
    describelbs()