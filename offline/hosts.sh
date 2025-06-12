#!/bin/bash
cat << EOF > /etc/hosts
127.0.0.1   localhost localhost.localdomain localhost4 localhost4.localdomain4
::1         localhost localhost.localdomain localhost6 localhost6.localdomain6

127.0.0.1 simlocal
127.0.0.1 simulator
127.0.0.1 controller
127.0.0.1 rfpseudohost
10.107.65.5 git.udev.local git.bh.local
10.107.65.13 docker.ci.bh.local
10.107.65.14 docker.bh.local
10.107.65.15 docker.dev.bh.local
10.107.65.16 builder

18.252.154.122 docker-dev.artifactory.parsons.us
10.107.65.27 repo.internal
10.107.65.27 inf-lg2-spw01.udev.internal
127.0.0.1 mb01.realm.trex.internal
10.107.65.2 ntp01.external-infrastructure.kepler.internal ntp
127.0.0.1 mb01.realm.kepler.internal
127.0.0.1 db01.realm.kepler.internal
EOF
