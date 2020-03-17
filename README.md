# Prisma Cloud alert csv export with tags and account group names 

Version: *1.0*
Author: *Eddie Beuerlein*

### Summary
This script will create a csv file that contains all the data from the alert CSV export in the UI in addition to tag and account groups per alert id.

### Requirements and Dependencies

1. Python 3.7 or newer

2. OpenSSL 1.0.2 or newer

(if using on Mac OS, additional items may be nessessary.)

3. Pip

```sudo easy_install pip```

4. Requests (Python library)

```sudo pip install requests```

5. YAML (Python library)

```sudo pip install pyyaml```

### Configuration

1. Navigate to *alert_tags_acctgrp/config/configs.yml*

2. Fill out your Prisma Cloud access key, secret, and customer name - if you are the only customer in your account then leave this blank.

3. API base - only need to adjust this if you are on a different stack (app=api, app2=api2, app3=api3, etc.)

4. You can also set the time range for the data that is pulled by setting the following(in runner.py at the top):

    ```
    'timerange_unit': 'month', # day, week, month, hour
    'timerange_amount': 1
    ```
    

### Run

```
python runner.py

```
