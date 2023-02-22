import logging
import os
from argparse import ArgumentParser, Namespace
from datetime import datetime

import requests
from tqdm import tqdm

from pilot_summary.globals import (FHIR_ENDPOINT, FHIR_RESOURCES,
                                   OUTPUT_DIR_DEFAULT, OUTPUT_FILENAME_DEFAULT)
from pilot_summary.notification import send_email
from pilot_summary.storage import write_to_csv


def setup_argparser():
  arg_parser = ArgumentParser(
    # TODO
    # description = '',
    # epilog = ''
  )
  #
  arg_parser.add_argument('-p', '--pilot',
    type=str, default='',
    help="Name of the pilot")
  #
  arg_parser.add_argument('-o', '--output-dir',
    type=str, default=OUTPUT_DIR_DEFAULT,
    help="Path of the results directory")
  #
  arg_parser.add_argument('-m', '--smtp-server',
    type=str, default='',
    help="IP or FQDN of SMTP server")
  #
  arg_parser.add_argument('-s', '--sender',
    type=str, default='',
    help="Sender email address. RECOMMENDED: noreply@example.org")
  #
  arg_parser.add_argument('-l', '--mailing-list',
    type=str, default='',
    help="Path of the mailing list file")
  #
  return arg_parser

def check_args(args: Namespace):
  #
  if args.pilot == '':
    raise ValueError("A pilot (-p, --pilot) name must be indicated")
  #
  output_dir = str(args.output_dir)
  if not os.path.exists(output_dir):
    os.makedirs(output_dir)
  #
  # TODO check if smtp_server is a valid url
  # TODO check if sender is a valid address
  #
  mailing_list_file = str(args.mailing_list)
  if not os.path.exists(mailing_list_file):
    raise ValueError("'%s' not exists" % mailing_list_file)
  # TODO check if mailing_list is not an empty file


#
# Main function
#
def main():
  logger = logging.getLogger()
  #
  try:
    # Parse console arguments
    arg_parser = setup_argparser()
    args = arg_parser.parse_args()
    # print(args) # DEBUG
    check_args(args)

    # Collect data from the selected pilot
    results = {}
    for resource in tqdm(FHIR_RESOURCES):
      request_url = FHIR_ENDPOINT % (args.pilot, resource)
      response = requests.get(request_url)
      results[resource] = str(response.json()['total'])

    # Store result in a CSV file
    date = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    output_filename = OUTPUT_FILENAME_DEFAULT % (args.pilot, date)
    output_file = args.output_dir + '/' + output_filename
    write_to_csv(results, output_file)

    # Send mail notification to the mailing list recipients
    subject = "[GATEKEEPER-%s] Report %s" % (args.pilot, date)
    with open(args.mailing_list) as f:
      mailing_list = [line.rstrip() for line in f]
    send_email(args.smtp_server, args.sender, mailing_list, subject, output_file)
  #
  except ValueError as e:
    logger.error("%s" % e)
  except Exception:
    logger.error("Interrupted:", exc_info=True)


if __name__=="__main__":
  print("DISCLAIMER: You must run this program from a machine with access to HPE's VPN\n\n "
        "FHIR GATEKEEPER DATA Summary.\n  ")
  main()
