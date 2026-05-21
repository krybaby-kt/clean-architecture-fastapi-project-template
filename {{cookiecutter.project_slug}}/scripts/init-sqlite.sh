#!/bin/sh
# POSIX sh — works on Alpine without bash.
set -e

DB_PATH="/data/{{ cookiecutter.database_name }}.db"

mkdir -p /data

if [ ! -f "$DB_PATH" ]; then
    echo "Creating SQLite database at $DB_PATH"
    : > "$DB_PATH"
    chmod 666 "$DB_PATH"
else
    echo "SQLite database already exists at $DB_PATH"
fi

echo "SQLite init complete"
