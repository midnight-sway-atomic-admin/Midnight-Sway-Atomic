SDDM RICE

No external images, fonts, Plasma components, or third-party QML dependencies.

Install command (reboot after running):

sudo systemctl set-default graphical.target

cd ~/downloads
unzip sddm-rice.zip

sudo install -d /var/lib/sddm/themes
sudo cp -r sddm-rice /var/lib/sddm/themes/
sudo restorecon -RF /var/lib/sddm/themes/sddm-rice

sudo install -d /etc/sddm.conf.d
sudo tee /etc/sddm.conf.d/10-sddm-rice.conf >/dev/null <<'EOF'
[Theme]
ThemeDir=/var/lib/sddm/themes
Current=sddm-rice
EnableAvatars=false
EOF
