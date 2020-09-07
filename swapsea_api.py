import requests
import argparse
import base64
# from requests_jwt import JWTAuth


def upload_report(endpoint, fname, auth=None):
    # data = open(fname, "r").read()
    # data64 = base64.encodestring(data)
    # auth = JWTAuth(apikey)
    # auth.add_field('file', data64)
    # r = requests.post(endpoint, data={"file": data64})
    r = requests.post(endpoint, files={'file_data': open(fname, 'r')} , auth=auth)
    return (r.status_code, r.reason)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Upload report to Swapsea')
    parser.add_argument('-f', type=str, required=True, help='Path to report file')
    parser.add_argument('-e', type=str, required=True, help='URI to API endpoint')
    parser.add_argument('-u', type=str, required=True, help='Username')
    parser.add_argument('-p', type=str, required=True, help='Password')

    #parser.add_argument('-k', type=str, required=True, help='API key')
    args = parser.parse_args()
    print ("Uploading: {} to {}".format(args.e, args.f))
    code, reason = upload_report(args.e, args.f, (args.u, args.p))
    print ("Response ({}): {}".format(code, reason))
