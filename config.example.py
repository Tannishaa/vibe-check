# config.py
REGION = "ap-south-1"
FUNCTION_NAME = "VibeCheck_Analyzer"

# Enter your AWS Resource ARNs here
SNS_TOPIC_ARN = "arn:aws:sns:ap-south-1:123456789012:VibeCheck_Alerts"
IAM_ROLE_ARN = "arn:aws:iam::123456789012:role/VibeCheck_Lambda_Role"
TABLE_NAME = "VibeCheck_Sentiment_Data"