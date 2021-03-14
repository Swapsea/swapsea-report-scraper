from google_oauth2 import RefreshToken, GenerateOAuth2String, TestImapAuthentication, imaplib
from email.parser import HeaderParser
from bs4 import BeautifulSoup
import re
import urllib2
import urllib
import os
import time
import glob
import linecache
import json
import traceback
from swapsea_api import upload_report

# Get config values from JSON file
def get_json_config(cfg_filename):
    with open(cfg_filename) as data_file:
        return json.load(data_file)

# Get temporary token from refresh token (valid for 1 hour)
def get_oauth2_access_token(client_id, client_secret, refresh_token):
    print ("Getting refresh token for: {}".format(client_id))
    resp = RefreshToken(client_id, client_secret, refresh_token)
    return resp['access_token']

# Authenticate connection
def get_imap_conn(user, access_token):
    print ("IMAP authentication for: {}".format(user))
    auth_string = GenerateOAuth2String(user, access_token,base64_encode=False)
    imap_conn = imaplib.IMAP4_SSL('imap.gmail.com')
    #imap_conn.debug = 4
    imap_conn.authenticate('XOAUTH2', lambda x: auth_string)
    imap_conn.select('INBOX')
    return imap_conn

# Get emails
def save_surfguard_reports_from_email(imap_conn, search_for, savedir):
    print ("Checking emails...")
    status, email_ids = imap_conn.search(None, search_for)
    nurls, nemails, nlinks = 0, 0, 0
    for e_id in email_ids[0].split():
        print ("  Checking email ID: {}".format(e_id))
        nemails += 1
        _, response = imap_conn.fetch(e_id, '(UID BODY[TEXT])')
        email_urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', response[0][1])
        for f in email_urls:
            try:
                print ("  Found link: {}".format(f))
                resp = urllib2.urlopen(f)
                soup = BeautifulSoup(resp, 'html.parser')
                for link in soup.find_all('a', href=True):
                    file_link = link.get('href',None)
                    if os.path.splitext(file_link)[1].lower()=='.csv':
                        tmpfile = os.path.join(savedir,os.path.basename(file_link))
                        print ("  Saving file: {} to {}".format(file_link, tmpfile))
                        urllib.urlretrieve(file_link, tmpfile)
                        nlinks += 1
                nurls += 1
            except Exception as e:
                print ("*** ERROR with: {}".format(f))
                traceback.print_exc()
        #imap_conn.store(e_id, '-X-GM-LABELS', "\Inbox")  # Archive by removing Inbox label NOT WORKING YET
        #imap_conn.uid('STORE', e_id , '-FLAGS', '(Inbox)')
    print ("Done processing {} links from {} urls in {} emails...".format(nlinks, nurls, nemails))


# Process files
def process_surfguard_reports(filetypes, header_line_no, tempdir, archdir, swapsea_url, swapsea_auth):
    print ("Processing temporary files...")
    timestr = time.strftime("%Y%m%d-%H%M%S")
    nfiles = 0
    for f in glob.glob(os.path.join(tempdir,"*.csv")):
        nfiles += 1
        header = linecache.getline(f,header_line_no).strip()
        for finfo in filetypes:
            if header == finfo['header_line']:
                origfile = os.path.splitext(os.path.basename(f))[0]
                fname = os.path.join(archdir, finfo['fname'].format(timestamp=timestr, origfile=origfile))
                print ("  Upload to: {}".format(finfo["post_endpoint"]))
                code, reason = upload_report(swapsea_url+finfo["post_endpoint"], f, auth=swapsea_auth)
                print ("  Response ({}): {}".format(code, reason))
                print ("  Renaming from: {} to {}".format(f, fname))
                os.rename(f, fname)
                break  # move to next file
    print ("Done processing {} files...".format(nfiles))




if __name__ == '__main__':
    cfg = get_json_config('process_surfguard_email.json')
    #cfg = get_json_config('process_surfguard_email-swapsea.json')
    # create directories if they do not exist
    if not os.path.exists(cfg['DATA_TMP_DIR']):
        os.makedirs(cfg['DATA_TMP_DIR'])
    if not os.path.exists(cfg['DATA_ARCH_DIR']):
        os.makedirs(cfg['DATA_ARCH_DIR'])

    access_token = get_oauth2_access_token(
        os.environ.get('CLIENT_ID',cfg['CLIENT_ID']) ,
        os.environ.get('CLIENT_SECRET',cfg['CLIENT_SECRET']),
        os.environ.get('REFRESH_TOKEN',cfg['REFRESH_TOKEN'])
    )
    swapsea_auth = (os.environ.get('SWAPSEA_USERNAME',cfg['SWAPSEA_USERNAME']),
                    os.environ.get('SWAPSEA_PASSWORD',cfg['SWAPSEA_PASSWORD']))

    swapsea_url = os.environ.get('SWAPSEA_URL', cfg['SWAPSEA_URL'])

    imap_conn = get_imap_conn(os.environ.get('USER_EMAIL',cfg['USER_EMAIL']), access_token)
    save_surfguard_reports_from_email(imap_conn, cfg['SEARCH_FOR'], cfg['DATA_TMP_DIR'])
    process_surfguard_reports(cfg['FILETYPES'], cfg['HEADER_LINE_NO'], cfg['DATA_TMP_DIR'], cfg['DATA_ARCH_DIR'], swapsea_url, swapsea_auth)
