# Project

## Installation

1. Clone the repository and sub-modules

    ```shell
    git clone https://github.com/Basketball-Competition-Dashboard/Project.git
    cd Project
    git submodule update --init --recursive --remote
    ```

2. Install the dependencies for the server

    - [`pip`](https://pip.pypa.io/en/stable/installation/)

        ```shell
        pip install -Ur requirements.txt
        ```

3. Install the database

    - Download link: https://kaggle.com/datasets/8e63bac156b2f779188ae0eff48ea602f347ab59e98b413e261e95fc6161375c

    - Put the downloaded file `nbaDB.db` to `data/`

        ```shell
        cp nbaDB.db data/
        ```

4. Build the client

    - [`bun`](https://bun.sh)

        ```shell
        cd web/
        bun install --no-save
        bun run build
        cd ../
        ```

5. Run the server

    ```shell
    python -m main
    ```

## Development

1. Try to update all dependencies by following the [installation steps](#installation) if you have encountered any issue.
2. The site URL is [http://127.0.0.1:5000](http://127.0.0.1:5000)
3. The Web API documentation URL is [http://127.0.0.1:5000/_doc/api/web](http://127.0.0.1:5000/_doc/api/web)
