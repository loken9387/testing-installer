username="xmmgr"

if [ -z "$username" ]; then
  echo "Usage: $0 <username>"
  exit 1
fi

usermod -aG sudo "$username"

if [ $? -eq 0 ]; then
  echo "User '$username' added to sudoers."
else
  echo "Failed to add user '$username' to sudoers."
fi