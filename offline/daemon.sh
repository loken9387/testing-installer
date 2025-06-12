#!/bin/bash
cat << EOF > /etc/docker/daemon.json
{
"mtu": 9216,
"insecure-registries": ["docker.bh.local","docker.dev.bh.local","docker.ci.bh.local"]
}
EOF
