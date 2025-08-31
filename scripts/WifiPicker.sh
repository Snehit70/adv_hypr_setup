#!/usr/bin/env bash

# Simple Wi‑Fi picker for Waybar/Hyprland using rofi + nmcli
# Falls back to iwgtk / gnome-control-center / nm-connection-editor / nmtui if rofi is unavailable

set -u

have() { command -v "$1" >/dev/null 2>&1; }

# If rofi is not available, gracefully fall back to a GUI or TUI
if ! have rofi; then
  if have iwgtk; then
    nohup iwgtk >/dev/null 2>&1 &
    exit 0
  fi
  if have gnome-control-center; then
    nohup gnome-control-center wifi >/dev/null 2>&1 &
    exit 0
  fi
  if have nm-connection-editor; then
    nohup nm-connection-editor >/dev/null 2>&1 &
    exit 0
  fi
  # Fallback to terminal nmtui
  if have kitty; then nohup kitty --title nmtui -e nmtui >/dev/null 2>&1 & exit 0; fi
  if have alacritty; then nohup alacritty -t nmtui -e nmtui >/dev/null 2>&1 & exit 0; fi
  if have footclient; then nohup footclient -T nmtui nmtui >/dev/null 2>&1 & exit 0; fi
  if have wezterm; then nohup wezterm -e nmtui >/dev/null 2>&1 & exit 0; fi
  if have gnome-terminal; then nohup gnome-terminal -- nmtui >/dev/null 2>&1 & exit 0; fi
  if have konsole; then nohup konsole -e nmtui >/dev/null 2>&1 & exit 0; fi
  if have xterm; then nohup xterm -e nmtui >/dev/null 2>&1 & exit 0; fi
  # As a last resort, try nmtui directly
  nohup nmtui >/dev/null 2>&1 &
  exit 0
fi

rofi_cmd() {
  rofi -dmenu -i -p "Wi‑Fi" "$@"
}

notify() {
  local msg="$1"
  if command -v notify-send >/dev/null 2>&1; then
    notify-send "Wi‑Fi" "$msg"
  fi
}

wifi_dev=$(nmcli -t -f DEVICE,TYPE device status 2>/dev/null | awk -F: '$2=="wifi"{print $1; exit}')
if [[ -z "${wifi_dev:-}" ]]; then
  rofi_cmd <<< "No Wi‑Fi device found" >/dev/null
  exit 0
}

wifi_radio=$(nmcli radio wifi 2>/dev/null)

list_networks() {
  nmcli -t -f ACTIVE,SSID,BSSID,SIGNAL,SECURITY device wifi list --rescan yes 2>/dev/null |
    awk -F: '
      function sigicon(s){if(s>=80)return "󰤨";else if(s>=60)return "󰤥";else if(s>=40)return "󰤢";else if(s>=20)return "󰤟";else return "󰤯"}
      function lockicon(sec){return (sec=="--"||sec=="")?"":""}
      {
        active=$1; ssid=$2; bssid=$3; sig=$4; sec=$5;
        if(ssid=="") ssid="<hidden>";
        mark=(active=="yes")?"*":" ";
        printf "%s  %3s  %s  %s  %s  [%s]\n", mark, sig, sigicon(sig), ssid, lockicon(sec), bssid
      }'
}

show_menu() {
  local extra1 extra2 extra3
  if [[ "$wifi_radio" == "enabled" ]]; then
    extra1="󰖩  Toggle Wi‑Fi (Off)"
  else
    extra1="󰖩  Toggle Wi‑Fi (On)"
  fi
  extra2="↻  Rescan"
  extra3="🛠  Edit Connections"

  { printf "%s\n%s\n%s\n" "$extra1" "$extra2" "$extra3"; list_networks; } | rofi_cmd
}

handle_choice() {
  local choice="$1"

  case "$choice" in
    "󰖩  Toggle Wi‑Fi (Off)")
      nmcli radio wifi off && notify "Wi‑Fi turned off"
      ;;
    "󰖩  Toggle Wi‑Fi (On)")
      nmcli radio wifi on && notify "Wi‑Fi turned on"
      ;;
    "↻  Rescan")
      nmcli device wifi rescan >/dev/null 2>&1
      ;;
    "🛠  Edit Connections")
      if command -v nm-connection-editor >/dev/null 2>&1; then
        nohup nm-connection-editor >/dev/null 2>&1 &
      else
        notify "Install nm-connection-editor for GUI editing"
      fi
      ;;
    *)
      # Network line: "*  80  ICON  SSID  LOCK  [BSSID]"
      # Extract BSSID and SSID
      local bssid ssid
      bssid=$(sed -n 's/.*\[\(.*\)\].*/\1/p' <<<"$choice")
      ssid=$(sed -E 's/^.?\s+[0-9]+\s+[^ ]+\s+([^ ].*?)\s+(|)\s+\[.*$/\1/' <<<"$choice")
      if [[ -z "$bssid" || -z "$ssid" ]]; then
        return
      fi

      # Determine if secured (lock icon present)
      if grep -q "" <<<"$choice"; then
        # Ask for password
        local pass
        pass=$(rofi -dmenu -password -p "Password for $ssid" <<< "")
        [[ -z "${pass}" ]] && exit 0
        if nmcli device wifi connect "$bssid" password "$pass" >/dev/null 2>&1; then
          notify "Connected to $ssid"
        else
          notify "Failed to connect to $ssid"
        fi
      else
        if nmcli device wifi connect "$bssid" >/dev/null 2>&1; then
          notify "Connected to $ssid"
        else
          notify "Failed to connect to $ssid"
        fi
      fi
      ;;
  esac
}

main() {
  local choice
  choice=$(show_menu) || exit 0
  [[ -z "$choice" ]] && exit 0
  handle_choice "$choice"
}

main
