# Bluelight-filter toggle

# First make it executable with chmod +x "$HOME/.config/rofi/scripts/toggle-sunset.sh"

#!/bin/sh

if pgrep -x wlsunset >/dev/null; then
  pkill -x wlsunset
else
  nohup wlsunset -T 1500 -t 1000 >/dev/null 2>&1 &
fi
