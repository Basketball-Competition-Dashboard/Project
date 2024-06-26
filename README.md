# Project

## Documentation

Please refer to the [doc repository](https://github.com/Basketball-Competition-Dashboard/doc) for more information.

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
        python3 -m pip install -Ur requirements.txt
        ```

3. Install the database

    - Download link: https://kaggle.com/datasets/8e63bac156b2f779188ae0eff48ea602f347ab59e98b413e261e95fc6161375c

    - Put the downloaded file `nbaDB.db` to `data/`

        ```shell
        cp nbaDB.db data/
        ```

4. Build the client

    - [`bun`](https://bun.sh) or [`npm`](https://www.npmjs.com/)

        ```shell
        cd web/
        bun install --no-save
        bun run build
        cd ../
        ```

5. Run the server!

    ```shell
    python3 -m main
    ```

## Usage

Authentication is required for some endpoints. One of the default username and password are `Demo Manager Zoe` and `A super safe password!`.

## Development

1. Try to update all dependencies by following the [installation steps](#installation) if you have encountered any issue.
2. The site URL is [http://localhost:5000](http://localhost:5000)
3. The Web API documentation URL is [http://localhost:5000/_doc/api/web](http://localhost:5000/_doc/api/web)
4. The Web E2E tests are run by the following command:

    ```shell
    cd web/
    bun run test-e2e
    ```
