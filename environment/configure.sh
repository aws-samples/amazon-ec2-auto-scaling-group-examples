#!/bin/bash

set -euxo pipefail

ACCOUNT_ID=$(aws sts get-caller-identity --query 'Account' --output text)
CURRENT_REGION=$(curl -s http://169.254.169.254/latest/meta-data/placement/availability-zone | sed 's/\(.*\)[a-z]/\1/')
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

export INFOPATH="/home/linuxbrew/.linuxbrew/share/info"

function _logger() {
    echo -e "$(date) ${YELLOW}[*] $@ ${NC}"
}

function resize_volume() {
    SIZE=${1:-20}
    INSTANCEID=$(curl http://169.254.169.254/latest/meta-data/instance-id)
    VOLUMEID=$(aws ec2 describe-instances \
    --instance-id $INSTANCEID \
    --query "Reservations[0].Instances[0].BlockDeviceMappings[0].Ebs.VolumeId" \
    --output text)

    aws ec2 modify-volume --volume-id $VOLUMEID --size $SIZE

    while [ \
    "$(aws ec2 describe-volumes-modifications \
        --volume-id $VOLUMEID \
        --filters Name=modification-state,Values="optimizing","completed" \
        --query "length(VolumesModifications)"\
        --output text)" != "1" ]; do
    sleep 1
    done

    if [ $(readlink -f /dev/xvda) = "/dev/xvda" ]
    then
        sudo growpart /dev/xvda 1
        STR=$(cat /etc/os-release)
        SUB="VERSION_ID=\"2\""
        if [[ "$STR" == *"$SUB"* ]]
        then
            sudo xfs_growfs -d /
        else
            sudo resize2fs /dev/xvda1
        fi
    else
        sudo growpart /dev/nvme0n1 1
        STR=$(cat /etc/os-release)
        SUB="VERSION_ID=\"2\""
        if [[ "$STR" == *"$SUB"* ]]
        then
            sudo xfs_growfs -d /
        else
            sudo resize2fs /dev/nvme0n1p1
        fi
    fi
}

function upgrade_sam_cli() {
    _logger "[+] Backing up current SAM CLI"
    cp $(which sam) ~/.sam_old_backup

    _logger "[+] Installing latest SAM CLI"
    brew tap aws/tap
    brew install aws-sam-cli

    _logger "[+] Updating Cloud9 SAM binary"
    # Allows for local invoke within IDE (except debug run)
    ln -sf $(which sam) ~/.c9/bin/sam
}

function upgrade_existing_packages() {
    _logger "[+] Upgrading system packages"
    sudo yum update -y

    _logger "[+] Upgrading Python pip and setuptools"
    python3 -m pip install --upgrade pip setuptools --user

    _logger "[+] Installing latest AWS CLI"
    python3 -m pip install --upgrade --user awscli
}

function install_linuxbrew() {
    _logger "[+] Creating touch symlink"
    sudo ln -sf /bin/touch /usr/bin/touch
    _logger "[+] Installing homebrew..."
    echo | sh -c "$(curl -fsSL https://raw.githubusercontent.com/Linuxbrew/install/master/install.sh)"
    _logger "[+] Adding homebrew in PATH"
    test -d ~/.linuxbrew && eval $(~/.linuxbrew/bin/brew shellenv)
    test -d /home/linuxbrew/.linuxbrew && eval $(/home/linuxbrew/.linuxbrew/bin/brew shellenv)
    test -r ~/.bash_profile && echo "eval \$($(brew --prefix)/bin/brew shellenv)" >>~/.bash_profile
    echo "eval \$($(brew --prefix)/bin/brew shellenv)" >>~/.profile
}

function install_utilities() {
    sudo yum install -y jq
    brew install dateutils
}

function main() {
    resize_volume
    upgrade_existing_packages
    install_linuxbrew
    upgrade_sam_cli
    install_utilities

    echo 'export PATH="/home/linuxbrew/.linuxbrew/opt/python@3.8/bin:$PATH"' >> /home/ec2-user/.bash_profile

    echo -e "${RED} [!!!!!!!!!] OPEN A NEW TERMINAL AND CLOSE THIS ONE ${NC}"
    exec ${SHELL}
}

main