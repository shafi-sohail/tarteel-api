import re

ip_str = "https://tarteel-data.s3.amazonaws.com/media/29_51_3340224152.wav?AWSAccessKeyId=AKIAINDBU7YJPBEMUQHA&Signature=tpnEWgFDYAGKH8I3sWGEosAITBA%3D&Expires=1705752297"
op_str = re.sub('(\?.*)', '', ip_str)
print (op_str) 
