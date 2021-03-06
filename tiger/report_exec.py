import io
import json
import uuid
import traceback
from tabulate import tabulate

from tiger.constants import RE_COMPUTE
from tiger.report import Report, MetadataNotFound
from gooddata_metadata_client.exceptions import ApiException


def process_compute_execution(metadata_client, slack_client, report_match, text, channel_id, workspace_id):
    try:
        # Init Report(Pandas) SDK
        report_client = Report(workspace_id, metadata_client)
        request = report_client.parse_request(RE_COMPUTE, text)
        if request:
            df = report_client.execute(request['metrics'], request['labels'])
            base_path = '/tmp/' + str(uuid.uuid4())
            if report_match.group(1) == 'tab':
                file_path = base_path + '.txt'
                target_file_name = 'insight.txt'
                with open(file_path, 'wt') as fd:
                    fd.write(tabulate(df, headers='keys', tablefmt='psql', showindex="never"))
            elif report_match.group(1) == 'csv':
                file_path = base_path + '.csv'
                target_file_name = 'insight.csv'
                with open(file_path, 'wt') as fd:
                    df.to_csv(fd, index=False)
            elif report_match.group(1) == 'xls':
                file_path = base_path + '.xls'
                target_file_name = 'insight.xlsx'
                with open(file_path, 'w+b') as fd:
                    df.to_excel(fd, index=False)
            else:
                file_path = base_path + '.png'
                target_file_name = 'insight.png'
                print(f"Creating file {file_path} for {text}")
                with open(file_path, 'w+b') as fd:
                    if report_match.group(1) == 'line':
                        ax = report_client.plot_line(df, request['labels'][0]['title'])
                    else:
                        ax = report_client.plot_bar(df, request['labels'][0]['title'])
                    ax.figure.savefig(fd)
                print(f"Finished file {file_path} for {text}")
            slack_client.send_file(channel_id, file_path, target_file_name)
        else:
            slack_client.send_markdown_message(
                channel_id, ['ERROR: invalid execute request, valid is {metric} BY {dimension}\n']
            )
    except ApiException as nfe:
        print(f"Got you - {type(nfe.body)}")
        msg = str(nfe.body)
        body_io_str = None
        try:
            body_io_str = io.StringIO(nfe.body)
            body_dict = json.load(body_io_str)
            msg = f"{body_dict['detail']} - {body_dict['title']}"
            print("Have detail")
        except Exception as e:
            print(f"Have detail failed - {str(e)}")
            pass
        finally:
            if body_io_str:
                body_io_str.close()
        slack_client.send_markdown_message(channel_id, [f"Execution of request `{text}` failed.\n{msg}\n"])
    except MetadataNotFound as e:
        slack_client.send_markdown_message(channel_id, [f"Execution of request `{text}` failed.\n{str(e)}\n"])
    except Exception as e:
        print(traceback.format_exc())
        text_i: str = text
        if not text_i.startswith("execute"):
            split_text = text_i.split(' ', maxsplit=1)
            if len(split_text) > 1:
                text = split_text[1]
        slack_client.send_markdown_message(channel_id, [f"Execution of request `{text}` failed.\n"])
