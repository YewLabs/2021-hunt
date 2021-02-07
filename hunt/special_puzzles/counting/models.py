from django.db import models

from hunt.models import TeamworkSession


class CountingGameState(models.Model):

  session = models.OneToOneField(TeamworkSession, on_delete=models.CASCADE)
  last_count = models.PositiveSmallIntegerField(default=0)
  high_score = models.PositiveSmallIntegerField(default=0)
  npc_chance = models.BinaryField(blank=True)
  npc_threads = models.BinaryField(blank=True)
  npc_memory = models.BinaryField(blank=True)

  def __str__(self):
    return self.session.team.name


class QuizbOwlQuestion(models.Model):

  question = models.CharField(max_length=200, unique=True)
  answer = models.PositiveSmallIntegerField()
