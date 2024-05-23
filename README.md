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

3. Install nbaDB.db

    https://kaggle.com/datasets/8e63bac156b2f779188ae0eff48ea602f347ab59e98b413e261e95fc6161375c

    ```
    mkdir data
    ```
    把剛才下載好的nbaDB放進data中

3. Build the client

    - [`npm`](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm)

    ```shell
    cd web/
    npm install
    npm run build
    cd ../
    ```

4. Run the server

    ```shell
    python -m main
    ```
