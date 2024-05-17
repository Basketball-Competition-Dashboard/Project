# Project

## Installation

### 1. Clone the repository and sub-modules

```shell
git clone --recursive https://github.com/Basketball-Competition-Dashboard/Project.git
cd Project
```

### 2. Install the dependencies for the server

- [`pip`](https://pip.pypa.io/en/stable/installation/)

```shell
pip install -Ur requirements.txt
```

### 3. Build the client

- [`npm`](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm)

```shell
cd web/
npm install
npm run build
cd ../
```

### 4. Run the server

```shell
python -m main
```
