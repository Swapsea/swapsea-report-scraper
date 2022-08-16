# Automated email report processing for Swapsea

Swapsea is a superior, award-winning patrol swap system for Australian Surf Life Saving Clubs. This part of the app is written in Python and processes emails from Surfguard to import into Swapsea. It is now Open Source to attract more amazing volunteer [contributors](https://github.com/Swapsea/swapsea-report-scraper/graphs/contributors) - just like the Life Saving movement itself.

- See CONTRIBUTING.md for instructions on how to contribute to Swapsea.
- See LICENSE.md for the terms under which Swapsea is Open Source.

## Setup (local test environment)

Create a virtual environment to sandbox this script:

```bash
sudo easy_install pip         # install pip
sudo pip install virtualenv   # install virtualenv
virtualenv env                # create env
source env/bin/activate       # activate env
```

Get dependencies:

```bash
pip install -r requirements.txt
```

Setup chosen gmail account account for oAuth2 by following instructions in the following link: https://developers.google.com/gmail/api/auth/about-auth

Once you have the `USER`, `CLIENT_ID` and `CLIENT_SECRET`, you will need to generate the `REFRESH_TOKEN` using the following command:

```bash
python google_oauth2.py --user=xxx@gmail.com \
   --client_id=1038[...].apps.googleusercontent.com \
   --client_secret=SECRET \
   --generate_oauth2_token
```

Then follow the instructions... Copy the `REFRESH_TOKEN` for the next step.

Set credentials in the config file:

```bash
nano process_surfguard_email.json
```

Update `USER`, `CLIENT_ID`, `CLIENT_SECRET` and `REFRESH_TOKEN` for the relevant account that will receive the reports.

## Running script

```bash
python process_surfguard_email.py
```

## Deployment on Heroku

- Add Heroku remote
- Push to deploy on Heroku
- Set Heroku environment variables for `USER`, `CLIENT_ID`, `CLIENT_SECRET` and `REFRESH_TOKEN` (so that they do not need to be set in the config file and saved to the git repository, as Heroku file storage is ephemeral and gets wiped with each deployment)
- Setup Heroku Scheduler add-on to execute at desired frequency (daily)

To set up Heroku Scheduler:

1. `Configure Add-ons > Heroku Scheduler > Add Job/edit`
1. Setup schedule:
   - Every dat at... `6:00 PM UTC` (translates to 5am AEDT / 4am AEST)
   - Run command: `python process_surfguard_email.py`
   - With `Standard-1X` (only runs for a few seconds each day)

## How it works

1. The script logs in to a gmail account using oAuth2 credentials contained in the config file.
1. It then searches for **UNSEEN** emails that have the subject "**SurfGuard Report: Custom Report**" (`SEARCH_FOR` in the config file)
1. It then processes the email(s) to:
   1. Extract and open any link(s) contained in the email(s)
   1. Locate the temporary file by extracting the links from the HTML of the Surfguard report download page
   1. Download the temporary file to the temporary directory (`DATA_TMP_DIR` in the config file)
1. The next step is to processes any downloaded temporary files contained in the temporary directory:
   1. Checks the report type based on identifying information (`header_line` in the config file)
   1. Uploads it to the relevant endpoint (`post_endpoint` in the config file)
   1. Renames and moves it to the archive directory (`DATA_ARCH_DIR` & `fname` in the config file)

## TODO

- add more detailed info to the Heroku deployment section.
- Uncomment and test line# 80 of process_surfguard_reports.py to actually perform HTTP post to Swapsea API

---

Copyright (C) 2019 Ariell Friedman

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

The GNU General Public License is at [LICENSE](LICENSE).

Contact us at help@swapsea.com.au
