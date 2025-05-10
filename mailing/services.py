from django.core.cache import cache

from config.settings import CACHE_ENABLED
from mailing.models import Dispatch, Message, Recipient


def get_recipients_from_cache():
    """Получает список всех получателей из кеша"""
    if not CACHE_ENABLED:
        return Recipient.objects.all()
    key = "recipients_list"
    recipients = cache.get(key)
    if recipients is not None:
        return recipients
    recipients = Recipient.objects.all()
    cache.set(key, recipients)
    return recipients


def get_recipients_for_user_from_cache(user):
    """Получает список опубликованных продуктов из кеша"""
    if not CACHE_ENABLED:
        return Recipient.objects.filter(owner=user)
    key = "recipients_list_for_user"
    recipients = cache.get(key)
    if recipients is not None:
        return recipients
    recipients = Recipient.objects.filter(owner=user)
    cache.set(key, recipients)
    return recipients


def get_messages_from_cache():
    """Получает список всех сообщений из кеша"""
    if not CACHE_ENABLED:
        return Message.objects.all()
    key = "messages_list"
    messages = cache.get(key)
    if messages is not None:
        return messages
    messages = Message.objects.all()
    cache.set(key, messages)
    return messages


def get_messages_for_user_from_cache(user):
    """Получает список опубликованных продуктов из кеша"""
    if not CACHE_ENABLED:
        return Message.objects.filter(owner=user)
    key = "messages_list_for_user"
    messages = cache.get(key)
    if messages is not None:
        return messages
    messages = Message.objects.filter(owner=user)
    cache.set(key, messages)
    return messages


def get_dispatches_from_cache():
    """Получает список всех сообщений из кеша"""
    if not CACHE_ENABLED:
        return Dispatch.objects.all()
    key = "dispatches_list"
    dispatches = cache.get(key)
    if dispatches is not None:
        return dispatches
    dispatches = Dispatch.objects.all()
    cache.set(key, dispatches)
    return dispatches


def get_dispatches_for_user_from_cache(user):
    """Получает список опубликованных продуктов из кеша"""
    if not CACHE_ENABLED:
        return Dispatch.objects.filter(owner=user)
    key = "dispatches_list_for_user"
    dispatches = cache.get(key)
    if dispatches is not None:
        return dispatches
    dispatches = Dispatch.objects.filter(owner=user)
    cache.set(key, dispatches)
    return dispatches
