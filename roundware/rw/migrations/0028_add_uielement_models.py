# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-11-15 11:27
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rw', '0027_add_owner_desc_to_project'),
    ]

    operations = [
        migrations.CreateModel(
            name='UIElement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('variant', models.CharField(choices=[('@2x', '@2x'), ('@3x', '@3x'), ('-iPad@2x', 'iPad@2x'), ('-iPad@3x', 'iPad@3x'), ('-mdpi', 'mdpi'), ('-hdpi', 'hdpi'), ('-xhdpi', 'xhdpi'), ('-xxhdpi', 'xxhdpi'), ('-xxxhdpi', 'xxxhdpi')], max_length=15)),
                ('file_extension', models.CharField(choices=[('png', 'png'), ('jpg', 'jpg')], max_length=10, verbose_name='File Extension')),
                ('label_text_color', models.CharField(blank=True, max_length=10, verbose_name='Label Text Color (hex)')),
                ('label_position', models.CharField(blank=True, choices=[('text_below', 'text below image'), ('text_overlay', 'text overlaid on image')], max_length=20, verbose_name='Label Position')),
                ('label_text_loc', models.ManyToManyField(blank=True, related_name='label_text_string', to='rw.LocalizedString', verbose_name='Label Text')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rw.Project')),
            ],
            options={
                'verbose_name': 'UI Element',
                'verbose_name_plural': 'UI Elements',
            },
        ),
        migrations.CreateModel(
            name='UIElementName',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('description', models.TextField(blank=True, null=True)),
                ('view', models.CharField(choices=[('home', 'home'), ('listen', 'listen'), ('speak', 'speak'), ('listentags', 'listen tags'), ('speaktags', 'speak tags'), ('thankyou', 'thank you')], max_length=20)),
            ],
            options={
                'verbose_name': 'UI Element Name',
                'verbose_name_plural': 'UI Element Names',
            },
        ),
        migrations.AddField(
            model_name='uielement',
            name='uielementname',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rw.UIElementName', verbose_name='UI Element Name'),
        ),
    ]
