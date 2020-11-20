from datetime import datetime

from sessions import get_sessions
from utils import get_datetime_obj


class ContactFormGame:

    def __init__(self):
        self.set_count(0)
        self.display_intro()

    @staticmethod
    def get_session_count(session):
        return session["outcomes"].get("Contact Form", 0)

    def display_exit(self):
        best = self.get_best_session()
        current = self.get_count()

        print(f"\n{current} form{self.get_plural(current)} submitted!")

        if current > best:
            print(f"You beat the previous record of {best}")
            print("Great job!")
        print("")

    def display_intro(self):
        best = self.get_best_session()

        if best == 0:
            print("\nYou haven't submitted any forms yet today.")
            print("Let's see what you got!")
        else:
            print("\nCurrent record for today is")
            print(f"{best} form submission{self.get_plural(best)}!")
            print("Can you beat it?")
        print("")

    def display_status(self):
        best = self.get_best_session()
        current = self.get_count()

        print(f"\n{current} form{self.get_plural(current)} submitted!")

        if current < best:
            beat = (best - current) + 1
            print(f"Only {beat} form{self.get_plural(beat)} needed")
            print("to beat today's record.")
        elif current > best:
            print("You have set a new record, keep it going!")
        else:
            print("You matched today's record, one more to go!")
        print("")

    def get_best_session(self):
        if not hasattr(self, "_best"):
            self._best = 0
            today = datetime.now().date()

            for session in get_sessions():
                start = get_datetime_obj(session["start"])
                if start.date() == today:
                    forms_submitted = self.get_session_count(session)
                    if forms_submitted > self._best:
                        self._best = forms_submitted
        return self._best

    def get_count(self):
        return self._count

    def get_plural(self, count):
        if count > 1 or count < 1:
            return "s"
        return ""

    def set_count(self, count):
        self._count = count

    def update(self, session):
        session_count = self.get_session_count(session)
        if not self.get_count() == session_count:
            self.set_count(session_count)
            self.display_status()
