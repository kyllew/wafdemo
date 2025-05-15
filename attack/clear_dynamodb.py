import boto3
import time

def clear_dynamodb_table(table_name):
    """
    Clear all items from a DynamoDB table
    
    Args:
        table_name: Name of the DynamoDB table to clear
    """
    # Initialize DynamoDB client
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    
    # Get all items from the table
    print(f"Scanning table {table_name}...")
    scan = table.scan()
    items = scan['Items']
    
    # Continue scanning if there are more items
    while 'LastEvaluatedKey' in scan:
        scan = table.scan(ExclusiveStartKey=scan['LastEvaluatedKey'])
        items.extend(scan['Items'])
    
    # Delete items in batches
    with table.batch_writer() as batch:
        for item in items:
            print(f"Deleting item: {item['review_id']}")
            batch.delete_item(
                Key={
                    'review_id': item['review_id'],
                    'product_id': item['product_id']
                }
            )
    
    print(f"Successfully deleted {len(items)} items from {table_name}")

if __name__ == "__main__":
    table_name = "waf-demo-product-reviews-demo"
    print(f"Starting to clear table {table_name}")
    clear_dynamodb_table(table_name)
    print("Done!")