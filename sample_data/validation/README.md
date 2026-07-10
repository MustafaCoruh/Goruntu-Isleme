# Validation Sample Data

This directory contains a small synthetic validation set for table occupancy checks. The sample images are committed as SVG text files so diff and review tooling can process them without binary-file errors.
Each `image_XXX.svg` file has a matching `image_XXX_expected.json` file that lists the expected status for tables `T-001` through `T-008`.

## Samples

- `image_001.svg`: empty room; all tables are expected to be `empty`.
- `image_002.svg`: partial occupancy; tables `T-002`, `T-004`, and `T-006` are expected to be `occupied`.
- `image_003.svg`: crowded room; all tables are expected to be `occupied`.
- `image_004.svg`: changed-lighting partial occupancy; tables `T-002`, `T-004`, and `T-006` are expected to be `occupied`.

## Expected JSON schema

Each expected file uses this structure:

```json
{
  "image": "image_001.svg",
  "tables": [
    {
      "table_id": "T-001",
      "expected_status": "empty"
    }
  ]
}
```

Allowed `expected_status` values are `empty` and `occupied`.
