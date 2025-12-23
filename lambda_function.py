import json
import boto3
import os
import uuid
from datetime import datetime

# Initialize clients
dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')

# Get environment variables
TABLE_NAME = os.environ['TABLE_NAME']
TOPIC_ARN = os.environ['TOPIC_ARN']

def analyze_sentiment_local(text):
    """
    A simple rule-based sentiment analyzer.
    Returns: 'POSITIVE' or 'NEGATIVE' and a confidence score.
    """
    negative_words = ["trash", "hate", "terrible", "worst", "awful", "bad", "broken", "sucks", "fail"]
    text_lower = text.lower()
    
    # Count how many negative words appear
    hit_count = sum(1 for word in negative_words if word in text_lower)
    
    if hit_count > 0:
        # If we found bad words, it's NEGATIVE.
        # Confidence increases with more bad words (Simple Logic)
        confidence = 0.7 + (0.05 * hit_count)
        return 'NEGATIVE', min(confidence, 0.99) # Cap at 99%
    else:
        # Default to POSITIVE
        return 'POSITIVE', 0.9

def lambda_handler(event, context):
    try:
        # 1. Parse Input
        if 'body' in event:
            body = json.loads(event['body'])
            text = body.get('text', '')
        else:
            text = event.get('text', '')

        if not text:
            return {'statusCode': 400, 'body': json.dumps('No text provided')}

        # 2. Analyze (USING OUR CUSTOM LOCAL FUNCTION)
        sentiment, score = analyze_sentiment_local(text)

        # 3. Store in DynamoDB
        table = dynamodb.Table(TABLE_NAME)
        record_id = str(uuid.uuid4())
        
        item = {
            'ReviewID': record_id,
            'Text': text,
            'Sentiment': sentiment,
            'Confidence': str(score),
            'Timestamp': datetime.now().isoformat()
        }
        table.put_item(Item=item)

        # 4. Alert if Negative
        if sentiment == 'NEGATIVE':
            sns.publish(
                TopicArn=TOPIC_ARN,
                Message=f"ALARM: Negative Review Detected!\n\nText: '{text}'\nConfidence: {score:.2f}",
                Subject="VibeCheck: Negative Alert"
            )

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Analysis Complete (Local Mode)',
                'sentiment': sentiment,
                'id': record_id
            })
        }

    except Exception as e:
        print(f"Error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Internal Server Error: {str(e)}")
        }