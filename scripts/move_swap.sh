#!/bin/bash

set -e

while [[ $# -gt 0 ]]; do
    case "$1" in
        --new-swap-size)
            NEW_SWAP_SIZE=$2
            shift 2
            ;;
        --swap-part)
            SWAP_PART=$2
            shift 2
            ;;
        --no-swap)
            NO_SWAP=true
            shift
            ;;
        *)
            echo "Unknown argument: $1"
            exit 1
            ;;
    esac
done


if [[ -z "$SWAP_PART" ]]; then
  SWAP_PART=$(lsblk -rno NAME,TYPE | awk '$2 == "part" {print "/dev/"$1}' | tail -n 1)
fi

if [[ -z "$SWAP_PART" ]]; then
    echo "No swap partition detected."
else
    if ! blkid "$SWAP_PART" | grep -q 'TYPE="swap"'; then
        echo "$SWAP_PART is NOT a swap partition."
        exit 1
    fi

    if [[ -z "$NEW_SWAP_SIZE" ]]; then
        NEW_SWAP_SIZE=$(lsblk -bno SIZE "$SWAP_PART")
        NEW_SWAP_SIZE=$((NEW_SWAP_SIZE / 1024 / 1024 / 1024))
    fi

    echo "Detected swap partition: $SWAP_PART"
    echo "Turning off swap on $SWAP_PART..."
    swapoff "$SWAP_PART"

    DISK=$(lsblk -no PKNAME "$SWAP_PART" | awk '{print "/dev/" $1}')
    PART_NUM=$(echo "$SWAP_PART" | grep -o '[0-9]*$')

    echo "Deleting swap partition $SWAP_PART..."
    parted -s "$DISK" rm "$PART_NUM"

    sed -i "\|^$SWAP_PART|d" /etc/fstab
fi

if [[ "$NO_SWAP" == "true" ]]; then
    exit 0
fi

echo "Creating new swap file of size $NEW_SWAP_SIZE GB..."
DISK_SIZE=$(lsblk -bno SIZE "$DISK" | grep -o '^[0-9]*' | awk '{print int($1/1024/1024)}')
SWAP_START=$((DISK_SIZE - (NEW_SWAP_SIZE * 1024)))
parted -s "$DISK" mkpart primary linux-swap "$SWAP_START"MiB 100%
SWAP_PART=$(lsblk -rno NAME,TYPE | awk '$2 == "part" {print "/dev/"$1}' | tail -n 1)
mkswap "$SWAP_PART"
swapon "$SWAP_PART"
echo "$SWAP_PART none swap defaults 0 0" >> /etc/fstab
echo "New swap partition created: $SWAP_PART"
