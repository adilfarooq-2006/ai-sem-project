class DisasterLogicEngine:
    def __init__(self):
        # Facts/Constants
        self.DRONE_MAX_WEIGHT = 2500
        self.DRONE_MAX_RANGE = 100
        self.TRUCK_MAX_RANGE = 600

    def verify_mission(self, vehicle_type, weight, road_status, distance):
        """
        Acts as a Prolog Inference Engine.
        Checks facts against rules and returns (Success, Reason).
        """
        reasons = []

        # Rule 1: Road Accessibility
        if road_status == "Blocked" and vehicle_type == "truck":
            return False, "RULE_VIOLATION: Ground vehicle cannot enter 'Blocked' zone."

        # Rule 2: Heavy Lift Protocol
        if weight > self.DRONE_MAX_WEIGHT and vehicle_type == "drone":
            return False, f"RULE_VIOLATION: Weight {weight}kg exceeds Drone limit of {self.DRONE_MAX_WEIGHT}kg."

        # Rule 3: Range Safety
        if vehicle_type == "drone" and (distance * 2) > self.DRONE_MAX_RANGE:
            return False, f"RULE_VIOLATION: Mission distance exceeds Drone battery range."

        # Success Rule
        return True, f"LOGIC_CONFIRMED: {vehicle_type.upper()} satisfies weight, road, and range constraints."

    def get_xai_log(self, mission_data):
        """Generates the 'Reasoning Log' for the Viva."""
        success, explanation = self.verify_mission(
            mission_data['vehicle'],
            mission_data['weight'],
            mission_data['status'],
            mission_data['dist']
        )
        return f"[PROLOG REASONING]: {explanation}"