# from django.test import TestCase
# from django.utils import timezone
# from mailing.models import Recipient, Message, Dispatch, MailingAttempt
# from users.models import User
#
#
# class RecipientModelTest(TestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(email='test@example.com', password='testpassword')
#         self.recipient = Recipient.objects.create(
#             email='recipient@example.com',
#             full_name='Test User',
#             owner=self.user
#         )
#
#     def test_recipient_str(self):
#         self.assertEqual(str(self.recipient), 'recipient@example.com')

# class MessageModelTest(TestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(username='testuser', password='testpassword')
#         self.message = Message.objects.create(
#             theme='Test Message',
#             content='This is a test message.',
#             owner=self.user
#         )
#
#     def test_message_str(self):
#         self.assertEqual(str(self.message), 'Test Message')
#
#
# class DispatchModelTest(TestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(username='testuser', password='testpassword')
#         self.recipient = Recipient.objects.create(
#             email='test@example.com',
#             full_name='Test User',
#             owner=self.user
#         )
#         self.message = Message.objects.create(
#             theme='Test Message',
#             content='This is a test message.',
#             owner=self.user
#         )
#         self.dispatch = Dispatch.objects.create(
#             message=self.message,
#             owner=self.user,
#             status='created'
#         )
#         self.dispatch.recipient.add(self.recipient)
#
#     def test_dispatch_str(self):
#         self.assertEqual(str(self.dispatch), 'Test Message - created')
#
#     def test_save_method_starts_dispatch(self):
#         self.dispatch.status = 'started'
#         self.dispatch.save()
#         self.assertIsNotNone(self.dispatch.first_sending_datetime)
#
#     def test_send_emails_success(self):
#         self.dispatch.status = 'started'
#         self.dispatch.save()
#         # В этом тесте вы можете использовать mock для проверки вызова send_mail
#         # Например, с использованием unittest.mock.patch
#
#
# class MailingAttemptModelTest(TestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(username='testuser', password='testpassword')
#         self.recipient = Recipient.objects.create(
#             email='test@example.com',
#             full_name='Test User',
#             owner=self.user
#         )
#         self.message = Message.objects.create(
#             theme='Test Message',
#             content='This is a test message.',
#             owner=self.user
#         )
#         self.dispatch = Dispatch.objects.create(
#             message=self.message,
#             owner=self.user,
#             status='completed'
#         )
#         self.attempt = MailingAttempt.objects.create(
#             mailing_attempt_datetime=timezone.now(),
#             status='success',
#             dispatch=self.dispatch,
#             owner=self.user
#         )
#
#     def test_mailing_attempt_str(self):
#         self.assertEqual(str(self.attempt), 'Попытка рассылки - success')
#
#     def test_mailing_attempt_status_choices(self):
#         self.assertIn(self.attempt.status, ['success', 'unsuccessfully'])
