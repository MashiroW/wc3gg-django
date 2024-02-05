import os
import csv
import ast
import json
from datetime import datetime
from django.core.management.base import BaseCommand
from myapp.models import GameSetting, Player, Entry
from django.db.models import Max
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.http import JsonResponse
from collections import defaultdict
from tqdm import tqdm

class Command(BaseCommand):
    help = 'Load players from CSV file or folder'

    def add_arguments(self, parser):
        parser.add_argument('csv_file_path', type=str, help='Path to the CSV file or folder')

    def handle(self, *args, **options):
        csv_file_path = options['csv_file_path']

        if os.path.isfile(csv_file_path):
            # If it's a file, process the single file
            self.process_csv(csv_file_path)
        elif os.path.isdir(csv_file_path):
            # If it's a folder, process all CSV files in the folder
            for filename in os.listdir(csv_file_path):
                if filename.endswith(".csv"):
                    file_path = os.path.join(csv_file_path, filename)
                    self.process_csv(file_path)
        else:
            self.stdout.write(self.style.ERROR(f"Invalid path: {csv_file_path}"))

    def process_csv(self, csv_file_path):
        _, filename = os.path.split(csv_file_path)
        parts = filename.split('_')
        season_str = parts[1][1:]
        season = int(season_str)

        gamemode = parts[2]
        race = parts[3][:-4]

        if race not in ["N-A", "all"]:
            return

        if race == "N-A":
            race = "all"

        current_datetime = datetime.now()
        game_setting = GameSetting.objects.create(
            season=season,
            gamemode=gamemode,
            race=race,
            created_at=current_datetime
        )

        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            # Calculate the total number of rows for tqdm
            total_rows = sum(1 for _ in reader)
            file.seek(0)  # Reset file pointer to the beginning
            # Use tqdm as a context manager to create a progress bar
            with tqdm(total=total_rows, desc=f"Processing {filename}") as pbar:
                for row in reader:
                    try:
                        battleTag_list = ast.literal_eval(row['battleTag'])
                        avatarId_list = ast.literal_eval(row['avatarId'])
                        players = []

                        for i in range(len(battleTag_list)):
                            try:
                                player, created = Player.objects.get_or_create(
                                    battleTag=battleTag_list[i]
                                )

                                player.last_avatarId = avatarId_list[i]
                                player.save()

                            except Player.DoesNotExist:
                                player = Player.objects.create(
                                    battleTag=battleTag_list[i],
                                    last_avatarId=avatarId_list[i]
                                )                      

                            players.append(player)

                        row.pop('toonname', None)
                        row.pop('battleTag', None)

                        entry = Entry.objects.create(
                            game_setting=game_setting,
                            **row
                        )
                        
                        entry.players.set(players)

                        pbar.update(1)  # Update progress bar

                    except Exception as e:
                        continue                         

        game_setting.stats = get_distribution(season)
        game_setting.save()


def get_distribution(season):
    player_entries = Entry.objects.filter(game_setting__season=season)

    division_names = {
        1: 'Unranked',
        2: 'Combatant',
        3: 'Challenger',
        4: 'Rival',
        5: 'Duelist',
        6: 'Elite',
        7: 'Gladiator',
        8: 'Champion',
    }

    distribution_data = defaultdict(lambda: {'division_distribution': {division_names[i]: 0 for i in range(1, 9)}, 'games_played': 0})

    for entry in player_entries:
        gamemode = entry.gamemode
        distribution_data[gamemode]['games_played'] += entry.wins + entry.losses

        division = entry.division
        distribution_data[gamemode]['division_distribution'][division_names[division]] += 1

    return json.dumps(distribution_data)
