from django.dispatch import Signal

user_followed = Signal()
user_commented = Signal()
post_liked = Signal()