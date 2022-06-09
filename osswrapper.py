from ossapi import *
from apikeys import CLIENT_ID, CLIENT_SECRET, API_KEY
from datetime import timedelta
from pprint import pprint

class Api:
    def __init__(self, keys):
        self.apiv1 = Ossapi(keys["api_key"])
        self.apiv2 = OssapiV2(keys["client_id"], keys["client_secret"], "http://localhost:3914/")

    def calc_acc(self, score):
        _300 = score.count_300
        _100 = score.count_100
        _50 = score.count_50
        _miss = score.count_miss
        return (300*_300 + 100*_100 + 50*_50)/(300*(_300 + _100 + _50 + _miss)) * 100
    
    def calc_completion(self, score, b):
        return (score.count_300 + score.count_100 + score.count_50 + score.count_miss)/(b.count_circles+b.count_sliders+b.count_spinners)*100

    def pretty_time(self, time):
        return f"{time.day:02d}.{time.month:02d}.{time.year} {time.hour:02d}:{time.minute:02d}"
    
    def score_string(self, score, b):
        map_status = {4: "Loved", 3: "Qualified", 2: "Approved", 1: "Ranked", 0: "Pending", -1: "WIP", -2: "Graveyard"}
        
        bs = b._beatmapset
        # pprint(score)
        res = f'''
            <{map_status[int(b.status.value)]}> {bs.artist} - {bs.title} [{b.version}] by {bs.creator}
            {b.total_length//60:02.0f}:{b.total_length%60:02.0f} | AR:{b.ar} CS:{b.cs} OD:{b.accuracy} HP:{b.drain} {b.bpm}BPM | {b.difficulty_rating:.2f}✩ {f"+{score.mods.short_name()}" if score.mods.value != 0 else ""}

            {self.pretty_time(score.created_at)}
            Score: {score.score} | Combo: {score.max_combo}x/{b.max_combo}x
            Accuracy: {self.calc_acc(score.statistics):.2f}%
            PP: {0 if score.pp is None else score.pp}
            Hitcounts: {score.statistics.count_300}/{score.statistics.count_100}/{score.statistics.count_50}/{score.statistics.count_miss}
            Grade: {score.rank.name} ({self.calc_completion(score.statistics, b):.2f}%)

            Beatmap: https://osu.ppy.sh/b/{b.id}
            '''
        return res

        
    def score_string_minimal(self, score, b):
        bs = b._beatmapset
        res = f'''
            {bs.title} [{b.version}] {f"+{score.mods.short_name()}" if score.mods.value != 0 else ""}
            AR:{b.ar} CS:{b.cs} OD:{b.accuracy} HP:{b.drain} {b.difficulty_rating:.2f}✩
            Grade: {score.rank.name} ⯈ {score.max_combo}x/{b.max_combo}x ⯈ {b.total_length//60:02.0f}:{b.total_length%60:02.0f}
            Accuracy: {self.calc_acc(score.statistics):.2f}% ⯈ {score.statistics.count_300}/{score.statistics.count_100}/{score.statistics.count_50}/{score.statistics.count_miss}
            PP: {score.pp}
            {self.pretty_time(score.created_at)}
            https://osu.ppy.sh/b/{b.id}
            '''
        return res

    def player_info(self, user_id):
        player = self.apiv2.user(user_id)
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
    
    def recent(self, user_id, index=None):
        if index is not None:
            if index > 50 or index <= 0:
                return "Доступны только последние 50 скоров"
        else:
            index = 1
            
        user_scores = self.apiv2.user_scores(user_id, ScoreType.RECENT, include_fails=1, limit=50)
        if len(user_scores) < index:
            # print(len(user_scores))
            # pprint(user_scores)
            return "Скор не найден"
        
        user_score = user_scores[index-1]
        
        b = self.apiv2.beatmap(user_score.beatmap.id)
        return self.score_string(user_score, b)
    
    def top_plays(self, user_id, index=None):
        use_minimal = True
        if index is not None:
            if index > 100 or index <= 0:
                return "Доступны только топ 100 скоров"
            else:
                scores = self.apiv2.user_scores(user_id, ScoreType.BEST, limit=100)[index-1:index]
                use_minimal=False
        else:
            scores = self.apiv2.user_scores(user_id, ScoreType.BEST, limit=100)[:3]
            index = 1
        
        player_name = self.apiv1.get_user(user_id).username
        res = f"Топ скоры игрока {player_name}:\n"
        
        for score in scores:
            b = self.apiv2.beatmap(score.beatmap.id)
            res += f"#{index}"
            index += 1
            if use_minimal:
                res += self.score_string_minimal(score, b)
            else:
                res += self.score_string(score, b)

        return res


if __name__ == "__main__":
    api = Api({"client_id": CLIENT_ID,
               "client_secret": CLIENT_SECRET,
               "api_key": API_KEY})
    # 1402392, 1405981
    # print(api.score_string(9453854, [1402392])[0])
    # print(api.score_string_minimal(9453854, [1402392])[0])
    # pprint(api.apiv2.user_scores(9453854, ScoreType.RECENT, include_fails=1)[0])
    # pprint(api.apiv2.user_scores(9453854, ScoreType.RECENT,)[0])
    # print(api.player_info(9453854))
    print(api.player_info(15400032))
    # print(api.top_plays(9453854))
    # print(api.recent(9453854))
    
    # pprint(vars(api.apiv1.get_user_recent(9453854, 0, 10)[0]))