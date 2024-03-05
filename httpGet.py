import requests, os
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("url", help="URL to get")

if __name__ == "__main__":
    args = parser.parse_args()
    print(args.url)

    resp = requests.get(args.url)
    if resp.status_code != 200:
        print("Error: {}".format(resp.status_code))
        os._exit(1)
    else:
        print(resp.text)
        os._exit(0)