from django.core.cache import cache

from config.settings import CACHE_ENABLED
from mailing.models import Dispatch, MailingAttempt, Message, Recipient


def get_recipients_from_cache():
    """
    Получает список всех получателей из кеша.
    Если кеш отключен, возвращает всех получателей из базы данных.
    Returns:
        QuerySet: Список всех получателей.
    """
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
    """
    Получает список всех получателей из кеша для указанного владельца.
    Если кеш отключен, возвращает получателей, принадлежащих указанному пользователю.
    Args:
        user (User): Пользователь, для которого запрашиваются получатели.
    Returns:
        QuerySet: Список получателей, принадлежащих указанному пользователю.
    """
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
    """
    Получает список всех сообщений из кеша.
    Если кеш отключен, возвращает все сообщения из базы данных.
    Returns:
        QuerySet: Список всех сообщений.
    """
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
    """
    Получает список всех сообщений из кеша для указанного владельца.
    Если кеш отключен, возвращает сообщения, принадлежащих указанному пользователю.
    Args:
        user (User): Пользователь, для которого запрашиваются сообщения.
    Returns:
        QuerySet: Список сообщений, принадлежащих указанному пользователю.
    """
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
    """
    Получает список всех рассылок из кеша.
    Если кеш отключен, возвращает все рассылки из базы данных.
    Returns:
        QuerySet: Список всех рассылок.
    """
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
    """
    Получает список всех рассылок из кеша для указанного владельца.
    Если кеш отключен, возвращает рассылки, принадлежащих указанному пользователю.
    Args:
        user (User): Пользователь, для которого запрашиваются рассылки.
    Returns:
        QuerySet: Список рассылок, принадлежащих указанному пользователю.
    """
    if not CACHE_ENABLED:
        return Dispatch.objects.filter(owner=user)
    key = "dispatches_list_for_user"
    dispatches = cache.get(key)
    if dispatches is not None:
        return dispatches
    dispatches = Dispatch.objects.filter(owner=user)
    cache.set(key, dispatches)
    return dispatches


def get_mailing_attempts_from_cache():
    """
    Получает список всех попыток рассылок из кеша.
    Если кеш отключен, возвращает все попытки рассылок из базы данных.
    Returns:
        QuerySet: Список всех попыток рассылок.
    """
    if not CACHE_ENABLED:
        return MailingAttempt.objects.all()
    key = "mailing_attempts_list"
    mailing_attempts = cache.get(key)
    if mailing_attempts is not None:
        return mailing_attempts
    mailing_attempts = MailingAttempt.objects.all()
    cache.set(key, mailing_attempts)
    return mailing_attempts


def get_mailing_attempts_for_user_from_cache(user):
    """
    Получает список всех попыток рассылок из кеша для указанного владельца.
    Если кеш отключен, возвращает попытки рассылок, принадлежащих указанному пользователю.
    Args:
        user (User): Пользователь, для которого запрашиваются попытки рассылок.
    Returns:
        QuerySet: Список попыток рассылок, принадлежащих указанному пользователю.
    """
    if not CACHE_ENABLED:
        return MailingAttempt.objects.filter(owner=user)
    key = "mailing_attempts_list_for_user"
    mailing_attempts = cache.get(key)
    if mailing_attempts is not None:
        return mailing_attempts
    mailing_attempts = MailingAttempt.objects.filter(owner=user)
    cache.set(key, mailing_attempts)
    return mailing_attempts
