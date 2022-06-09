from datetime import timedelta
from math import floor
from ossapi import Ossapi
import oppadc
from apikeys import API_KEY
from pprint import pprint


def user(api, uid):
    player = api.get_user(uid)
    day_delta = timedelta(seconds=player.seconds_played).days
    hour_delta = timedelta(seconds=player.seconds_played-day_delta*86400).seconds//3600
    min_delta = timedelta(seconds=player.seconds_played-day_delta*86400-hour_delta*3600).seconds//60
    full_hours = player.seconds_played//3600
    
    res = f'''
    Player: {player.username}
    Rank: #{player.rank} ({player.country} #{player.country_rank})
    Playcount: {player.playcount} (Lv{floor(player.level)})
    Playtime: {day_delta}d {hour_delta}h {min_delta}m ({full_hours} hours)
    PP: {player.pp_raw:.0f}
    Accuracy: {player.accuracy:.2f}%
    https://osu.ppy.sh/u/{player.user_id}'''
    return res

# <Graveyard> TAKU INOUE & Mori Calliope - Yona Yona Journey [dancing in the moonlight] by PotatoDew
# 03:33 | AR:9 CS:4 OD:9 HP:3.5 122BPM | 7.29✩

# Score: 14428 | Combo: 19x/1462x
# Accuracy: 79.63%
# PP: 10.01 ⯈ FC: 335.39 ⯈ SS: 538.44
# Hitcounts: 19/7/1/0
# Grade: F (2.3%)

# Beatmap: https://osu.ppy.sh/b/3514695
def recent(api, uid):
    print(len(api.get_user_recent(uid)))
    score = api.get_user_recent(uid)[0]
    b = api.get_beatmaps(beatmap_id=score.beatmap_id)[0]
    
    map_status = {4: "Loved", 3: "Qualified", 2: "Approved", 1: "Ranked", 0: "Pending", -1: "WIP", -2: "Graveyard"}
    
    return f'''
    <{map_status[int(b.approved)]}> {b.artist} - {b.title} [{b.version}] by {b.creator}
    {b.total_length//60:.0f}:{b.total_length%60:.0f} | AR:{b.approach_rate} CS:{b.circle_size} OD:{b.overrall_difficulty} HP:{b.health} {b.bpm}BPM | {b.star_rating:.2f}✩ {f"+{score.mods.short_name()}" if score.mods.value != 0 else ""}
    
    Score: {score.score} | Combo: {score.max_combo}x/{b.max_combo}x
    Accuracy: acc
    PP: {0 if score.pp is None else score.pp}
    Hitcounts: {score.count_300}/{score.count_100}/{score.count_50}/{score.count_miss}
    Grade: {score.rank}
    
    Beatmap: https://osu.ppy.sh/b/{b.beatmap_id}
    '''


api = Ossapi(API_KEY)

# print(user(api, "sakamata1"))
print(recent(api, 9453854))
# pprint(recent(api, 9453854))