
from django.conf.urls import include, url
from .views import locationHelperBotView
urlpatterns = [
                  url(r'^216b079c8cfca24abec8e41d7b21ac79463af9928498326478/?$', locationHelperBotView.as_view()) 
               ]