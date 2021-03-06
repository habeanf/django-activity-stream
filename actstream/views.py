from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from actstream import user_stream, actor_stream, model_stream
from actstream.models import Follow, Action

@login_required
def follow_unfollow(request, content_type_id, object_id, follow=True):
    """
    Creates follow relationship st ``request.user`` starts following the actor defined by ``content_type_id``, ``object_id``
    """
    ctype = get_object_or_404(ContentType, pk=content_type_id)
    actor = get_object_or_404(ctype.model_class(), pk=object_id)
    lookup = {
        'user': request.user,
        'content_type': ctype,
        'object_id': object_id,
    }
    def resp(code=201):
        if 'next' in request.REQUEST:
            return HttpResponseRedirect(request.REQUEST['next'])
        return type('Response%d' % code, (HttpResponse,), {'status_code': code})()
        
    if follow:
        Follow.objects.get_or_create(**lookup)
        return resp()
    Follow.objects.get(**lookup).delete()
    return resp(204)
    
@login_required
def stream(request):
    """
    Index page for authenticated user's activity stream. (Eg: Your feed at github.com)
    """
    return render_to_response('activity/actor.html', {
        'ctype': ContentType.objects.get_for_model(request.user),
        'actor':request.user,'action_list':user_stream(request.user)
    }, context_instance=RequestContext(request))
    
def followers(request, content_type_id, object_id):
    """
    Creates a listing of ``User``s that follow the actor defined by ``content_type_id``, ``object_id``
    """
    ctype = get_object_or_404(ContentType, pk=content_type_id)
    follows = Follow.objects.filter(content_type=ctype, object_id=object_id)
    actor = get_object_or_404(ctype.model_class(), pk=object_id)
    return render_to_response('activity/followers.html', {
        'followers': [f.user for f in follows], 'actor':actor
    }, context_instance=RequestContext(request))
    
def user(request, username):
    """
    ``User`` focused activity stream. (Eg: Profile page twitter.com/justquick)
    """
    user = get_object_or_404(User, username=username)
    return render_to_response('activity/actor.html', {
        'ctype': ContentType.objects.get_for_model(User),
        'actor':user,'action_list':actor_stream(user)
    }, context_instance=RequestContext(request))
    
def detail(request, action_id):
    """
    ``Action`` detail view (pretty boring, mainly used for get_absolute_url)
    """
    return render_to_response('activity/detail.html', {
        'action': get_object_or_404(Action, pk=action_id)
    }, context_instance=RequestContext(request))
    
def actor(request, content_type_id, object_id):
    """
    ``Actor`` focused activity stream for actor defined by ``content_type_id``, ``object_id``
    """
    ctype = get_object_or_404(ContentType, pk=content_type_id)
    actor = get_object_or_404(ctype.model_class(), pk=object_id)    
    return render_to_response('activity/actor.html', {
        'action_list': actor_stream(actor), 'actor':actor,'ctype':ctype
    }, context_instance=RequestContext(request))
    
def model(request, content_type_id):
    """
    ``Actor`` focused activity stream for actor defined by ``content_type_id``, ``object_id``
    """
    ctype = get_object_or_404(ContentType, pk=content_type_id)
    actor = ctype.model_class()
    return render_to_response('activity/actor.html', {
        'action_list': model_stream(actor),'ctype':ctype,'actor':ctype#._meta.verbose_name_plural.title()
    }, context_instance=RequestContext(request)) 
