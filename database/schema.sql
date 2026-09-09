-- ============================================================
-- Electrical Engineering Suite
-- SQLite Database Schema
-- Version: 0.1.0
-- ============================================================


-- ============================================================
-- PROJECTS
-- Stores engineering projects.
-- ============================================================

CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    name TEXT NOT NULL,

    description TEXT,

    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);


-- ============================================================
-- CALCULATIONS
-- Stores calculations performed by users.
-- ============================================================

CREATE TABLE IF NOT EXISTS calculations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    project_id INTEGER,

    calculation_type TEXT NOT NULL,

    input_data TEXT NOT NULL,

    result_data TEXT NOT NULL,

    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (project_id)
        REFERENCES projects(id)
        ON DELETE SET NULL
);


-- ============================================================
-- SETTINGS
-- Stores application settings.
-- ============================================================

CREATE TABLE IF NOT EXISTS settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    setting_name TEXT NOT NULL UNIQUE,

    setting_value TEXT,

    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);


-- ============================================================
-- USERS
-- Basic user information.
-- Authentication will be added later.
-- ============================================================

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    username TEXT NOT NULL UNIQUE,

    display_name TEXT,

    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);