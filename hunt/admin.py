from hunt.special_puzzles.events.sailing import SailingTeamData
from hunt.special_puzzles.events.archery import ArcheryTeamData
from hunt.special_puzzles.events.pistol import PistolTeamData
from hunt.special_puzzles.events.bonus import BonusEventTeamData
from hunt.special_puzzles.puzzle593 import Puzzle593TeamData
from hunt.special_puzzles.puzzle617 import Puzzle617TeamData
from hunt.special_puzzles.counting.models import *  # puzzle277
from django.contrib import admin
from django import forms
from .models import *
from spoilr.admin import noInfinite

class Y2021TeamDataAdmin(admin.ModelAdmin):
    list_display = ['team', 'tempest_id', 'emoji', 'base_juice']
    search_fields = ['team__name']

admin.site.register(Y2021TeamData, Y2021TeamDataAdmin)

from django.contrib.admin import SimpleListFilter

class NoInfiniteFilter(SimpleListFilter):
    title = ''

    parameter_name = ''

    def lookups(self, request, model_admin):
        return (
            ('all', 'All'),
        )

    def queryset(self, request, queryset):
        return (queryset.exclude(puzzle__round__url='infinite') | queryset.filter(puzzle__round__url='infinite', puzzle__is_meta=True))


class Y2021PuzzleDataAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        return (super(Y2021PuzzleDataAdmin, self)
            .get_queryset(request)
            .select_related('puzzle', 'puzzle__round', 'required_available_puzzle', 'required_available_puzzle__round', 'parent', 'parent__round'))

    def render_change_form(self, request, context, *args, **kwargs):
        context['adminform'].form.fields['puzzle'].queryset = noInfinite(Puzzle.objects)
        context['adminform'].form.fields['required_available_puzzle'].queryset = noInfinite(Puzzle.objects)
        context['adminform'].form.fields['parent'].queryset = Puzzle.objects.filter(round__url='infinite-template').select_related('round')
        return super(Y2021PuzzleDataAdmin, self).render_change_form(request, context, *args, **kwargs)

    def puzzle_name(data):
        return '%s (%s)' % (data.puzzle.name, data.puzzle.round.name)
    puzzle_name.short_description = 'Puzzle Name'
    list_filter = [NoInfiniteFilter, 'puzzle__round__name']
    list_display = [puzzle_name, 'points_req', 'feeder_req', 'feeder_tag', 'unlock_time', 'unlock_req']
    search_fields = ['puzzle__name']
    ordering = ['puzzle__round__order', 'puzzle__order']

admin.site.register(Y2021PuzzleData, Y2021PuzzleDataAdmin)

class Y2021RoundDataAdmin(admin.ModelAdmin):
    def round_name(data):
        return data.puzzle.name
    list_display = ['round', 'points_required']
    ordering = ['round__order']

admin.site.register(Y2021RoundData, Y2021RoundDataAdmin)

class Y2021SettingsAdmin(admin.ModelAdmin):
    list_display = ['name']

admin.site.register(Y2021Settings, Y2021SettingsAdmin)

class MMOUnlockAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        return (super(MMOUnlockAdmin, self)
            .get_queryset(request)
            .select_related('puzzle', 'puzzle__round', 'round', 'interaction'))

    def render_change_form(self, request, context, *args, **kwargs):
        context['adminform'].form.fields['puzzle'].queryset = noInfinite(Puzzle.objects)

        return super(MMOUnlockAdmin, self).render_change_form(request, context, *args, **kwargs)

    list_display = ['unlock_id', 'description', 'puzzle', 'round', 'juice', 'force']

admin.site.register(MMOUnlock, MMOUnlockAdmin)

class JuiceBoxAdmin(admin.ModelAdmin):
    list_filter = ['round']
    list_display = ['__str__', 'unlock_time', 'active']

admin.site.register(JuiceBox, JuiceBoxAdmin)

class JuiceScheduleAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'active', 'students_juice', 'green_juice', 'real_infinite_juice', 'nano_juice', 'stata_juice', 'clusters_juice', 'tunnels_juice']
    ordering = ['-timestamp']
admin.site.register(JuiceSchedule, JuiceScheduleAdmin)

admin.site.register(KtaneTeamData)
admin.site.register(KtaneHighScoreData)
admin.site.register(Puzzle179TeamData)
admin.site.register(Puzzle593TeamData)
admin.site.register(Puzzle617TeamData)
admin.site.register(CountingGameState)
admin.site.register(FencingTeamData)
admin.site.register(BoggleTeamData)
admin.site.register(BoggleHighScoreData)
admin.site.register(SailingTeamData)
admin.site.register(ArcheryTeamData)
admin.site.register(PistolTeamData)
admin.site.register(BonusEventTeamData)
