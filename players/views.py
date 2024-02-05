from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from myapp.models import *
from django.shortcuts import render
from django.db.models import Count
from django.db.models import Max

def player_profile(request, username=None, tag=None):
    print("IM INSIDE !")
    # Combine username and tag to form battleTag
    battle_tag = f"{username}#{tag}"
    
    # Fetch player data
    player = get_object_or_404(Player, battleTag=battle_tag)

    # Add any additional logic to fetch and pass player data to the template
    return render(request, 'players/player_profile.html', {'player': player})

def get_player_data(request):
    # Get BattleTag from the request
    username = request.GET.get('username')
    tag = request.GET.get('tag')
    battle_tag = f"{username}#{tag}"

    # Find the corresponding Player object
    player = get_object_or_404(Player, battleTag=battle_tag)

    # Get player entries, filter by the specified player, and order by season number (descending)
    player_entries = Entry.objects.filter(
        players=player
    ).order_by('-game_setting__season')

    # Create a list of dictionaries containing entry information
    entries_data = [
        {
            'rank': entry.rank,
            'mmr': entry.mmr,
            'race': entry.race,
            'wins': entry.wins,
            'losses': entry.losses,
            'division': entry.division,
            'draws': entry.draws,
            'season': entry.game_setting.season,
            'gamemode': entry.game_setting.gamemode,
            'player_battle_tags': entry.player_battle_tags,
            'player_avatars': entry.player_avatars,
            'created_at': entry.game_setting.created_at
        }
        for entry in player_entries
    ]

    # Return JSON response with player entries data
    return JsonResponse(entries_data, safe=False)

def get_player_summary(player_entries):
    summary_rows = {
        'Lifetime Games Played': calculate_lifetime_games_played(player_entries),
        'Lifetime Win/Loss Ratio': calculate_lifetime_win_loss_ratio(player_entries),
        'Most Played Race': calculate_most_played_race(player_entries),
        'Most Played Gamemode': calculate_most_played_gamemode(player_entries),
        'Current Highest Rank': get_highest_rank_image_path(player_entries)
    }

    return summary_rows

# Helper functions

def calculate_lifetime_games_played(player_entries):
    return sum(entry['wins'] + entry['losses'] for entry in player_entries)

def calculate_lifetime_win_loss_ratio(player_entries):
    total_wins = sum(entry['wins'] for entry in player_entries)
    total_losses = sum(entry['losses'] for entry in player_entries)
    
    if total_losses == 0:
        return '∞'
    
    return round(total_wins / total_losses, 2)

def calculate_most_played_race(player_entries):
    race_counts = {}
    
    for entry in player_entries:
        race = entry['race'].lower()
        race_counts[race] = race_counts.get(race, 0) + 1
    
    return max(race_counts, key=race_counts.get)

def calculate_most_played_gamemode(player_entries):
    gamemode_counts = {}
    
    for entry in player_entries:
        gamemode = entry['gamemode'].lower()
        gamemode_counts[gamemode] = gamemode_counts.get(gamemode, 0) + 1
    
    return max(gamemode_counts, key=gamemode_counts.get)

def get_highest_rank_image_path(player_entries):
    highest_season = get_highest_season_number()
    
    if not highest_season:
        # If there's no season data, return a default image path
        return '/static/myapp/common/img/Ranked/full_size/rankedBadge_0.png'
    
    highest_season_entries = [entry for entry in player_entries if entry['season'] == highest_season]
    
    if not highest_season_entries:
        # If there are no entries for the highest season, return a default image path
        return '/static/myapp/common/img/Ranked/full_size/rankedBadge_0.png'
    
    highest_mmr_entry = max(highest_season_entries, key=lambda entry: entry['mmr'])
    division_image_path = f'/static/myapp/common/img/Ranked/full_size/rankedBadge_{highest_mmr_entry["division"]}.png'
    
    return division_image_path

def get_highest_season_number(request):
    highest_season = GameSetting.objects.aggregate(Max('season'))['season__max']
    return JsonResponse({'highest_season': highest_season} if highest_season is not None else {'highest_season': 0})