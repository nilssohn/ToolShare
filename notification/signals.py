from django.dispatch import Signal
"""
signals sends all of the signals for where the tools themselves are going.
Helps direct where the signals will go
@authors: Tina Howard, Nick Mattis, Grant Gadomski
"""
borrow_request = Signal(providing_args = ["owner", "requester", "tool_id", "start_date", "end_date", "message"])
request_result = Signal(providing_args = ["result", "owner", "requester"])
tool_borrowed = Signal(providing_args = ["owner", "borrower", "tool_id"])
tool_ready_for_borrow = Signal(providing_args = ["owner", "borrower", "tool"])
tool_returned_check = Signal(providing_args = ["owner", "borrower", "tool_id", "reservation_id"])
tool_returned = Signal(providing_args = ["owner", "borrower", "tool"])
rating_result = Signal(providing_args = ["owner", "borrower", "comments", "thumb"])
created_new_shed = Signal(providing_args = ["shed_name", "creator"])
added_to_shed = Signal(providing_args = ["shed_name", "creator", "person_added"])
message_to_user = Signal(providing_args = ["message", "to_user", "from_user"])
tool_deregistered = Signal(providing_args = ["tool", "owner", "requester"])
removed_shed = Signal(providing_args=["shed_name", "user_to_remove"])
cancel_reservation = Signal(providing_args=["shed_name", "user_to_cancel", "tool", "user_who_cancelled"])