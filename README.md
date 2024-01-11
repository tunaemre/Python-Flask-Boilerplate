A boilerplate project written in Python and built using Flask, Celery and common packages.
Auth0 used for authentication purposes.

## Migrations
Before starting the project, make sure your development DB is up-to-date. 
Run the following command in src folder:

    flask db upgrade

If you make a change that requires a DB schema update, create a migration:

    flask db migrate -m "<migration_message>"

If you create empty revision file, create with this command:

    flask db revision -m "<migration_message>"

If you want to downgrade to a specific revision of a migration:

    flask db downgrade <revision_id>
