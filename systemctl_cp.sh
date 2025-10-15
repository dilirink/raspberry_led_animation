name=flask-app.service
cp $name /etc/systemd/system/

systemctl enable $name
systemctl start $name