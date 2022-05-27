from ossapi import *
from apikeys import CLIENT_ID, CLIENT_SECRET, API_KEY
from datetime import timedelta
from math import floor
from pprint import pprint


def user_v2(api, uid):
    player = api.user(uid)
    # pprint(vars(player))
    stats = player.statistics
    
    day_delta = timedelta(seconds=stats.play_time).days
    hour_delta = timedelta(seconds=stats.play_time-day_delta*86400).seconds//3600
    min_delta = timedelta(seconds=stats.play_time-day_delta*86400-hour_delta*3600).seconds//60
    full_hours = stats.play_time//3600
    
    res = f'''
    Player: {player.username}
    Rank: #{stats.global_rank} ({player.country_code} #{stats.country_rank})
    Playcount: {stats.play_count} (Lv{stats.level.current})
    Playtime: {day_delta}d {hour_delta}h {min_delta}m ({full_hours} hours)
    PP: {stats.pp:.0f}
    Accuracy: {stats.hit_accuracy:.2f}%
    https://osu.ppy.sh/u/{player.id}'''
    return res


def calc_acc(score):
    _300 = score.count_300
    _100 = score.count_100
    _50 = score.count_50
    _miss = score.count_miss
    return (300*_300 + 100*_100 + 50*_50)/(300*(_300 + _100 + _50 + _miss)) * 100

def calc_completion(score, b):
    return (score.count_300 + score.count_100 + score.count_50 + score.count_miss)/(b.count_hitcircles+b.count_sliders+b.count_spinners)*100

def recent(apiv1, apiv2, uid, index=None):
    if index is not None:
        if index > 50 or index == 0:
            return "Доступны только последние 50 скоров"
    else:
        index = 1
        
    score = apiv1.get_user_recent(uid, 0, index)[index-1]
    b = apiv1.get_beatmaps(beatmap_id=score.beatmap_id)[0]
    map_status = {4: "Loved", 3: "Qualified", 2: "Approved", 1: "Ranked", 0: "Pending", -1: "WIP", -2: "Graveyard"}
    
    return f'''
    <{map_status[int(b.approved)]}> {b.artist} - {b.title} [{b.version}] by {b.creator}
    {b.total_length//60:.0f}:{b.total_length%60:.0f} | AR:{b.approach_rate} CS:{b.circle_size} OD:{b.overrall_difficulty} HP:{b.health} {b.bpm}BPM | {b.star_rating:.2f}✩ {f"+{score.mods.short_name()}" if score.mods.value != 0 else ""}
    
    Score: {score.score} | Combo: {score.max_combo}x/{b.max_combo}x
    Accuracy: {calc_acc(score):.2f}%
    PP: {0 if score.pp is None else score.pp}
    Hitcounts: {score.count_300}/{score.count_100}/{score.count_50}/{score.count_miss}
    Grade: {score.rank} ({calc_completion(score, b):.2f}%)
    
    Beatmap: https://osu.ppy.sh/b/{b.beatmap_id}
    '''


def top_plays(apiv1, uid, index=None):
    if index is not None:
        if index > 100 or index == 0:
            return "Доступны только последние 100 скоров"
        else:
            scores = apiv1.get_user_best(uid, 0, index)[index-1:index]
    else:
        scores = apiv1.get_user_best(uid, 0, index)[:3]
        index = 1
    
    player_name = apiv1.get_user(uid).username
    res = f"Топ скоры игрока {player_name}:"
    for score in scores:
        b = apiv1.get_beatmaps(beatmap_id=score.beatmap_id)[0]
        res += f'''
        #{index}
        {b.title} [{b.version}] {f"+{score.mods.short_name()}" if score.mods.value != 0 else ""}
        AR:{b.approach_rate} CS:{b.circle_size} OD:{b.overrall_difficulty} HP:{b.health} {b.star_rating:.2f}✩
        Grade: {score.rank} ⯈ {score.max_combo}x/{b.max_combo}x ⯈ {b.total_length//60:.0f}:{b.total_length%60:.0f}
        Accuracy: {calc_acc(score):.2f}% ⯈ {score.count_300}/{score.count_100}/{score.count_50}/{score.count_miss}
        PP: {score.pp}
        {score.date}
        https://osu.ppy.sh/b/{b.beatmap_id}
        '''
        index += 1
    return res


apiv2 = OssapiV2(CLIENT_ID, CLIENT_SECRET)
apiv1 = Ossapi(API_KEY)


# print(user_v2(apiv2, "qod3r"))
# print(recent(apiv1, apiv2, "whitecat"))
print(top_plays(apiv1, "qod3r"))