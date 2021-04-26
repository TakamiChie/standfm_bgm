import os
from pathlib import Path
import datetime
from argparse import ArgumentParser

from pydub import AudioSegment
from pydub.utils import db_to_float, ratio_to_db

import yaml

TODAY = datetime.date.today()

config = {
  "path": {}
}

parser = ArgumentParser()
parser.add_argument("--date", default=TODAY, type=lambda s: datetime.datetime.strptime(s, "%Y/%m/%d"), help="yyyy/mm/dd形式の日付。指定がない場合は今日の日付。")
parser.add_argument("--bgm", default="default.mp3", help="BGMに使用するファイル名。指定が無い場合はdefault.mp3")
args = parser.parse_args()

with open("config.yml", "r") as f:
  config = yaml.safe_load(f)
  for n, v in config["path"].items():
    config["path"][n] = Path(os.path.expandvars(v))

voice = AudioSegment.from_mp3(config["path"]["basefolder"] / datetime.datetime.strftime(args.date, "%Y-%m-%d.mp3"))
bgm = AudioSegment.from_mp3(config["path"]["bgmfolder"] / args.bgm)
back = bgm[:5 * 1000] + (bgm[5 * 1000:] + ratio_to_db(0.2))
