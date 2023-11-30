""" Small script to load prefect secrets """
import os
import sys
from pathlib import Path

# pylint: disable=F0401
import dotenv
from dotenv import load_dotenv
# pylint: enable=F0401
from prefect.blocks.system import Secret

load_dotenv(Path('stack.env'))
if __name__ == '__main__':
    SECRET = sys.argv[1]
    assert os.getenv('PREFECT_API_KEY')
    print(Secret.load(f"{SECRET}").get())
    dotenv.set_key(Path('stack.env'), "key", "value")
