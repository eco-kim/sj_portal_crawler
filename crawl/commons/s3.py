import boto3
from config import s3
import json

def s3Client():
    return boto3.client('s3',aws_access_key_id=s3['accesskey'], aws_secret_access_key=s3['secretkey'])

def s3Upload(rst, category_id, num):
    s3 = s3Client()
    fname = f'category_{str(category_id).zfill(5)}_{str(num).zfill(4)}.json'
    temp = {'category_id':category_id,
            'values':rst}
    temp = bytes(json.dumps(temp).encode('utf-8'))
    s3.put_object(
            Bucket=s3['bucket_info'],
            Key=fname,
            Body=temp)
    s3.close()