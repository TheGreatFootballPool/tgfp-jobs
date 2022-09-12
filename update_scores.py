""" This file will update all the scores in the mongo DB for the great football pool """
import pprint
from datetime import datetime
import pytz
from tgfp_lib import TGFP, TGFPGame
from tgfp_nfl import TgfpNfl


def main():
    """ This is the function runs the entire module. """
    pretty_printer = pprint.PrettyPrinter(indent=4)
    tgfp = TGFP()
    week_no = tgfp.current_week()
    nfl = TgfpNfl(week_no=week_no)
    nfl_games = nfl.games()
    all_games_are_final = True

    for nfl_game in nfl_games:
        tgfp_g: TGFPGame = tgfp.find_games(tgfp_nfl_game_id=nfl_game.id)[0]
        # if nfl_game.status_type == "postponed":
        #     continue
        if not nfl_game.is_pregame:
            print("Games are in progress")
            if tgfp_g:
                if tgfp_g.home_team_score != int(nfl_game.total_home_points) or \
                   tgfp_g.road_team_score != int(nfl_game.total_away_points) or \
                   tgfp_g.game_status != nfl_game.game_status_type:
                    tgfp_g.home_team_score = int(nfl_game.total_home_points)
                    tgfp_g.road_team_score = int(nfl_game.total_away_points)
                    tgfp_g.game_status = nfl_game.game_status_type
                    print("saving a game score")
                    pretty_printer.pprint(tgfp_g.mongo_data())
                if nfl_game.is_final:
                    print("Score is final")
                        # bot_sender.alert_game_id_final(tgfp_g.id)
        extra_info = tgfp_g.extra_info
        now = datetime.now()
        timestamp = now.astimezone(pytz.timezone('US/Pacific')).strftime('%Y-%m-%d %H:%M:%S %Z')

        extra_info['status_check'] = timestamp
        tgfp_g.save()

        if not nfl_game.is_final:
            all_games_are_final = False

    if all_games_are_final:
        print("all games are final")


if __name__ == "__main__":
    main()
