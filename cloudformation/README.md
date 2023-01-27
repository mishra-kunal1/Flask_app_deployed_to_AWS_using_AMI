# infrastructure

export AWS_PROFILE=devuser

aws cloudformation create-stack --stack-name myvpcwithparam --template-body file://csye6225-infra.yaml --parameters ParameterKey=VpcCidrBlock,ParameterValue="11.0.0.0/16" ParameterKey=Subnet1,ParameterValue="11.0.0.0/24" ParameterKey=Subnet2,ParameterValue="11.0.1.0/24" ParameterKey=Subnet3,ParameterValue="11.0.2.0/24" --region us-west-2

aws cloudformation create-stack --parameters ParameterKey=imageId,ParameterValue=ami-06dfb20e4303a536a ParameterKey=Environment,ParameterValue=demo ParameterKey=KeyName,ParameterValue=aws-root ParameterKey=TTL,ParameterValue=2 --template-body file://csye6225-infra.yaml --region us-east-1 --capabilities CAPABILITY_NAMED_IAM --stack-name vpcroot


    aws cloudformation create-stack --parameters ParameterKey=imageId,ParameterValue=ami-06dfb20e4303a536a ParameterKey=KeyName,ParameterValue=aws-root ParameterKey=TTL,ParameterValue=2 --template-body file://csye6225-infra.yaml --region us-east-1 --capabilities CAPABILITY_NAMED_IAM --stack-name vpcroot 
