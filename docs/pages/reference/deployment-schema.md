# Deployment Schema

- deployment
    - represents each deployment attempt
    - schema:
        - unique identifier: `deployment_id` (UUID)
        - attrs:
            - `service_id` -> service
            - `commit_sha`
