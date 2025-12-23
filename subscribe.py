import boto3
from config import SNS_TOPIC_ARN, REGION

# --- PUT YOUR EMAIL HERE ---
MY_EMAIL = "Tanisha.connect.in@gmail.com"  # <--- Verify this is correct

def subscribe_email():
    if not MY_EMAIL or "@" not in MY_EMAIL:
        print("Error: Please put your valid email in the script code first!")
        return

    sns = boto3.client('sns', region_name=REGION)
    
    print(f"Subscribing '{MY_EMAIL}' to the Alarm System...")
    
    try:
        sns.subscribe(
            TopicArn=SNS_TOPIC_ARN,
            Protocol='email',
            Endpoint=MY_EMAIL
        )
        print("Request sent successfully!")
        print("\n⚠️  ACTION REQUIRED: ⚠️")
        print("1. Go to your Gmail inbox: Tanisha.connect.in@gmail.com")
        print("2. Look for an email from 'AWS Notifications'.")
        print("3. Click the 'Confirm subscription' link.")
        print("   (If you don't do this, you will NEVER get the alerts!)")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    subscribe_email()