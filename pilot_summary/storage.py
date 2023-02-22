import csv


def write_to_csv(results, filename):
  csv_columns = ['Resource', 'Count']
  with open(filename, 'w') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
    writer.writeheader()
    for data in results:
      writer.writerow({"Resource": data, 'Count': results[data]})
