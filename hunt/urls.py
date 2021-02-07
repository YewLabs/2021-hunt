from django.urls import path, re_path, include
from django.conf import settings

import hunt.views as views

import hunt.sample_puzzle

from hunt.special_puzzles import puzzle179, puzzle271, puzzle277, puzzle281, puzzle292, puzzle566, puzzle573, puzzle206, puzzle434, puzzle407
from hunt.special_puzzles.puzzle69 import puzzle69
from hunt.special_puzzles.events import archery, bonus, fencing, pistol, sailing

# Dynamic Puzzles
urlpatterns = [
    re_path('^puzzle/(?P<puzzle>cool_dynamic_puzzle)/dynamic$', hunt.sample_puzzle.cool_dynamic_view),
    re_path('^puzzle/(?P<puzzle>random-hall)/dynamic$', puzzle292.puzzle292_view),
    re_path('^puzzle/(?P<puzzle>cafe-five)/dynamicx$', puzzle179.puzzle179_handle_cafe_msg),
    re_path('^puzzle/dating-sim/check$', puzzle271.puzzle271_check),
    re_path('^puzzle/dating-sim/check_final$', puzzle271.puzzle271_final_scene),
    re_path('^puzzle/(?P<puzzle>infinite-corridor-simulator)/dynamic/(?P<iid>[0-9]+)$', puzzle566.puzzle566_data),
    re_path('^puzzle/(?P<puzzle>make-your-own-wordsearch)/dynamic/(?P<iid>[0-9]+)$', puzzle281.puzzle281_solve),
    re_path('^puzzle/(?P<puzzle>make-your-own-wordsearch)/lookup$', puzzle281.puzzle281_lookup),
    re_path('^puzzle/(?P<puzzle>dna)/dynamic$', puzzle573.puzzle573_view),
    re_path('^puzzle/(?P<puzzle>oh-the-places-youll-go)/dynamic$', puzzle434.puzzle434_view),
    re_path('^puzzle/(?P<puzzle>bingo)/dynamic$', puzzle69.puzzle69_view),
    re_path('^puzzle/(?P<puzzle>so-you-think-you-can-count)/leaderboard$', puzzle277.leaderboard_view),
    re_path('^puzzle/archery/register$', archery.register_view),
    re_path('^puzzle/bonus/register$', bonus.register_view),
    re_path('^puzzle/fencing/register$', fencing.register_view),
    re_path('^puzzle/fencing/casual_register$', fencing.casual_register_view),
    re_path('^puzzle/fencing/tourney_register$', fencing.tourney_register_view),
    re_path('^puzzle/fencing/admin$', fencing.admin_view),
    re_path('^puzzle/pistol/register$', pistol.register_view),
    re_path('^puzzle/sailing/register$', sailing.register_view),
    re_path('^puzzle/sailing/admin$', sailing.admin_view),
    re_path('^puzzle/(?P<puzzle>bracketeering)/dynamic$', puzzle206.puzzle206_view),
    re_path('^puzzle/(?P<puzzle>✏)/dynamic$', puzzle407.puzzle407_view),
]

urlpatterns += [
    re_path('^puzzle/(?P<puzzle>[^/]+)/$', views.puzzle_view, name='puzzle_view'),
    re_path('^puzzle/(?P<puzzle>[^/]+)/solution/$', views.solution_view, name='puzzle_solution'),
    re_path('^puzzle/(?P<puzzle>[^/]+)/canned_hints/$', views.hints_view, name='puzzle_hints'),
    re_path('^puzzle/(?P<puzzle>[^/]+)/(?P<resource>.*)$', views.local_puzzle_asset_view),
    re_path('^srpuzzle/(?P<puzzle>[^/]+)/(?P<resource>.*)$', views.puzzle_asset_view),
    re_path('^round/(?P<round>[^/]+)/$', views.round_view, name='round_view'),
    re_path('^round/(?P<round>[^/]+)/solution/$', views.round_solution_view, name='round_solution'),
    re_path('^round/(?P<round>[^/]+)/(?P<resource>.*)$', views.round_asset_view),
    re_path('^projection_device$', views.mmo_view, name='mmo'),
    re_path('^device_message/$', views.mmo_message_view, name='device_message'),
    re_path('^$', views.top_view, name='top'),
    re_path('^puzzles$', views.all_view, name='all'),
    re_path('^prelaunch$', views.prelaunch_view, name='prelaunch'),
    re_path('^faq$', views.faq_view, name='faq'),
    re_path('^updates$', views.updates_view, name='updates'),
    re_path('^story$', views.storylog_view, name='story'),
    re_path('^postmeta$', views.pmis_view, name='postmeta'),
    re_path('^events$', views.eventschedule_view, name='events'),
    re_path('^sponsors$', views.sponsors_view, name='sponsors'),
    re_path('^statistics$', views.statistics_view, name='statistics'),
    re_path('^credits$', views.credits_view, name='credits'),
    re_path('^log$', views.completelog_view, name='log'),
    re_path('^assets/(?P<asset_path>.+)', views.global_asset_view, name='asset'),
    re_path('^unlock$', views.unlock, name='unlock'),
    re_path('^hq/tick$', views.global_tick),
    re_path('^set_mmo_version/$', views.set_mmo_version, name='set_mmo_version'),
    re_path('^get_mmo_version/$', views.get_mmo_version, name='get_mmo_version'),
    re_path('^get_teams/$', views.get_teams, name='get_teams'),
    re_path('^set_unlock_state/$', views.set_unlock_state),
    re_path('^find_puzzle/(?P<puzzle>[^/]+)/(?P<puzzle_id>[^/]+)/$', views.find_puzzle_view, name='find_puzzle'),
    re_path('^admin_find_puzzle/(?P<team_url>[^/]+)/(?P<puzzle_url>[^/]+)/$', views.admin_find_view, name='admin_find'),
    re_path('^register_discord/(?P<discord_id>[^/]+)/$', views.register_discord_view, name='register_discord'),
    re_path('^remove_discord/$', views.remove_discord_view, name='remove_discord'),
    re_path('^lookup_discord/$', views.lookup_discord_view, name='lookup_discord'),
    re_path('^endgame/(?P<team_url>[^/]+)/$', views.endgame_view, name='endgame'),
    re_path('^endgame$', views.endgame_puzzle_view, name='endgame_puzzle'),
    re_path('^endgame_solution$', views.endgame_solution_view, name='endgame_solution'),
]
