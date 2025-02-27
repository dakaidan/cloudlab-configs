#!/bin/bash

set -e

if [ -f /local/complete_grow ]; then
    echo "Already completed, skipping"
    exit 0
fi

apt-get update
apt-get install -y cloud-guest-utils

ROOT_PART=$(findmnt / -o source -n | grep -o '[0-9]*$')
ROOT_DISK=/dev/"$(lsblk -no PKNAME "$(findmnt -no SOURCE /)")"

growpart "$ROOT_DISK" "$ROOT_PART"
resize2fs "$(findmnt / -no SOURCE)"

touch /local/complete_grow
