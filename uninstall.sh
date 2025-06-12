 sudo apt --fix-broken install
 # sudo apt get remove --purge openssh-server -y
 sudo apt-get remove --purge vim -y
 sudo apt-get remove --purge plocate -y
 sudo apt-get remove --purge findutils -y
#  sudo apt-get remove --purge tigervnc-standalone-server -y
#  sudo apt-get remove --purge tigervnc-viewer -y
 sudo apt-get remove --purge docker-compose -y
 sudo apt-get remove --purge net-tools -y
 sudo apt-get remove --purge selinux-utils -y
 sudo apt-get remove --purge gcc -y
#  sudo apt-get remove --purge xrdp -y
 sudo apt-get remove --purge minicom -y
 sudo apt-get remove --purge screen -y
 sudo apt-get remove --purge dos2unix -y
 sudo apt-get remove --purge lm-sensors -y
 sudo apt-get remove --purge google-chrome-stable -y
# sudo apt-get remove python3 -y
webserver_container="webserver"
postgres_container="postgres"
# node_container="node-service"

# Get the image ID associated with the container
webserver_image=$(docker inspect --format='{{.Image}}' $webserver_container)

# Stop the container
docker stop $webserver_container

# Delete the container
docker rm $webserver_container


# Get the image ID associated with the container
postgres_image=$(docker inspect --format='{{.Image}}' $postgres_container)

# Remove the corresponding image
docker rmi $webserver_image

# Stop the container
docker stop $postgres_container

# Delete the container
docker rm $postgres_container


# Remove the corresponding image
docker rmi $postgres_image

# # Stop the container
# docker stop $node_container

# # Delete the container
# docker rm $node_container

# # Get the image ID associated with the container
# node_image=$(docker inspect --format='{{.Image}}' $node_container)

# # Remove the corresponding image
# docker rmi $node_image

for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc; do sudo apt-get remove $pkg; done