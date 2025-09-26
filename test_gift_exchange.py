#!/usr/bin/env python3
"""
Simple tests for the gift exchange randomizer.
"""

import json
import os
import tempfile
from gift_exchange import Participant, GiftExchangeRandomizer, load_participants_from_file, save_assignments_to_file


def test_participant_exclusions():
    """Test that participant exclusions work correctly."""
    print("Testing participant exclusions...")
    
    # Test participant with spouse and previous recipient
    p = Participant("Alice", spouse="Bob", previous_recipient="Charlie")
    
    assert not p.can_be_assigned("Alice")  # Cannot assign to self
    assert not p.can_be_assigned("Bob")   # Cannot assign to spouse
    assert not p.can_be_assigned("Charlie")  # Cannot assign to previous recipient
    assert p.can_be_assigned("Diana")     # Can assign to others
    
    print("✓ Participant exclusions working correctly")


def test_simple_randomization():
    """Test randomization with a simple case."""
    print("Testing simple randomization...")
    
    participants = [
        Participant("Alice"),
        Participant("Bob"),
        Participant("Charlie")
    ]
    
    randomizer = GiftExchangeRandomizer(participants)
    assignments = randomizer.randomize_assignments()
    
    # Validate basic constraints
    assert len(assignments) == 3
    assert set(assignments.keys()) == {"Alice", "Bob", "Charlie"}
    assert set(assignments.values()) == {"Alice", "Bob", "Charlie"}
    
    # No one should be assigned to themselves
    for giver, recipient in assignments.items():
        assert giver != recipient
    
    print("✓ Simple randomization working correctly")


def test_spouse_constraints():
    """Test that spouse constraints are respected."""
    print("Testing spouse constraints...")
    
    participants = [
        Participant("Alice", spouse="Bob"),
        Participant("Bob", spouse="Alice"),
        Participant("Charlie"),
        Participant("Diana")
    ]
    
    randomizer = GiftExchangeRandomizer(participants)
    
    # Run multiple times to ensure constraint is always respected
    for _ in range(10):
        assignments = randomizer.randomize_assignments()
        
        # Alice should never be assigned to Bob and vice versa
        assert assignments["Alice"] != "Bob"
        assert assignments["Bob"] != "Alice"
    
    print("✓ Spouse constraints working correctly")


def test_previous_recipient_constraints():
    """Test that previous recipient constraints are respected."""
    print("Testing previous recipient constraints...")
    
    participants = [
        Participant("Alice", previous_recipient="Bob"),
        Participant("Bob", previous_recipient="Charlie"),
        Participant("Charlie", previous_recipient="Alice")
    ]
    
    randomizer = GiftExchangeRandomizer(participants)
    
    # Run multiple times to ensure constraint is always respected
    for _ in range(10):
        assignments = randomizer.randomize_assignments()
        
        # No one should get their previous recipient
        assert assignments["Alice"] != "Bob"
        assert assignments["Bob"] != "Charlie"
        assert assignments["Charlie"] != "Alice"
    
    print("✓ Previous recipient constraints working correctly")


def test_file_operations():
    """Test loading from and saving to JSON files."""
    print("Testing file operations...")
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        test_data = {
            "participants": [
                {"name": "Alice", "spouse": "Bob", "previous_recipient": "Charlie"},
                {"name": "Bob", "spouse": "Alice", "previous_recipient": "Diana"},
                {"name": "Charlie", "spouse": None, "previous_recipient": "Alice"},
                {"name": "Diana", "spouse": None, "previous_recipient": "Bob"}
            ]
        }
        json.dump(test_data, f)
        temp_filename = f.name
    
    try:
        # Test loading
        participants = load_participants_from_file(temp_filename)
        assert len(participants) == 4
        
        alice = next(p for p in participants if p.name == "Alice")
        assert alice.spouse == "Bob"
        assert alice.previous_recipient == "Charlie"
        assert not alice.can_be_assigned("Bob")
        assert not alice.can_be_assigned("Charlie")
        
        # Test randomization and saving
        randomizer = GiftExchangeRandomizer(participants)
        assignments = randomizer.randomize_assignments()
        
        save_assignments_to_file(assignments, temp_filename)
        
        # Load again and verify previous recipients were updated
        updated_participants = load_participants_from_file(temp_filename)
        for participant in updated_participants:
            expected_recipient = assignments[participant.name]
            assert participant.previous_recipient == expected_recipient
        
        print("✓ File operations working correctly")
        
    finally:
        # Clean up
        os.unlink(temp_filename)


def test_impossible_assignment():
    """Test handling of impossible assignments."""
    print("Testing impossible assignment handling...")
    
    # Create scenario where no valid assignment is possible
    participants = [
        Participant("Alice", previous_recipient="Bob"),
        Participant("Bob", previous_recipient="Alice")
    ]
    
    randomizer = GiftExchangeRandomizer(participants)
    
    try:
        assignments = randomizer.randomize_assignments(max_attempts=10)
        # If we get here, something went wrong
        assert False, "Should have raised ValueError for impossible assignment"
    except ValueError as e:
        assert "Could not find valid assignment" in str(e)
        print("✓ Impossible assignment handling working correctly")


def run_all_tests():
    """Run all tests."""
    print("Running gift exchange randomizer tests...\n")
    
    test_participant_exclusions()
    test_simple_randomization()
    test_spouse_constraints()
    test_previous_recipient_constraints()
    test_file_operations()
    test_impossible_assignment()
    
    print("\n🎉 All tests passed!")


if __name__ == "__main__":
    run_all_tests()