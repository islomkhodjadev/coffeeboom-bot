# Generated by Django 5.0.6 on 2024-06-30 16:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('botAdmin', '0002_menucategory_menuitem'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='chatmessage',
            options={'verbose_name': 'Chat Message', 'verbose_name_plural': 'Chat Messages'},
        ),
        migrations.AlterModelOptions(
            name='chats',
            options={'verbose_name': 'Chat', 'verbose_name_plural': 'Chats'},
        ),
        migrations.AlterModelOptions(
            name='eventdata',
            options={'verbose_name': 'Event Data', 'verbose_name_plural': 'Event Data'},
        ),
        migrations.AlterModelOptions(
            name='image',
            options={'verbose_name': 'Image', 'verbose_name_plural': 'Images'},
        ),
        migrations.AlterModelOptions(
            name='menucategory',
            options={'verbose_name': 'Menu Category', 'verbose_name_plural': 'Menu Categories'},
        ),
        migrations.AlterModelOptions(
            name='menuitem',
            options={'verbose_name': 'Menu Item', 'verbose_name_plural': 'Menu Items'},
        ),
        migrations.AlterModelOptions(
            name='postchannel',
            options={'verbose_name': 'Post Channel', 'verbose_name_plural': 'Post Channels'},
        ),
        migrations.AlterModelOptions(
            name='telegramuser',
            options={'verbose_name': 'Telegram User', 'verbose_name_plural': 'Telegram Users'},
        ),
        migrations.AddField(
            model_name='menuitem',
            name='promotion',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='chatmessage',
            name='is_admin',
            field=models.BooleanField(default=False, verbose_name='Is Admin'),
        ),
        migrations.AlterField(
            model_name='chatmessage',
            name='telegram_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='botAdmin.telegramuser', verbose_name='Telegram User'),
        ),
        migrations.AlterField(
            model_name='chatmessage',
            name='text',
            field=models.TextField(verbose_name='Text'),
        ),
        migrations.AlterField(
            model_name='chatmessage',
            name='timestamp',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Timestamp'),
        ),
        migrations.AlterField(
            model_name='chats',
            name='name',
            field=models.CharField(max_length=200, verbose_name='Chat Name'),
        ),
        migrations.AlterField(
            model_name='eventdata',
            name='content',
            field=models.TextField(verbose_name='Content'),
        ),
        migrations.AlterField(
            model_name='eventdata',
            name='expire_date',
            field=models.DateTimeField(verbose_name='Expire Date'),
        ),
        migrations.AlterField(
            model_name='image',
            name='image',
            field=models.ImageField(upload_to='posts/', verbose_name='Image'),
        ),
        migrations.AlterField(
            model_name='image',
            name='post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='image', to='botAdmin.postchannel', verbose_name='Post'),
        ),
        migrations.AlterField(
            model_name='menucategory',
            name='image',
            field=models.ImageField(upload_to='menu/category/', verbose_name='Image'),
        ),
        migrations.AlterField(
            model_name='menucategory',
            name='name',
            field=models.CharField(max_length=200, verbose_name='Category Name'),
        ),
        migrations.AlterField(
            model_name='menuitem',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='item', to='botAdmin.menucategory', verbose_name='Category'),
        ),
        migrations.AlterField(
            model_name='menuitem',
            name='description',
            field=models.TextField(verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='menuitem',
            name='image',
            field=models.ImageField(upload_to='menu/menu-items/', verbose_name='Image'),
        ),
        migrations.AlterField(
            model_name='menuitem',
            name='name',
            field=models.CharField(max_length=200, verbose_name='Item Name'),
        ),
        migrations.AlterField(
            model_name='menuitem',
            name='price',
            field=models.IntegerField(verbose_name='Price'),
        ),
        migrations.AlterField(
            model_name='postchannel',
            name='ai_caption',
            field=models.BooleanField(default=False, verbose_name='AI Generated Caption'),
        ),
        migrations.AlterField(
            model_name='postchannel',
            name='caption',
            field=models.TextField(verbose_name='Caption'),
        ),
        migrations.AlterField(
            model_name='postchannel',
            name='chat',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='botAdmin.chats', verbose_name='Chat'),
        ),
        migrations.AlterField(
            model_name='postchannel',
            name='task_time',
            field=models.DateTimeField(verbose_name='Task Time'),
        ),
        migrations.AlterField(
            model_name='telegramuser',
            name='bio',
            field=models.TextField(blank=True, null=True, verbose_name='Bio'),
        ),
        migrations.AlterField(
            model_name='telegramuser',
            name='id_user',
            field=models.TextField(verbose_name='User ID'),
        ),
        migrations.AlterField(
            model_name='telegramuser',
            name='name',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='telegramuser',
            name='phone_number',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Phone Number'),
        ),
        migrations.AlterField(
            model_name='telegramuser',
            name='profile_picture',
            field=models.ImageField(blank=True, null=True, upload_to='profile_pictures/', verbose_name='Profile Picture'),
        ),
        migrations.AlterField(
            model_name='telegramuser',
            name='surname',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Surname'),
        ),
        migrations.AlterField(
            model_name='telegramuser',
            name='username',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Username'),
        ),
    ]
