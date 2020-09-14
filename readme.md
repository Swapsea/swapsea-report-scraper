# Automated email report processing for Swapsea

## Setup (local test environment)
Create a virtual environment to sandbox this script:
```
cd swapsea-v2/plugins/surfguard_reports
sudo easy_install pip         # install pip
sudo pip install virtualenv   # install virtualenv
virtualenv env                # create env
source env/bin/activate       # activate env
```

Get dependencies:
```
pip install -r requirements.txt
```

Setup chosen gmail account account for oAuth2 by following  instructions in the following link:  https://developers.google.com/gmail/api/auth/about-auth

Once you have the ``USER``, ``CLIENT_ID`` and ``CLIENT_SECRET``, you will need to generate the ``REFRESH_TOKEN`` using the following command:
```
python google_oauth2.py --user=xxx@gmail.com \
   --client_id=1038[...].apps.googleusercontent.com \
   --client_secret=VWFn8LIKAMC-MsjBMhJeOplZ \
   --generate_oauth2_token
```
Then follow the instructions... Copy the ``REFRESH_TOKEN`` for the next step.

Set credentials in the config file:
```
nano process_surfgaurd_email.json
```
Update ``USER``, ``CLIENT_ID``, ``CLIENT_SECRET`` and ``REFRESH_TOKEN`` for the relevant account that will receive the reports.

## Running script
```
python process_surfgaurd_email.py
```

## Deployment on Heroku ##
* Add Heroku remote
* Push to deploy on Heroku
* Set Heroku environment variables for ``USER``, ``CLIENT_ID``, ``CLIENT_SECRET`` and ``REFRESH_TOKEN`` (so that they do not need to be set in the config file and saved to the git repository, as Heroku file storage is ephemeral and gets wiped with each deployment)
* Setup Heroku Scheduler add-on to execute at desired frequency (daily)

To set up Heroku Scheduler:
1. `Configure Add-ons > Heroku Scheduler > Add Job/edit`
1. Setup schedule:
   * Every dat at... `6:00 PM UTC` (translates to 5am AEDT / 4am AEST)
   * Run command: `python process_surfgaurd_email.py`
   * With `Standard-1X` (only runs for a few seconds each day)

## How it works: ##

1. The script logs in to a gmail account using oAuth2 credentials contained in the config file.
1. It then searches for **UNSEEN** emails that have the subject "**SurfGuard Report: Custom Report**" (``SEARCH_FOR`` in the config file)
1. It then processes the email(s) to:
    1. Extract and open any link(s) contained in the email(s)
    1. Locate the temporary file by extracting the links from the HTML of the Surfguard report download page
    1. Download the temporary file to the temporary directory (``DATA_TMP_DIR`` in the config file)
1. The next step is to processes any downloaded temporary files contained in the temporary directory:
    1. Checks the report type based on identifying information (``header_line`` in the config file)
    1. Uploads it to the relevant endpoint (``post_endpoint`` in the config file)
    1. Renames and moves it to the archive directory (``DATA_ARCH_DIR`` & ``fname`` in the config file)

## TODOS:
* add more detailed info to the Heroku deployment section.
* Uncomment and test line# 80 of process_surfguard_reports.py to actually perform HTTP post to Swapsea API
