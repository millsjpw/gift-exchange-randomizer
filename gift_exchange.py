#!/usr/bin/env python3
"""
Gift Exchange Randomizer

A script to randomly assign gift recipients while respecting constraints:
- Spouses cannot be assigned to each other
- People cannot get the same person they had last time
"""

import json
import random
import sys
from typing import Dict, List, Set, Optional


class Participant:
    """Represents a participant in the gift exchange."""
    
    def __init__(self, name: str, spouse: Optional[str] = None, previous_recipient: Optional[str] = None):
        self.name = name
        self.spouse = spouse
        self.previous_recipient = previous_recipient
        self.excluded_recipients: Set[str] = set()
        
        # Add spouse and previous recipient to exclusions
        if spouse:
            self.excluded_recipients.add(spouse)
        if previous_recipient:
            self.excluded_recipients.add(previous_recipient)
        
        # Cannot be assigned to themselves
        self.excluded_recipients.add(name)
    
    def can_be_assigned(self, recipient: str) -> bool:
        """Check if this participant can be assigned to give a gift to the recipient."""
        return recipient not in self.excluded_recipients
    
    def __repr__(self):
        return f"Participant(name='{self.name}', spouse='{self.spouse}', previous='{self.previous_recipient}')"


class GiftExchangeRandomizer:
    """Handles the randomization logic for gift exchange assignments."""
    
    def __init__(self, participants: List[Participant]):
        self.participants = participants
        self.participant_names = [p.name for p in participants]
        self.assignments: Dict[str, str] = {}
    
    def randomize_assignments(self, max_attempts: int = 1000) -> Dict[str, str]:
        """
        Randomly assign gift recipients to participants.
        
        Returns a dictionary mapping giver name to recipient name.
        Raises ValueError if no valid assignment can be found.
        """
        for attempt in range(max_attempts):
            if self._try_assignment():
                return self.assignments.copy()
        
        raise ValueError(f"Could not find valid assignment after {max_attempts} attempts. "
                        "The constraints may be too restrictive.")
    
    def _try_assignment(self) -> bool:
        """Try to create a valid assignment. Returns True if successful."""
        self.assignments = {}
        available_recipients = set(self.participant_names)
        participants_to_assign = self.participants.copy()
        random.shuffle(participants_to_assign)
        
        for participant in participants_to_assign:
            # Find valid recipients for this participant
            valid_recipients = [
                name for name in available_recipients 
                if participant.can_be_assigned(name)
            ]
            
            if not valid_recipients:
                return False  # No valid assignment possible
            
            # Randomly select from valid recipients
            chosen_recipient = random.choice(valid_recipients)
            self.assignments[participant.name] = chosen_recipient
            available_recipients.remove(chosen_recipient)
        
        return True
    
    def validate_assignments(self, assignments: Dict[str, str]) -> List[str]:
        """Validate assignments and return list of any constraint violations."""
        violations = []
        participant_dict = {p.name: p for p in self.participants}
        
        for giver, recipient in assignments.items():
            if giver not in participant_dict:
                violations.append(f"Unknown giver: {giver}")
                continue
            
            participant = participant_dict[giver]
            if not participant.can_be_assigned(recipient):
                violations.append(f"{giver} cannot be assigned to {recipient}")
        
        # Check that all participants are assigned exactly once as givers and recipients
        givers = set(assignments.keys())
        recipients = set(assignments.values())
        all_names = set(self.participant_names)
        
        if givers != all_names:
            violations.append(f"Missing givers: {all_names - givers}")
        if recipients != all_names:
            violations.append(f"Missing recipients: {all_names - recipients}")
        
        return violations


def load_participants_from_file(filename: str) -> List[Participant]:
    """Load participants from a JSON file."""
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
        
        participants = []
        for person_data in data.get('participants', []):
            name = person_data['name']
            spouse = person_data.get('spouse')
            previous_recipient = person_data.get('previous_recipient')
            participants.append(Participant(name, spouse, previous_recipient))
        
        return participants
    
    except FileNotFoundError:
        raise FileNotFoundError(f"Could not find file: {filename}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in file {filename}: {e}")
    except KeyError as e:
        raise ValueError(f"Missing required field in JSON: {e}")


def save_assignments_to_file(assignments: Dict[str, str], filename: str):
    """Save assignments to a JSON file for use as next year's previous recipients."""
    # Load existing data to preserve it
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {'participants': []}
    
    # Update previous recipients based on current assignments
    participant_dict = {p['name']: p for p in data['participants']}
    
    for giver, recipient in assignments.items():
        if giver in participant_dict:
            participant_dict[giver]['previous_recipient'] = recipient
        else:
            # Add new participant if they don't exist
            participant_dict[giver] = {
                'name': giver,
                'spouse': None,
                'previous_recipient': recipient
            }
    
    # Convert back to list format
    data['participants'] = list(participant_dict.values())
    
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)


def main():
    """Main function to run the gift exchange randomizer."""
    if len(sys.argv) != 2:
        print("Usage: python gift_exchange.py <participants_file.json>")
        print("\nThe JSON file should contain participant data in this format:")
        print('''{
  "participants": [
    {
      "name": "Alice",
      "spouse": "Bob",
      "previous_recipient": "Charlie"
    },
    {
      "name": "Bob", 
      "spouse": "Alice",
      "previous_recipient": "Diana"
    }
  ]
}''')
        sys.exit(1)
    
    filename = sys.argv[1]
    
    try:
        # Load participants
        participants = load_participants_from_file(filename)
        
        if len(participants) < 2:
            print("Error: Need at least 2 participants for gift exchange.")
            sys.exit(1)
        
        print(f"Loaded {len(participants)} participants:")
        for p in participants:
            exclusions = list(p.excluded_recipients - {p.name})
            print(f"  {p.name} (cannot give to: {', '.join(exclusions) if exclusions else 'none'})")
        
        # Create randomizer and generate assignments
        randomizer = GiftExchangeRandomizer(participants)
        assignments = randomizer.randomize_assignments()
        
        # Validate assignments
        violations = randomizer.validate_assignments(assignments)
        if violations:
            print("Error: Assignment validation failed!")
            for violation in violations:
                print(f"  - {violation}")
            sys.exit(1)
        
        # Display results
        print("\n🎁 Gift Exchange Assignments:")
        print("=" * 40)
        for giver, recipient in sorted(assignments.items()):
            print(f"{giver} → {recipient}")
        
        # Save assignments back to file for next year
        save_assignments_to_file(assignments, filename)
        print(f"\nAssignments saved to {filename} for next year's exclusions.")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()