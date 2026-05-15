/* Bluelight-filter toggle */

#!/bin/sh

if pgrep -x wlsunset >/dev/null; then
  pkill -x wlsunset
else
  wlsunset -T 1500 -t 1000 &
fi
