# csvdiff

Fast column-aware diff tool for large CSV files with configurable key columns.

---

## Installation

```bash
pip install csvdiff
```

Or install from source:

```bash
git clone https://github.com/yourusername/csvdiff.git
cd csvdiff && pip install -e .
```

---

## Usage

Compare two CSV files using one or more columns as the key:

```bash
csvdiff old.csv new.csv --key id
```

Use multiple key columns:

```bash
csvdiff old.csv new.csv --key department --key employee_id
```

Output shows added, removed, and modified rows clearly labeled:

```
+ [id=42]  name: "Alice" | role: "Engineer"
- [id=17]  name: "Bob"   | role: "Manager"
~ [id=9]   salary: "70000" -> "75000"
```

### Python API

```python
from csvdiff import diff

changes = diff("old.csv", "new.csv", key_cols=["id"])
for change in changes:
    print(change)
```

---

## Options

| Flag | Description |
|------|-------------|
| `--key` | Column(s) to use as the unique row identifier (repeatable) |
| `--output` | Write diff results to a file instead of stdout |
| `--ignore` | Columns to exclude from comparison |
| `--format` | Output format: `text` (default), `json`, or `csv` |

---

## License

MIT © 2024 — see [LICENSE](LICENSE) for details.