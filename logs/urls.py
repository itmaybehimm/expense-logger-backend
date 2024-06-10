from django.urls import path
from . import views
urlpatterns = [
    path('logs/', view=views.LogGroupView.as_view()),
    path('logs/<int:log_id>/', view=views.LogView.as_view()),
    path('logs/<int:log_id>/items/', view=views.ItemGroupView.as_view()),
    path('logs/<int:log_id>/items/<int:item_id>/', view=views.ItemView.as_view())
]
