""" Used to create the picks page """
import pprint

from tgfp_lib import TGFP, TGFPGame
from tgfp_nfl import TgfpNfl

pp = pprint.PrettyPrinter(indent=4)
tgfp = TGFP()
tgfp_teams = tgfp.teams()
week_no = tgfp.current_week()
nfl = TgfpNfl(week_no=week_no)
nfl_games = nfl.games()


def round_to(number, precision):
    """ rounds a given number to a given precision """
    correction = 0.5 if number >= 0 else -0.5
    return int(number / precision + correction) * precision


def main():
    """ Runs the main method to create the picks page """
    print("Current week: %d" % week_no)
    for nfl_game in nfl_games:
        print("nfl_game_id: " + nfl_game.id)
        print(nfl_game.away_team.full_name)
        road_team_id = nfl_game.away_team.tgfp_id(tgfp_teams)
        home_team_id = nfl_game.home_team.tgfp_id(tgfp_teams)
        print("road_team_id: " + str(road_team_id))
        print(nfl_game.home_team.full_name)
        print("home_team_id: " + str(home_team_id))
        average_spread = nfl_game.average_home_spread()
        print(average_spread)
        if average_spread is None:
            average_spread = 0
        if average_spread < 0:
            if average_spread > -0.5:
                average_spread = -0.5
            favorite_team_id = home_team_id
        elif average_spread > 0:
            average_spread = max(average_spread, 0.5)
            favorite_team_id = road_team_id
        else:
            favorite_team_id = home_team_id
            average_spread = 0.5
        average_spread = round_to(abs(average_spread), .5)
        tgfp_game = TGFPGame(tgfp=tgfp)
        tgfp_game.favorite_team_id = favorite_team_id
        tgfp_game.game_status = nfl_game.status_type

        tgfp_game.home_team_id = home_team_id
        tgfp_game.home_team_score = 0
        tgfp_game.road_team_id = road_team_id
        tgfp_game.road_team_score = 0
        tgfp_game.spread = float(average_spread)
        tgfp_game.start_time = nfl_game.start_time
        tgfp_game.week_no = int(week_no)
        tgfp_game.tgfp_nfl_game_id = nfl_game.id
        tgfp_game.season = tgfp.current_season()
        print("Saving game in mongo database")
        pp.pprint(tgfp_game.mongo_data())
        tgfp_game.save()
        print("")


if __name__ == "__main__":
    main()
