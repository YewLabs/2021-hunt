from django.conf import settings

from spoilr.models import Interaction, Team, PuzzleAccess, Puzzle

def submission_instructions(interaction, team, include_prefix=True):
    if settings.POSTHUNT:
        answer = interaction.puzzle.answer
        if interaction.url == 'squee-squee':
            answer = 'PIGPEN PALS'
        return 'During the hunt, teams emailed their submissions to HQ and received the answer <span class="answer spoiler">%s.</span>' % answer
    to = 'submission@%s' % (settings.DEFAULT_DOMAIN)
    subject = "%s for %s" % (interaction.email_key, team.username)
    if not include_prefix:
        return '<a href="mailto:%s?subject=%s" target="_blank">%s</a> with the subject "%s".' % (to, subject, to, subject)
    prefix = 'Send your submission to'
    if interaction.name.endswith(' Puzzle'):
        prefix = 'When you’re ready for this puzzle, contact us at'
    return '%s <a href="mailto:%s?subject=%s" target="_blank">%s</a> with the subject "%s".' % (prefix, to, subject, to, subject)

def puzzle_found(team, puzzle):
    from spoilr.actions import release_interaction
    for interaction in Interaction.objects.filter(puzzle=puzzle, unlock_type='FOUND'):
        release_interaction(team, interaction, 'found "%s"' % (puzzle.name))

def puzzle_solved(team, puzzle):
    from spoilr.actions import release_interaction
    for interaction in Interaction.objects.filter(puzzle=puzzle, unlock_type='SOLVED'):
        release_interaction(team, interaction, 'solved "%s"' % (puzzle.name))

    if puzzle.is_meta:
        totalMetas = Puzzle.objects.filter(is_meta=True).count()
        if team.solved_puzzles.filter(is_meta=True).count() == totalMetas:
            interaction = Interaction.objects.get(url='endgame')
            release_interaction(team, interaction, 'solved all metas')
