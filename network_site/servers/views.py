from django.shortcuts import get_object_or_404, render

from .models import Router, Server


def server_list(request):
    servers = Server.objects.all()
    return render(request, 'servers/server_list.html', {'servers': servers})


def server_detail(request, pk):
    server = get_object_or_404(Server, pk=pk)
    return render(request, 'servers/server_detail.html', {'server': server})

def router_detail(request, server_pk, router_pk):
    router = get_object_or_404(Router, server_id=server_pk, pk=router_pk)
    return render(request, 'servers/router_detail.html', {'router': router})
