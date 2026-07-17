# Database recovery helpers

This folder contains small helpers for recording and restoring local MySQL databases used by DRHL test applications.

## SCARF

### 1. Capture the current database as the baseline

Run this once when the current `scarf` database is in the state you want to reuse:

```powershell
python database_recovery\scarf_database_recovery.py --capture
```

It writes:

- `database_recovery/scarf/scarf_baseline.sql`
- `database_recovery/scarf/scarf_baseline.metadata.json`

### 2. Restore the database to the recorded baseline

After the baseline exists, simply run:

```powershell
python database_recovery\scarf_database_recovery.py
```

The default action is restore, so running the script without arguments restores the database to `scarf_baseline.sql`.

## events_lister

### 1. Capture the current database as the baseline

Run this once when the current `events_lister` database is in the state you want to reuse:

```powershell
python database_recovery\events_lister_database_recovery.py --capture
```

It writes:

- `database_recovery/events_lister/events_lister_baseline.sql`
- `database_recovery/events_lister/events_lister_baseline.metadata.json`

### 2. Restore the database to the recorded baseline

After the baseline exists, simply run:

```powershell
python database_recovery\events_lister_database_recovery.py
```

The default action is restore, so running the script without arguments restores the database to `events_lister_baseline.sql`.


## mybb

### 1. Capture the current database as the baseline

Run this once when the current `mybb` database is in the state you want to reuse:

```powershell
python database_recovery\mybb_database_recovery.py --capture
```

It writes:

- `database_recovery/mybb/mybb_baseline.sql`
- `database_recovery/mybb/mybb_baseline.metadata.json`

### 2. Restore the database to the recorded baseline

After the baseline exists, simply run:

```powershell
python database_recovery\mybb_database_recovery.py
```

The default action is restore, so running the script without arguments restores the database to `mybb_baseline.sql`.

## django_lms

### 1. Capture the current PostgreSQL database as the baseline

Run this once when the current `lms` PostgreSQL database is in the state you want to reuse:

```powershell
python database_recovery\django_lms_database_recovery.py --capture
```

It writes:

- `database_recovery/django_lms/django_lms_baseline.sql`
- `database_recovery/django_lms/django_lms_baseline.metadata.json`

### 2. Restore the database to the recorded baseline

After the baseline exists, simply run:

```powershell
python database_recovery\django_lms_database_recovery.py
```

The default action is restore, so running the script without arguments restores the database to `django_lms_baseline.sql`.

## Notes

- The SCARF script reads MySQL connection settings from `configs/scarf.json`.
- The events_lister script reads MySQL connection settings from `configs/events_lister.json`.
- The mybb script reads MySQL connection settings from `configs/mybb.json`.
- The baseline SQL file contains the database content. Keep it private if the database contains sensitive data.
- Running `--capture` again overwrites the old baseline with the current database state.
