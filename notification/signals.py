from django.dispatch import Signal

user_followed = Signal()
user_commented = Signal()
post_liked = Signal()
verification_request = Signal()
verification_response = Signal()
verificaton_success = Signal()
verfication_expired = Signal()
message_recived = Signal()