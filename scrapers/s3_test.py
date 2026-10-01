import boto3
from botocore.config import Config


s3 = boto3.client(
    "s3",
    endpoint_url="http://localhost:9090",
    aws_access_key_id="test",
    aws_secret_access_key="test",
    region_name="us-east-1",
    config=Config(request_checksum_calculation="when_required"),

)

# s3.create_bucket(Bucket="tender-raw") 
try:
    s3.create_bucket(Bucket="tender-raw")
except s3.exceptions.BucketAlreadyOwnedByYou:
    pass



# print([b["Name"] for b in s3.list_buckets()["Buckets"]])



s3.upload_file("tenders.jsonl","tender-raw","raw/2026-10-01/tenders.jsonl")

for obj in s3.list_objects_v2(Bucket="tender-raw").get("Contents",[]):
    print(obj["Key"], obj["Size"])
