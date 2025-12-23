import boto3
import time
from config import REGION, FUNCTION_NAME, IAM_ROLE_ARN

def setup_api_gateway():
    print(f"Setting up API Gateway for '{FUNCTION_NAME}'...")

    lambda_client = boto3.client('lambda', region_name=REGION)
    apigateway = boto3.client('apigatewayv2', region_name=REGION)

    # 1. Get the Lambda Function ARN (Address)
    try:
        response = lambda_client.get_function(FunctionName=FUNCTION_NAME)
        function_arn = response['Configuration']['FunctionArn']
    except Exception as e:
        print(f"Error: Could not find Lambda function. Did you deploy it? {e}")
        return

    # 2. Create the API (HTTP Protocol)
    print("Creating API...")
    api = apigateway.create_api(
        Name='VibeCheck_API',
        ProtocolType='HTTP',
        Target=function_arn 
    )
    api_id = api['ApiId']
    api_endpoint = api['ApiEndpoint']
    print(f"API Created. ID: {api_id}")

    # 3. Grant Permission (Allow API Gateway to invoke Lambda)
    # This is the "Security Badge" the API needs to talk to your function.
    try:
        lambda_client.add_permission(
            FunctionName=FUNCTION_NAME,
            StatementId='apigateway-invoke-permission',
            Action='lambda:InvokeFunction',
            Principal='apigateway.amazonaws.com',
            SourceArn=f"arn:aws:execute-api:{REGION}:{response['Configuration']['FunctionArn'].split(':')[4]}:{api_id}/*/*/analyze"
        )
        print("Permissions granted to API Gateway.")
    except lambda_client.exceptions.ResourceConflictException:
        print("Permissions already exist.")

    # 4. Define the Route (The URL path)
    # We want users to send POST requests to /analyze
    # Note: When creating an API with 'Target' above, AWS sets up a default route.
    # We will verify/create a specific route for clarity.
    
    # Create Integration
    integration = apigateway.create_integration(
        ApiId=api_id,
        IntegrationType='AWS_PROXY',
        IntegrationUri=function_arn,
        PayloadFormatVersion='2.0'
    )
    integration_id = integration['IntegrationId']

    # Create Route 'POST /analyze'
    apigateway.create_route(
        ApiId=api_id,
        RouteKey='POST /analyze',
        Target=f"integrations/{integration_id}"
    )
    print("Route 'POST /analyze' configured.")

    print("\n--------------------------------------------------")
    print("API IS LIVE")
    print(f"Base URL: {api_endpoint}")
    print(f"Test URL: {api_endpoint}/analyze")
    print("--------------------------------------------------")
    print("Save this Test URL!")

if __name__ == "__main__":
    setup_api_gateway()