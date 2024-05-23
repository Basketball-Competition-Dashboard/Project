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

    - 把下載好的 `nbaDB.db` 放進 data 中

        ```shell
        mkdir data
        cp nbaDB.db data/
        ```

4. Build the client

    - [`npm`](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm)

        ```shell
        cd web/
        npm install
        npm run build
        cd ../
        ```

5. Run the server

    ```shell
    python -m main
    ```
