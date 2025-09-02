# Seating Arrangement Solver

This script uses the Z3 theorem prover to find an optimal seating arrangement for a group of guests at a set of tables, based on a list of constraints and preferences.

## Usage

The script reads guest constraints from a CSV file via standard input and takes the size of each table as command-line arguments.

```bash
cat <constraints.csv> | python seating.py <table1_size> <table2_size> ...
```

### Input CSV Format

The input CSV file must be a square matrix where the first row is a header with guest names. The file should look like this:

```csv
GuestA,GuestB,GuestC
0,100,-1
100,0,5
-1,5,0
```

The values in the matrix define the relationships between guests:
- `100`: Hard constraint. These two guests *must* be seated at the same table.
- `-1`: Hard constraint. These two guests *must not* be seated at the same table.
- Positive values (e.g., `5`): A preference for these guests to be seated at the same table. The script will try to maximize the sum of these preference values for all co-seated guests.
- `0`: No preference.

### Generating the CSV from the Template

A `master.xlsx` spreadsheet template can be used to simplify creating the input CSV file.

1.  In the `master.xlsx` file, open the `Matrice` sheet.
2.  List all guest names in the first column. The header row will automatically populate with the same names.
3.  Fill in the grid with the relationship values. Any blank cells will be treated as `0` (no preference).
4.  Switch to the `Output` sheet, which contains the formatted matrix.
5.  Export the `Output` sheet to a CSV file.
6.  **Important**: During the export process, you must omit the first column (the one with guest names for each row). The final CSV file should only have guest names in the header row, as shown in the "Input CSV Format" section.

### Example

Given a `test.csv` file with constraints and a desired arrangement of two tables with 3 seats each and two tables with 2 seats each, you would run:

```bash
cat test.csv | python seating.py 3 3 2 2
```

The script will output one or more possible seating arrangements that satisfy the hard constraints, along with their "preference score". It will iteratively search for better solutions.
