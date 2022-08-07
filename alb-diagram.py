import boto3
import pprint
import sys
import json
from diagrams import Cluster, Diagram
from diagrams.aws.compute import EC2
from diagrams.aws.network import ELB

global alblist
alblist=[]


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
    # print(result)
    return result

def describelbs():
    lbs = elb.describe_load_balancers(PageSize=400)
    for lb in lbs["LoadBalancers"]:
        # print("\n"*2)
        # print ("-"*6)
        lbjson={}
        lbjson['Name']=lb["LoadBalancerName"]
        lbjson['Type']=lb["Type"]
        lbjson['TG']=gettargetgrouparns(lb["LoadBalancerArn"])
        lbjson['TGData']=[]
        # print("Name:",lb["LoadBalancerName"])
        # print("Type:",lb["Type"])
        # print("TargetGroups:",gettargetgroups(lb["LoadBalancerArn"]))
        
        # instancelist=[]
        
        TGLIST=[]
        for tgs in lbjson['TG']:
            TGD={}
            TGD['Name']=tgs.split("/")[1]
            tgh=gettargethealth(tgs)
            # print("tgh",tgh)
            if len(tgh) > 0:
                # instancelist.append(tgh)
                TGD['Instances']=tgh
                # lbjson['TG'].append=tgh
            else:
                TGD['Instances']=""
            print("TGD here",TGD)
            TGLIST.append(TGD)
            print("TGLIST",TGLIST)
            
        lbjson['TGData'] = TGLIST
        print("result")
        print(json.dumps(lbjson))    

        

        with Diagram(profile+"_ALB_"+lbjson['Name'],show=False):
            if lbjson['Type'] == "application":
                lb = ELB(lbjson['Name'])
                for targetgroup in lbjson['TGData']:
                    print("TGName",targetgroup['Name'])

                    for instance in targetgroup['Instances']:
                        instance_group=[]
                        with Cluster(targetgroup['Name']):
                            instance_group.append(EC2(instance['Name']))
                            lb >> instance_group
                print(instance_group)
            
            if lbjson['Type'] == "network":
                lb = ELB(lbjson['Name'])
                for targetgroup in lbjson['TGData']:
                    print("TGName",targetgroup['Name'])

                    for instance in targetgroup['Instances']:
                        instance_group=[]
                        with Cluster(targetgroup['Name']):
                            instance_group.append(ELB(instance['Target']['Id'].split("/")[2]))
                            lb >> instance_group
                print(instance_group)
            
        

        

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
    elb = session.client('elbv2')
    ec2 = session.client('ec2')
    describelbs()