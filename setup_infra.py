import boto3
import json
import time

# --- CONFIGURATION ---
REGION = "ap-south-1"
TABLE_NAME = "VibeCheck_Sentiment_Data"
TOPIC_NAME = "VibeCheck_Alerts"
ROLE_NAME = "VibeCheck_Lambda_Role"

def create_resources():
    print("Initializing Cloud Infrastructure...")

    # 1. Create SNS Topic
    sns = boto3.client("sns", region_name=REGION)
    try:
        topic = sns.create_topic(Name=TOPIC_NAME)
        topic_arn = topic["TopicArn"]
        print(f"SNS Topic Created: {topic_arn}")
        # Note: You will need to manually subscribe your email to this ARN in the AWS Console.
    except Exception as e:
        print(f"SNS Error: {e}")
        return

    # 2. Create DynamoDB Table
    dynamodb = boto3.client("dynamodb", region_name=REGION)
    try:
        dynamodb.create_table(
            TableName=TABLE_NAME,
            KeySchema=[{'AttributeName': 'ReviewID', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'ReviewID', 'AttributeType': 'S'}],
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        )
        print(f"DynamoDB Table '{TABLE_NAME}' creating...")
        
        waiter = dynamodb.get_waiter('table_exists')
        waiter.wait(TableName=TABLE_NAME)
        print(f"Table '{TABLE_NAME}' is active.")
    except dynamodb.exceptions.ResourceInUseException:
        print(f"Table '{TABLE_NAME}' already exists.")

    # 3. Create IAM Role
    iam = boto3.client("iam", region_name=REGION)
    
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"Service": "lambda.amazonaws.com"},
            "Action": "sts:AssumeRole"
        }]
    }

    try:
        role = iam.create_role(
            RoleName=ROLE_NAME,
            AssumeRolePolicyDocument=json.dumps(trust_policy)
        )
        print(f"IAM Role '{ROLE_NAME}' created.")
    except iam.exceptions.EntityAlreadyExistsException:
        print(f"IAM Role '{ROLE_NAME}' already exists.")
        role = iam.get_role(RoleName=ROLE_NAME)

    # Attach AdministratorAccess (For development simplicity)
    iam.attach_role_policy(
        RoleName=ROLE_NAME,
        PolicyArn="arn:aws:iam::aws:policy/AdministratorAccess"
    )
    print("Permissions attached to Role.")
    
    print("\n--- INFRASTRUCTURE READY ---")
    print(f"SNS Topic ARN: {topic_arn}")
    print(f"IAM Role ARN:  {role['Role']['Arn']}")
    print("----------------------------")
    print("Save these ARNs.")

if __name__ == "__main__":
    create_resources()