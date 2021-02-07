import datetime

from django.db import models

from django.forms import ModelForm
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.clickjacking import xframe_options_sameorigin

from spoilr.decorators import require_admin, require_team
from spoilr.models import Team, now


class BonusEventTeamData(models.Model):
  team = models.ForeignKey(Team, on_delete=models.CASCADE)
  name = models.CharField(max_length=40, blank=False)
  email = models.EmailField()
  registered_time = models.DateTimeField(null=True, blank=True)

  def __str__(self):
    out = [self.name,
           f'({self.email})',
           f'<{str(self.team)}>']
    return ' '.join(out)


@require_team
@xframe_options_sameorigin
def register_view(request):
  new_registration = False
  error = None
  if request.method == 'POST':
    my_registration, created = BonusEventTeamData.objects.get_or_create(
        team=request.team, email=request.POST['email'])
    if created:
      my_registration.name = request.POST['name']
      my_registration.registered_time = now()
      my_registration.save()
      new_registration = True
    elif my_registration.name == request.POST['name']:
      # User wants to unregister
      my_registration.delete()
    else:
      # Name x Email pair mismatch
      error = 'Matching name-email pair required for deregistration.'
  all_registrations = BonusEventTeamData.objects.filter(team=request.team)
  return render(request, 'hunt/special_puzzles/events/bonus.html', {
      'data': [{
          'name': reg.name,
          'time': reg.registered_time,
      } for reg in all_registrations],
      'error': error,
      'now': now(),
      'new_registration': new_registration,
  })
