class ViolationAgent:

    def generate(
        self,
        triple_riding
    ):

        violations = []

        if triple_riding:

            violations.append(
                "Triple Riding"
            )

        return violations