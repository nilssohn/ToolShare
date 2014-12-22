from django.dispatch import Signal

user_message = Signal(providing_args = ["receiving_user", "sending_user", "message"])
shed_message = Signal(providing_args = ["receiving_user", "sending_user", "sending_shed", "message"])