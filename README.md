
# NNIATE Student Counsil's feedback telegram bot

## How to run

* ### Run via Docker

```shell
    # build image
    docker build \
      -f docker/files/Dockerfile \
      -t sc-nniate-feedback-telegram-bot:latest \
      .
```
```shell
    # launch container
    docker compose \
      -f docker/docker-compose.yml \
      --project-directory . \
      up -d
```
```shell
    # stop container
    docker compose \
      -f docker/docker-compose.yml \
      --project-directory . \
      down
```

> Note: You still have to clone 
> the project repository data to build docker image in place

---

* ### Run via native/local shell

    - Step 1:

      Install python ver. ~3.11

    - Step 2:
      ```shell
        python -m venv venv
      ```
    
    - Step 3:

      Attach python venv into terminal via venv/Scripts/*(your_os_option)*

    - Step 4:
      ```shell
        pip install -r requirements.txt
      ```

    - STEP 6

      ```shell
        python -m src/main
      ```



---

> NOTE: It is necessary to copy [.env.example](.env.example) 
> contents to **YOUR** custom .env end **EDIT IT WITH YOUR VALUES**
> **BEFORE YOU FOLLOW ANY OF APPROACHES**
