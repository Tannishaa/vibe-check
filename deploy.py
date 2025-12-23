import boto3
import zipfile
import io
import time  # <--- NEW IMPORT
from config import REGION, FUNCTION_NAME, IAM_ROLE_ARN, SNS_TOPIC_ARN, TABLE_NAME

def deploy_function():
    print(f"🚀 Deploying '{FUNCTION_NAME}' to AWS Lambda...")

    # 1. Create a ZIP package
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.write('lambda_function.py')
    zip_buffer.seek(0)
    zipped_code = zip_buffer.read()

    client = boto3.client('lambda', region_name=REGION)

    try:
        # Try to create new function
        response = client.create_function(
            FunctionName=FUNCTION_NAME,
            Runtime='python3.13',
            Role=IAM_ROLE_ARN,
            Handler='lambda_function.lambda_handler',
            Code={'ZipFile': zipped_code},
            Timeout=10,
            Environment={
                'Variables': {
                    'TABLE_NAME': TABLE_NAME,
                    'TOPIC_ARN': SNS_TOPIC_ARN
                }
            }
        )
        print("✅ Function created successfully!")
    
    except client.exceptions.ResourceConflictException:
        print("⚠️ Function already exists. Updating code...")
        
        # Step A: Update the Code
        client.update_function_code(
            FunctionName=FUNCTION_NAME,
            ZipFile=zipped_code
        )
        print("   -> Code uploaded. Waiting for AWS to process...")
        
        # Step B: WAIT for AWS to release the lock (Crucial Step)
        time.sleep(5) 
        
        # Step C: Update Configuration (Env Vars)
        client.update_function_configuration(
            FunctionName=FUNCTION_NAME,
            Environment={
                'Variables': {
                    'TABLE_NAME': TABLE_NAME,
                    'TOPIC_ARN': SNS_TOPIC_ARN
                }
            }
        )
        print("✅ Function updated successfully!")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    deploy_function()