import os

# Importing app.models (needed for the shared ServiceType) loads app.config,
# which requires DATABASE_URL. Unit tests never connect, so any URL works.
os.environ.setdefault("DATABASE_URL", "sqlite://")
