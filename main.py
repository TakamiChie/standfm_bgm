import os
from pathlib import Path
import datetime
from argparse import ArgumentParser

from pydub import AudioSegment
from pydub.utils import ratio_to_db
from mutagen.id3 import ID3
import yaml

TODAY = datetime.date.today()

config = {
  "path": {}
}

parser = ArgumentParser()
parser.add_argument("--date", default=TODAY, type=lambda s: datetime.datetime.strptime(s, "%Y/%m/%d"), help="yyyy/mm/dd形式の日付。指定がない場合は今日の日付。")
parser.add_argument("--file", type=str, help="処理対象のファイル名。これを指定した場合dateは無視される")
parser.add_argument("--bgm", default="default.mp3", help="BGMに使用するファイル名。指定が無い場合はdefault.mp3")
args = parser.parse_args()

with open("config.yml", "r") as f:
  config = yaml.safe_load(f)
  for n, v in config["path"].items():
    config["path"][n] = Path(os.path.expandvars(v))

print("> During data loading")
voicepath = Path(config["path"]["basefolder"] / (datetime.datetime.strftime(args.date, "%Y-%m-%d.mp3") if args.file is None else args.file))
destpath = Path(config["path"]["destfile"])
voice = AudioSegment.from_mp3(voicepath)
bgm = AudioSegment.from_mp3(config["path"]["bgmfolder"] / args.bgm)
back : AudioSegment = AudioSegment.empty()
introms= config["time"]["intro"]
endingms = config["time"]["ending"]
fadeoutms = config["time"]["fadeout"]
intros = introms / 1000
endings = endingms / 1000
body_vol : float = ratio_to_db(float(config["body_vol"]))
print("Finished.")

print("> Preparation of BGM")
print(f'0 / {int(voice.duration_seconds + intros + endings)}', end="")
while back.duration_seconds + bgm.duration_seconds < voice.duration_seconds + intros + endings:
  back = back + bgm
  print(f'\r{int(back.duration_seconds)} / {int(voice.duration_seconds + intros + endings)}', end="")
back = back + bgm[:voice.duration_seconds * 1000 - back.duration_seconds * 1000 + introms + endingms]
print(f'\r{int(back.duration_seconds)} / {int(voice.duration_seconds + intros + endings)}')
print("Finished.")

print("> Volume adjustment")
back = back[:introms] + (back[introms:endingms * -1] + body_vol) + \
  back[endingms * - 1:].fade_out(fadeoutms)
print("Finished.")

print("> Output voice creation")
result : AudioSegment = back.overlay(voice, introms)
result.export(destpath, format="mp3")
print("Finished.")

print("> Copy MP3 Tags")
srctag = ID3(str(voicepath))
desttag = ID3(str(destpath))
for v in srctag.values():
  desttag.add(v)
desttag.save()
print("Finished.")

print(f'All Finished. The file is stored in {destpath}.')
