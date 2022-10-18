# Getting Started

Launchbox is primarily developed on macOS systems and is used on Ubuntu container images in the cloud.
We are open to supporting other operating systems; please
[review our contribution guidelines](https://github.com/nasa-jpl/launchbox/blob/main/CONTRIBUTING.md)
if you would like to help add that support!


## Requirements

If you're running on macOS, the only real requirement that isn't preinstalled is [Docker](https://www.docker.com).


## Steps

1. Clone the Launchbox repo:
   ```bash
    git clone https://github.com/nasa-jpl/launchbox
   ```

2. Enter the newly created launchbox folder:
   ```bash
   cd launchbox
   ```

3. Setup your `.env` file:
   ```bash
   cp .env.dist .env
   ```
   Update or add to `.env` as needed. In particular, if you intend to use any private repositories as the source for a service, you will need to create a Personal Access Token and set `GIT_TOKEN` to that.

4. Build the Docker container:
   ```bash
   make devbuild
   ```

5. Start the Docker container:
   ```bash
   make start
   ```

6. In a new terminal, open the Launchbox dashboard:
   ```bash
   make dashboard
   ```

7. Install our demo service:
    1. Go to the Services section of the dashboard and click the **New Service** button
    2. Enter the following:
        - **Service Identifier:** demo
        - **Service Name:** Launchbox Demo
        - **Repo URL:** https://github.com/nasa-jpl/launchbox-demo-service
        - **Branch:** main
        - **Environment Name:** development
    3. Click the **Create** button
    4. On the new row in the All Services table, click the **View** button on the right
    5. Click the **Deployments** tab
    6. Click the **Deploy** button on the right of the top row
    7. Go to the Deploys section, wait a minute or so, and refresh a few times
       until you see that the deployment you just triggered is complete
        - Tip: You can also click the deployment's **View** button
          to see the progress of individual deployment steps. (This page auto-refreshes.)

8. Create a site using the demo service:
    1. Go to the Sites section and click the **New Site** button
    2. Give it a **Site Identifier**, choose the **demo** service, and click the **Create** button
    3. On the new row in the All Sites table, click the **View** button on the right
    4. Click the **Hostnames** tab
    5. In the **new hostname** field, enter `demo.launchbox.run`, then click **Add Hostname**
    6. Click the link that appears in the Hostname column in the new row to open the demo site in a new tab
