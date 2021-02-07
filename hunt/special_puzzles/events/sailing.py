import datetime

from django.db import models

from django.forms import ModelForm
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.clickjacking import xframe_options_sameorigin

from spoilr.decorators import require_admin, require_team
from spoilr.models import Team, now


TIME_SLOTS = [
    timezone.make_aware(datetime.datetime(
        year=2021, month=1, day=15, hour=hour, minute=0,))
    for hour in [18, 19, 20, 21]]


class SailingTeamData(models.Model):
  team = models.ForeignKey(Team, on_delete=models.CASCADE)
  name = models.CharField(max_length=40, blank=False)
  email = models.EmailField()
  registered_time = models.DateTimeField(null=True, blank=True)
  available_1900 = models.BooleanField(default=False)
  available_2000 = models.BooleanField(default=False)
  available_2100 = models.BooleanField(default=False)

  def __str__(self):
    out = ['[%s%s%s]' % ('7' if self.available_1900 else '-',
                         '8' if self.available_2000 else '-',
                         '9' if self.available_2100 else '-',),
           self.name,
           f'({self.email})',
           f'<{str(self.team)}>']
    return ' '.join(out)


@require_team
@xframe_options_sameorigin
def register_view(request):
  error = None
  if request.method == 'POST':
    my_registration, created = SailingTeamData.objects.get_or_create(
        team=request.team, email=request.POST['email'])
    if created:
      time_slots = request.POST.getlist('times')
      my_registration.name = request.POST['name']
      my_registration.available_1900 = ('slot-7' in time_slots)
      my_registration.available_2000 = ('slot-8' in time_slots)
      my_registration.available_2100 = ('slot-9' in time_slots)
      my_registration.registered_time = now()
      my_registration.save()
    elif my_registration.name == request.POST['name']:
      # User wants to unregister
      my_registration.delete()
    else:
      # Name x Email pair mismatch
      error = 'Matching name-email pair required for deregistration.'
  all_registrations = SailingTeamData.objects.filter(team=request.team)
  return render(request, 'hunt/special_puzzles/events/sailing.html', {
      'data': [{
          'name': reg.name,
          'slot_7': reg.available_1900,
          'slot_8': reg.available_2000,
          'slot_9': reg.available_2100,
          'time': reg.registered_time,
      } for reg in all_registrations],
      'error': error,
      'slots': TIME_SLOTS,
      'now': now(),
  })

@require_admin
@xframe_options_sameorigin
def admin_view(request):
  # TODO: Make this show some processed scheduling data instead of just the raw
  all_registrations = SailingTeamData.objects.all()
  team_count = SailingTeamData.objects.aggregate(
      models.Count('team', distinct=True))
  return render(request, 'hunt/special_puzzles/events/sailing-admin.html', {
      'data': [{
          'team_username': reg.team.username,
          'name': reg.name,
          'email': reg.email,
          'slot_7': reg.available_1900,
          'slot_8': reg.available_2000,
          'slot_9': reg.available_2100,
      } for reg in all_registrations],
      'slots': TIME_SLOTS,
      'team_count': team_count['team__count'],
  })
