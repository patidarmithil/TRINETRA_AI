class TripleRidingAgent:

    def detect(
        self,
        motorcycle_count,
        person_count
    ):

        if motorcycle_count > 0 and person_count >= 3:
            return True

        return False