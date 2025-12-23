import boto3
import json
from config import FUNCTION_NAME, REGION

def test_vibe_check(text):
    client = boto3.client('lambda', region_name=REGION)
    
    # Prepare the data
    payload = {'text': text}
    
    print(f"\nSending to Cloud: '{text}'")
    
    # Invoke the Lambda function
    response = client.invoke(
        FunctionName=FUNCTION_NAME,
        InvocationType='RequestResponse',
        Payload=json.dumps(payload)
    )
    
    # Read the response
    response_payload = json.loads(response['Payload'].read())
    
    # Pretty print the result
    print(f"AI Analysis: {json.dumps(response_payload, indent=2)}")

if __name__ == "__main__":
    # Test 1: Positive Vibe
    test_vibe_check("I absolutely love this service! It is the best thing ever.")
    
    # Test 2: Negative Vibe (⚠️ THIS SHOULD TRIGGER AN EMAIL)
    test_vibe_check("This product is trash. I hate it. It never works.")