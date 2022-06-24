from django.shortcuts import render
from django.views.generic import ListView
from django.views.generic.edit import CreateView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.dispatch import receiver
from django.db.models import Q
from ranking.models import Match
from django.forms import ModelForm, DateInput
from allauth.account.signals import user_signed_up


class DateInput(DateInput):
    input_type = 'date'


class AddMatchForm(ModelForm):
    class Meta:
        model = Match
        fields = '__all__'
        widgets = {
            'date': DateInput(format='%d%m%Y')
        }


class AddMatchView(SuccessMessageMixin, CreateView):
    form_class = AddMatchForm
    model = Match
    success_url = reverse_lazy('index')
    success_message = "Partida adicionada com sucesso!"


@receiver(user_signed_up)
def populate_profile(sociallogin, user, **kwargs):
    if sociallogin.account.provider == 'google':
        user_data = user.socialaccount_set.filter(provider='google')[0].extra_data
        name = user_data['name']
    user.name = name
    user.save()


class UserGamesView(ListView):
    model = Match
    template_name = 'user_games.html'

    def get_queryset(self):
        if self.request.user.is_authenticated:
            user = self.request.user
        else:
            user = None
        return Match.objects.filter(Q(winner=user) | Q(loser=user))



class RankingView(ListView):
    model = Match
    template_name = 'ranking.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        matches = self.get_queryset()
        ranking = {}
        for match in matches:
            for result in ['winner', 'loser']:
                if result == 'winner':
                    name = match.winner.name
                else:
                    name = match.loser.name

                if name not in ranking:
                    ranking[name] = {
                        'name': name,
                        'matches': 0,
                        'wins': 0,
                        'losses': 0
                    }

                ranking[name]['matches'] += 1

                if result == 'winner':
                    ranking[name]['wins'] += 1
                else:
                    ranking[name]['losses'] += 1

        context['ranking'] = [ranking[player] for player in ranking]
        return context