*setup init script*

get libs
```
sudo apt-get install python-setuptools
sudo easy_install pip
```


place init script
```
cp temperature /etc/init.d
sudo update-rc.d temperature defaults
```
