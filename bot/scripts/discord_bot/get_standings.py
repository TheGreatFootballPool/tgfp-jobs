""" Helper module for the bot, retrieves information about standings / scores / picks, etc..  """
from dataclasses import dataclass
from typing import List, Any

import arrow
import hikari
from tgfp_lib import TGFP, TGFPPlayer, TGFPPick, TGFPGame, TGFPTeam

BLANK_SPACE = "<:s_:1024130854185865307>"


@dataclass
class GameCareScore:
    """ Container class for a game, and how much a player cares"""
    game: TGFPGame
    care_score: float
    player_count_against: int
    player_winner_team_id: Any
    is_lock: bool
    is_upset: bool


def get_number_of_against(my_pick: TGFPPick, game: TGFPGame, all_picks: List[TGFPPick]) -> int:
    """ Retrieves the number of players who picked against you"""
    number_of_against: int = 0
    pick: TGFPPick
    for pick in all_picks:
        if pick == my_pick:
            continue
        if pick.winner_for_game_id(game.id) != my_pick.winner_for_game_id(game.id):
            number_of_against += 1
    return number_of_against


def pick_is_lock(pick: TGFPPick, game: TGFPGame) -> bool:
    """ Is the pick a lock? """
    return pick.lock_team_id in (game.home_team_id, game.road_team_id)


def pick_is_upset(pick: TGFPPick, game: TGFPGame) -> bool:
    """ Is the pick an upset?"""
    return pick.upset_team_id in (game.home_team_id, game.road_team_id)


def get_game_care_scores_for_player(player: TGFPPlayer, tgfp: TGFP) -> List[GameCareScore]:
    """ Retrieves the game scores for a given player """
    all_picks: List[TGFPPick] = tgfp.find_picks(week_no=tgfp.current_week())
    all_games: List[TGFPGame] = tgfp.find_games(week_no=tgfp.current_week())

    care_scores: List[GameCareScore] = []
    game: TGFPGame
    for game in all_games:
        pick: TGFPPick = player.this_weeks_picks()
        number_against: int = get_number_of_against(pick, game, all_picks)
        number_of_picks: int = len(all_picks) - 1  # me
        score: float = round((number_against / number_of_picks), 2)
        winner_team_id = pick.winner_for_game_id(game.id)
        is_lock: bool = pick_is_lock(pick, game)
        is_upset: bool = pick_is_upset(pick, game)
        care_scores.append(
            GameCareScore(
                game=game,
                care_score=score,
                player_count_against=number_against,
                player_winner_team_id=winner_team_id,
                is_lock=is_lock,
                is_upset=is_upset
            )
        )
    return care_scores


def star_string_for_care_score(care: GameCareScore) -> str:
    """ Retrieves a string formatted for discord display """
    if 0 < care.care_score < 0.1:
        stars = 1
    else:
        stars = round(care.care_score / .2)
    star_string: str = ""
    for _ in range(stars):
        star_string += ':star:'
    return star_string


def formatted_care(care_scores: List[GameCareScore], tgfp: TGFP) -> str:
    """ Retrieves the care score formatted for discord """
    output: str = ""
    for care in care_scores:
        star_string = star_string_for_care_score(care)
        road_team: TGFPTeam = tgfp.find_teams(care.game.road_team_id)[0]
        home_team: TGFPTeam = tgfp.find_teams(care.game.home_team_id)[0]
        road_team_emoji: str = road_team.discord_emoji
        home_team_emoji: str = home_team.discord_emoji
        output += f"{road_team_emoji} @ {home_team_emoji} {star_string}\n"

    output += "\n> Type `/help` for more information"
    return output


def game_status_string(care: GameCareScore, road_team_emoji, home_team_emoji) -> str:
    """
    Returns a string for the current game status

    if the game is 'pregame' then it's kickoff time
    if it's in game then it's the current score
    if it's post game, then it's the final score + if you won / lost
    """
    game_status: str = ""
    status = "pregame"
    if not care.game.is_pregame:
        status = "final" if care.game.is_final else "live"
    match status:
        case "pregame":
            local_time = arrow.get(care.game.start_time).to('US/Pacific')
            formatted_time = local_time.format("ddd @ h:mma ZZZ")
            game_status = f"> **Kickoff**: *{formatted_time}*"
        case "live":
            game_status = f"> **Game Is LIVE:**\n" \
                          f"> Score: {road_team_emoji}({care.game.road_team_score}) " \
                          f"@ {home_team_emoji}({care.game.home_team_score})"
        case "final":
            game_status = f"> **Final Score**: {road_team_emoji}({care.game.road_team_score}) @ \
            {home_team_emoji}({care.game.home_team_score})"
    return game_status


def pick_detail_embed(care_scores: List[GameCareScore], tgfp: TGFP) -> hikari.Embed:
    # pylint: disable=too-many-locals
    """ Returns the pick details in a discord embed """
    description: str = "More detailed information about each of your picks for the week\n"
    description += ":lock: == Lock\n"
    description += ":fingers_crossed: == Upset\n"
    detail_embed: hikari.Embed = hikari.Embed(
        title="Pick Details",
        description=description
    )
    for care in care_scores:
        road_team: TGFPTeam = tgfp.find_teams(care.game.road_team_id)[0]
        home_team: TGFPTeam = tgfp.find_teams(care.game.home_team_id)[0]
        favored_team: TGFPTeam = tgfp.find_teams(care.game.favorite_team_id)[0]
        picked_winner: TGFPTeam = tgfp.find_teams(care.player_winner_team_id)[0]
        spread: int = care.game.spread
        road_team_emoji: str = road_team.discord_emoji
        home_team_emoji: str = home_team.discord_emoji
        picked_winner_emoji: str = picked_winner.discord_emoji
        favored_team_name: str = favored_team.long_name
        picked_winner_name: str = picked_winner.long_name
        lock_str: str = ":lock:" if care.is_lock else ""
        upset_str: str = ":fingers_crossed:" if care.is_upset else ""
        game_status = game_status_string(care, road_team_emoji, home_team_emoji)
        value_string: str = f"**{home_team_emoji} {home_team.long_name} @ " \
                            f"{road_team_emoji} {road_team.long_name}**\n"
        value_string += "__Game Information__\n"
        value_string += f"> **Line:** {favored_team_name} favored by {spread}\n"
        value_string += f"{game_status}\n"
        value_string += f"> **Your Pick:** {picked_winner_emoji} " \
                        f"{picked_winner_name} {lock_str} {upset_str}\n"
        value_string += f"> **Care Score:** {star_string_for_care_score(care)}"

        detail_embed.add_field(
            name="────────",
            value=value_string
        )
    return detail_embed


def length_of_city(tgfp: TGFP) -> int:
    """ Returns the length of the city"""
    max_length: int = 0
    for team in tgfp.teams():
        max_length = max(len(team.city), max_length)
    return max_length


def length_of_short_name(tgfp: TGFP) -> int:
    """ Returns the length of a team's short name """
    max_length: int = 0
    for team in tgfp.teams():
        max_length = max(len(team.short_name), max_length)
    return max_length
