#!/bin/bash
# This script does the set up of the grafana server for you
# It installs docker, launches the container on port 3000 and executes a command inside the Grafana Docker container as the root user.
# It creates or overwrites the AWS credentials file at .aws/credentials inside the container.
# The credentials are dynamically injected from the host environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN).


# Ensure required AWS environment variables are set
if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ] || [ -z "$AWS_SESSION_TOKEN" ]; then
    echo "Error: AWS credentials (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN) are not set as environment variables."
    exit 1
fi

# Update and install Docker
sudo yum update -y
sudo yum install -y docker

# Start and enable Docker
sudo systemctl start docker
sudo systemctl enable docker

# Ensure $USER is set
if [ -z "$USER" ]; then
  export USER=$(whoami)
fi

# Give user permissions to run Docker without sudo
sudo usermod -aG docker $USER

# Check if the Grafana container exists
if [ $(sudo docker ps -a -q -f name=grafana-container | wc -l) -eq 0 ]; then
    # Run the Grafana container
    sudo docker run -d --name grafana-container -p 3000:3000 -v grafana-storage:/var/lib/grafana grafana/grafana
else
    # Start the existing Grafana container
    sudo docker start grafana-container
fi

# Overwrite the AWS credentials file in the container
sudo docker exec -it -u root grafana-container /bin/bash <<EOF
cat > .aws/credentials <<EOL
[default]
aws_access_key_id=$AWS_ACCESS_KEY_ID
aws_secret_access_key=$AWS_SECRET_ACCESS_KEY
aws_session_token=$AWS_SESSION_TOKEN
EOL
EOF
