"""This is a 'do everything' script for updating the scores in mongo."""

# pylint: disable=import-error
# pylint: disable=no-name-in-module
from config import get_config
from update_scores import main as update_scores
from mongo_backup import main as backup_db
from update_win_loss import main as update_win_loss


config = get_config()


def main():
    """Execute the steps in order necessary to update everything"""
    backup_db()
    update_scores()
    update_win_loss()


if __name__ == "__main__":
    main()
