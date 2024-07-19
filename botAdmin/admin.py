# admin.py
from django.contrib import admin
from django.urls import path
from django.shortcuts import render, get_object_or_404
from .models import TelegramUser, ChatMessage, EventData, Chats, MenuCategory, MenuItem, Promotion

class TelegramUserAdmin(admin.ModelAdmin):
    change_list_template = 'admin/telegram_user_change_list.html'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:user_id>/chat/', self.admin_site.admin_view(self.user_chat_view), name='user_chat'),
        ]
        return custom_urls + urls

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        users = TelegramUser.objects.all()
        extra_context['users'] = users
        return super().changelist_view(request, extra_context=extra_context)

    def user_chat_view(self, request, user_id):
        telegramuser = get_object_or_404(TelegramUser, pk=user_id)
        messages = ChatMessage.objects.filter(telegram_user=telegramuser).order_by('timestamp')
        context = dict(
            self.admin_site.each_context(request),
            telegramuser=telegramuser,
            messages=messages,
        )
        
        return render(request, 'admin/user_chat.html', context)


from .models import POSTCHANNEL, Image

class ImageInline(admin.TabularInline):  # or admin.StackedInline for a different layout
    model = Image
    extra = 1  # Number of empty forms the admin provides for new images

class POSTCHANNELAdmin(admin.ModelAdmin):
    inlines = [ImageInline]
    list_display = ('caption', 'task_time', "chat")  # Fields to display in the admin list view


admin.site.register(POSTCHANNEL, POSTCHANNELAdmin)

class Events(admin.ModelAdmin):
    
    list_display = ('content', 'expire_date')  # Fields to display in the admin list view


admin.site.register(TelegramUser, TelegramUserAdmin)
admin.site.register(ChatMessage)
admin.site.register(EventData, Events)
admin.site.register(Chats)
admin.site.register(MenuCategory)
admin.site.register(MenuItem)
# admin.site.register(Promotion)