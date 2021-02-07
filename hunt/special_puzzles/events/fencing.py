import datetime

from django.db import models
from django.forms import ModelForm
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.clickjacking import xframe_options_sameorigin

from spoilr.decorators import require_team, require_admin
from spoilr.models import Team, now

REGISTER_CUTOFF = timezone.make_aware(datetime.datetime(
    year=2021,
    month=1,
    day=16,
    hour=16,
    minute=30,
))

class FencingTeamData(models.Model):
    team = models.OneToOneField(Team, on_delete=models.CASCADE)
    registered = models.BooleanField(default=False)
    registered_time = models.DateTimeField(null=True, blank=True)
    url = models.CharField(max_length=100, blank=True)

    def __str__(self):
        out = str(self.team)
        if self.registered: out += ': registered'
        if self.url: out += ' (%s)' % self.url
        return out


class FencingTeamCasualData(models.Model):
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
def register_view(request, extra_context=None):
    casual_data = FencingTeamCasualData.objects.filter(team=request.team)
    tourney_data, _ = FencingTeamData.objects.get_or_create(team=request.team)
    context = {
        'casual_data': casual_data,
        'tourney_data': tourney_data,
        'cutoff': REGISTER_CUTOFF,
        'now': now(),
    }
    if extra_context:
        context.update(extra_context)
    return render(request, 'hunt/special_puzzles/events/fencing.html', context)

@require_team
@xframe_options_sameorigin
def tourney_register_view(request):
    tourney_data, _ = FencingTeamData.objects.get_or_create(team=request.team)
    tourney_data.registered = bool(request.POST['registered'])
    if not tourney_data.registered_time:
        tourney_data.registered_time = now()
    tourney_data.save()
    return register_view(request)

@require_team
@xframe_options_sameorigin
def casual_register_view(request):
    new_registration = False
    error = None
    casual_data = FencingTeamCasualData.objects.filter(team=request.team)

    my_registration, created = FencingTeamCasualData.objects.get_or_create(
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
    return register_view(request, extra_context={
        'new_registration': new_registration,
        'error': error,
    })

@require_admin
@xframe_options_sameorigin
def admin_view(request):
    registered = list(FencingTeamData.objects
                      .filter(registered=True)
                      .order_by('registered_time')
                      .select_related('team'))
    if request.method == 'POST' and 'data' in request.FILES:
        upload = request.FILES['data'].read().decode('utf-8').strip().split('\n')
        print(upload)
        urls = dict(line.split(',')[:2] for line in upload)
        for data in registered:
            data.url = urls.get(str(data.team_id), '')
            data.save()
    data = '\n'.join('%s,%s,%s' % (data.team.id, data.team.name, data.registered_time) for data in registered)
    return render(request, 'hunt/special_puzzles/events/fencing-admin.html', {'data': data})
