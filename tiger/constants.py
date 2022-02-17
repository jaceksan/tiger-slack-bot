import os
import re

RE_COMPUTE = re.compile(r'^<[^>]+>\s*compute (tab|csv|xls|vis) ', re.I)
ENDPOINT = 'https://bettermee.anywhere.gooddata.com'
TOKEN = os.environ.get('TIGER_API_TOKEN')
