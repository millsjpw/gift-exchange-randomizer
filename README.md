# Gift Exchange Randomizer

A Python script that randomly assigns gift recipients for holiday exchanges while respecting important constraints:

- **Spouses cannot be assigned to each other**
- **People cannot get the same person they had last time**
- **People cannot be assigned to themselves**

## Features

- 🎯 **Smart Constraint Handling**: Automatically prevents spouse-to-spouse assignments and repeat assignments
- 📁 **Persistent Data**: Stores assignments in JSON format for next year's exclusions
- 🔄 **Automatic Updates**: Each run updates the data file with new "previous recipient" information
- ✅ **Validation**: Built-in validation ensures all constraints are respected
- 🧪 **Tested**: Comprehensive test suite ensures reliability

## Usage

### Basic Usage

```bash
python gift_exchange.py participants.json
```

### Example Output

```
Loaded 6 participants:
  Alice (cannot give to: Charlie, Bob)
  Bob (cannot give to: Diana, Alice)
  Charlie (cannot give to: Diana, Alice)
  Diana (cannot give to: Charlie, Bob)
  Eve (cannot give to: Frank)
  Frank (cannot give to: Eve)

🎁 Gift Exchange Assignments:
========================================
Alice → Eve
Bob → Charlie
Charlie → Frank
Diana → Alice
Eve → Diana
Frank → Bob

Assignments saved to participants.json for next year's exclusions.
```

## Data Format

The script uses a JSON file to store participant data. Here's the format:

```json
{
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
    },
    {
      "name": "Charlie",
      "spouse": "Diana",
      "previous_recipient": null
    },
    {
      "name": "Diana",
      "spouse": "Charlie",
      "previous_recipient": null
    }
  ]
}
```

### Field Descriptions

- **`name`** (required): The person's name
- **`spouse`** (optional): Name of their spouse (use `null` if single)
- **`previous_recipient`** (optional): Who they gave a gift to last year (use `null` for first year)

## Getting Started

1. **Create your participants file**: Copy `example_participants.json` and modify it with your family/group members:

```bash
cp example_participants.json my_family.json
# Edit my_family.json with your participants
```

2. **Run the randomizer**:

```bash
python gift_exchange.py my_family.json
```

3. **Next year**: Simply run the same command again! The script automatically uses this year's assignments as next year's exclusions.

## Error Handling

The script handles various error cases:

- **Invalid JSON**: Clear error messages for malformed JSON files
- **Missing files**: Helpful error if the participants file doesn't exist
- **Impossible assignments**: If constraints make assignment impossible, the script will report this
- **Invalid data**: Validation of participant data and assignment results

## Testing

Run the test suite to verify everything works correctly:

```bash
python test_gift_exchange.py
```

## Examples

### First Year Setup

For your first year, create a JSON file with participants and their spouses (if any):

```json
{
  "participants": [
    {"name": "Alice", "spouse": "Bob", "previous_recipient": null},
    {"name": "Bob", "spouse": "Alice", "previous_recipient": null},
    {"name": "Charlie", "spouse": null, "previous_recipient": null},
    {"name": "Diana", "spouse": null, "previous_recipient": null}
  ]
}
```

### Subsequent Years

After the first run, the file automatically updates:

```json
{
  "participants": [
    {"name": "Alice", "spouse": "Bob", "previous_recipient": "Diana"},
    {"name": "Bob", "spouse": "Alice", "previous_recipient": "Charlie"},
    {"name": "Charlie", "spouse": null, "previous_recipient": "Alice"},
    {"name": "Diana", "spouse": null, "previous_recipient": "Bob"}
  ]
}
```

## Algorithm

The randomizer uses a constraint-satisfaction approach:

1. **Load Constraints**: Read participant data and build exclusion sets
2. **Random Assignment**: Shuffle participants and assign valid recipients
3. **Validation**: Verify all constraints are satisfied
4. **Retry Logic**: If assignment fails, retry up to 1000 times
5. **Update Data**: Save current assignments as next year's exclusions

## Requirements

- Python 3.6 or higher
- No external dependencies (uses only standard library)

## Contributing

Feel free to submit issues or pull requests to improve the randomizer!