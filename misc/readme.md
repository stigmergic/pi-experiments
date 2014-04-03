*setup init script*

get libs
```
sudo apt-get install python-setuptools
sudo easy_install pip
```


```
cp temperature /etc/init.d
sudo update-rc.d temperature defaults
```
