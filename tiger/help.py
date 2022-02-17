
def generate_help(slack_client, text, channel_id, thread_id):
    if "help compute" in text:
        help_hints = [
            ":speech_balloon: Thank you for asking, here is detailed doc about `compute <type>`:\n\n" +
            "* Usage: `compute <type>` metric1, metric2 BY label1, label2\n" +
            "\t* You can use 2 metrics but only 1 label in case of line/bar charts\n" +
            "\t* metric/label must be in form of ID with prefix\n" +
            "\t\t* e.g. label/date.month or fact/order_lines.price\n\n" +
            "\t* use `list labels/metrics` to get these IDs\n\n" +
            "* Compute types:\n" +
            "\t* `tab` - pretty printed table\n" +
            "\t* `csv` - CSV file as attachment\n" +
            "\t* `xls` - Excel file as attachment\n" +
            "\t* `line` - line chart rendered by `matplotlib`\n" +
            "\t* `bar` - bar chart rendered by `matplotlib`\n" +
            ":raised_hands:\n"
        ]
        slack_client.send_markdown_message(channel_id, help_hints, thread_id)
    else:
        help_hints = [
            ":speech_balloon: Thank you for asking, there are few hints I can help you with:\n\n" +
            "* `list (workspaces,data sources,labels,metrics,insights)` \n" +
            "\t* you can list multiple object types by single command, e.g. `list workspaces metrics`\n" +
            "* `compute (tab,csv,vis)`\n" +
            "\t* computes report and returns table, csv or visualization\n\n" +
            " use `help compute` to learn more about how to setup report definition"
            ":raised_hands:\n"
        ]
        slack_client.send_markdown_message(channel_id, help_hints, thread_id)
