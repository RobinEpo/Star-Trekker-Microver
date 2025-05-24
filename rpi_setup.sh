#!/bin/bash

# Fail fast on errors
set -e

# Settings
SSID="mati_rpi6"
PASSWORD="randomPassword"
IP_ADDRESS="192.168.4.1/24"
PLACEHOLDER_DIR="/Desktop/Star-Trekker-Microver/python"

# Create the hotspot
echo "Creating hotspot connection..."
sudo nmcli device wifi hotspot ifname wlan0 ssid "$SSID" password "$PASSWORD"

# Wait a moment for it to register
sleep 2

# Find the connection name just created
HOTSPOT_CON=$(nmcli -t -f NAME,TYPE connection show | grep ":wifi" | cut -d: -f1 | tail -n1)

echo "Configuring hotspot IP and sharing on connection: $HOTSPOT_CON"

# Set static IP and enable IP sharing
sudo nmcli connection modify "$HOTSPOT_CON" ipv4.addresses "$IP_ADDRESS"
sudo nmcli connection modify "$HOTSPOT_CON" ipv4.method shared

# Apply the connection
sudo nmcli connection up "$HOTSPOT_CON"

# Final step: switch to your working directory
cd "$PLACEHOLDER_DIR"
echo "Switched to directory: $PLACEHOLDER_DIR"
