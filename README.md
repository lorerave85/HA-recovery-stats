# HA-recovery-stats

## WORK IN PROGRESS

### Extract from DB

in app.py on row 78: replace database_path with your db path
```python
database_path = "/Users/ravello001/Downloads/old_home-assistant_v2.db"
```
Insert the list of your energy metrics in list.txt
```
sensor.consumption_43
sensor.consumption_45
sensor.consumption_47
sensor.consumption_38
...
```
Now run script
```shell
./script_01.sh
```
This script will create a .tsv file for each metric

### Merge file

Now run script
```shell
./script_02.sh
```
Now copy statisticdata.tsv in your HA and run the integration.

