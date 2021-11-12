import os
import uuid
import traceback
from tabulate import tabulate
from tiger.report import Report

ENDPOINT = 'https://hackaton.anywhere.gooddata.com'
TOKEN = os.environ.get('TIGER_API_TOKEN')


def process_report_exec(metadata_client, slack_client, re_report, report_match, text, channel_id, workspace_id):
    try:
        # Init Report(Pandas) SDK
        report_client = Report(ENDPOINT, TOKEN, workspace_id, metadata_client)
        request = report_client.parse_request(re_report, text)
        if request:
            df = report_client.execute(request['metrics'], request['labels'])
            base_path = '/tmp/' + str(uuid.uuid4())
            if report_match.group(1) == 'tab':
                file_path = base_path + '.txt'
                with open(file_path, 'wt') as fd:
                    fd.write(tabulate(df, headers='keys', tablefmt='psql', showindex="never"))
            elif report_match.group(1) == 'csv':
                file_path = base_path + '.csv'
                with open(file_path, 'wt') as fd:
                    df.to_csv(fd, index=False)
            else:
                file_path = base_path + '.png'
                print(f"Creating file {file_path} for {text}")
                with open(file_path, 'w+b') as fd:
                    plot = report_client.plot_vis(df, request['labels'], request['metrics'])
                    plot.savefig(fd)
                print(f"Finished file {file_path} for {text}")
            slack_client.send_file(channel_id, file_path)
        else:
            slack_client.send_markdown_message(
                channel_id, ['ERROR: invalid execute request, valid is {metric} BY {dimension}\n']
            )
    except Exception:
        print(traceback.format_exc())
        slack_client.send_markdown_message(channel_id, [f"Execution of request `{text}` failed.\n"])
