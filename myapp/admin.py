
from django.contrib import admin
from .models import *

from django import forms
from django.utils.safestring import mark_safe
from django.contrib.admin.widgets import FilteredSelectMultiple

class EntryForm(forms.ModelForm):
    class Meta:
        model = Entry
        fields = '__all__'
        widgets = {
            'players': FilteredSelectMultiple('Players', is_stacked=False),
        }

class EntryAdmin(admin.ModelAdmin):
    form = EntryForm
    list_display = ('player_battle_tags', 'game_setting', 'avatarId','rank', 'mmr', 'race', 'division', 'wins', 'losses', 'draws')
    list_filter = ('game_setting', 'race', 'division')

    def player_battle_tags(self, obj):
        return ', '.join(player.battleTag for player in obj.players.all())

    player_battle_tags.short_description = 'Player Battle Tags'
    
class GameSettingAdmin(admin.ModelAdmin):
    list_display = ('__str__',)  # Assuming you have __str__ method in GameSetting model
    list_filter = ('created_at', "season", "race", "gamemode")

class PlayerAdmin(admin.ModelAdmin):
    list_display = ('battleTag', 'last_avatarId')  # Adjust the fields as needed
    search_fields = ('battleTag',)  # Add fields you want to be searchable
    list_filter = ('last_avatarId',)  # Add filters as needed

admin.site.register(Book)
admin.site.register(Entry, EntryAdmin)
admin.site.register(GameSetting, GameSettingAdmin)
admin.site.register(Player, PlayerAdmin)

