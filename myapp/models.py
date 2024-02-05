from django.db import models

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)

    def __str__(self):
        return self.title
    
class Player(models.Model):
    battleTag = models.CharField(max_length=255)
    last_avatarId = models.CharField(max_length=50)

    def __str__(self):
        return self.battleTag

class GameSetting(models.Model):
    season = models.IntegerField()
    gamemode = models.CharField(max_length=50)
    race = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    stats = models.JSONField(default=dict)  # Use django.db.models.JSONField

    def __str__(self):
        return f"S{self.season}_{self.gamemode}_{self.race} - {self.created_at}"

class Entry(models.Model):
    rank = models.IntegerField()
    mmr = models.IntegerField()
    searchRace = models.CharField(max_length=50)
    race = models.CharField(max_length=50)

    # ForeignKey to GameSetting
    game_setting = models.ForeignKey(GameSetting, on_delete=models.CASCADE, default=1)

    # ManyToManyField to Player
    players = models.ManyToManyField(Player)

    # CharField for avatars
    avatarId = models.CharField(max_length=255)  # You can adjust the max length as needed

    division = models.IntegerField()
    wins = models.IntegerField()
    losses = models.IntegerField()
    draws = models.IntegerField()

    @property
    def player_battle_tags(self):
        return ', '.join(player.battleTag for player in self.players.all())
    
    @property
    def player_avatars(self):
        return ', '.join(player.last_avatarId for player in self.players.all())

    @property
    def season(self):
        return self.game_setting.season
    
    @property
    def gamemode(self):
        return self.game_setting.gamemode

    def __str__(self):
        return f"{self.players.all()} - {self.game_setting}"