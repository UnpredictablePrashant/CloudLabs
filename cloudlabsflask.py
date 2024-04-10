import boto3
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/')
def index():
    return "Welcome to the lab infrastructure monitoring API!"

@app.route('/users')
def get_users():
    # Initialize boto3 clients
    iam_client = boto3.client('iam')
    ec2_client = boto3.client('ec2')

    # Fetch IAM users and their policies
    response = iam_client.list_users()
    users = []
    for user in response['Users']:
        user_details = {
            'username': user['UserName'],
            'arn': user['Arn'],
            'policies': []
        }

        # Fetch attached policies
        attached_policies_response = iam_client.list_attached_user_policies(UserName=user['UserName'])
        attached_policy_arns = [policy['PolicyArn'] for policy in attached_policies_response['AttachedPolicies']]
        user_details['policies'].extend(attached_policy_arns)

        # Fetch inline policies
        inline_policies_response = iam_client.list_user_policies(UserName=user['UserName'])
        inline_policy_names = inline_policies_response['PolicyNames']
        for policy_name in inline_policy_names:
            inline_policy_response = iam_client.get_user_policy(UserName=user['UserName'], PolicyName=policy_name)
            user_details['policies'].append(inline_policy_response['PolicyArn'])

        users.append(user_details)

    # Fetch EC2 instances with no tags
    ec2_instances = ec2_client.describe_instances()

    instances_with_no_tags = []
    for reservation in ec2_instances['Reservations']:
        for instance in reservation['Instances']:
            if 'Tags' not in instance:
                instances_with_no_tags.append(instance['InstanceId'])

    return jsonify({'users': users, 'instances_with_no_tags': instances_with_no_tags})

if __name__ == '__main__':
    app.run(debug=True)
