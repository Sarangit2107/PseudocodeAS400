import paramiko
print('Hello World')
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(
    hostname="www.pub400.com",
    port="2222",
    username="NEERJAA",
    password="neerja12345",
    timeout=30
)
print("AS400 Connection successful!")
