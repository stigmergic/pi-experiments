*setup init script*

get libs
```
sudo apt-get install python-setuptools
sudo apt-get install python-dev
sudo easy_install pip
sudo pip install -r requirements.txt
```


place init script
```
cp temperature /etc/init.d
sudo update-rc.d temperature defaults
```
