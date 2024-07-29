# PyBonsai

PyBonsai is a Python script that generates procedural ASCII art trees in the comfort of your terminal.

## About

<img src="/Images/demo.gif" align="right" width="450px">

PyBonsai is inspired by the amazing [cbonsai](https://gitlab.com/jallbrit/cbonsai) repository.
Whereas cbonsai grows bonsai trees, PyBonsai trees look more like trees you would find in a forest (oak, ash and so on).

The trees are configurable via CLI options to make them different sizes, more or less complex, grow at different rates, or use a different set of characters. See [useage](#useage) for more information.

Currently, PyBonsai supports 4 different types of tree. Details of these are shown in the [tree types](#tree-types) section.

PyBonsai uses [ANSI escape codes](https://en.wikipedia.org/wiki/ANSI_escape_code) for colouring characters. Almost all modern terminals will support this but, if yours does not, PyBonsai will not work.

## Installation

Requirements:
- Python 3.6 or greater

To use PyBonsai, you need to first clone the repository:

    git clone https://github.com/Ben-Edwards44/PyBonsai.git

### Linux

To install for all users, run the included `install.sh` script to create a symlink in `/usr/local/bin`

    cd PyBonsai
    sudo chmod +x install.sh
    sudo ./install.sh

Verify the installation by running:

    pybonsai --version

### Windows and Mac OS

Please note that I have only tested PyBonsai on Ubuntu, but I see no reason why it would not work on Windows or Mac OS.
To install PyBonsai, you will need to clone the repository and add it to your system's PATH.

## Useage

Run `pybonsai --help` for useage:

    USEAGE: pybonsai [OPTION]...

    PyBonsai procedurally generates ASCII art trees in your terminal.

    OPTIONS:
    -h, --help           display help
        --version        display version
    -i, --instant        instant mode: display finished tree immediately
    -c, --branch-chars   string of chars randomly chosen for branches [default ~;:=]
    -C, --leaf-chars     string of chars randomly chosen for leaves [default &%#@]
    -w, --wait           time delay between drawing characters when not in instant mode [default 0]
    -x, --width          maximum width of the tree [default 80]
    -y, --height         maximum height of the tree [default 35]
    -t, --type           tree type: integer between 0 and 3 inclusive [default random]
    -s, --seed           seed for the random number generator
    -S, --start-len      length of the root branch [default 15]
    -L, --leaf-len       length of each leaf [default 4]
    -l, --layers         number of branch layers: more => more branches [default 8]
    -a, --angle          mean angle of branches to their parent, in degrees; more => more arched trees [default 40]

The following images demonstrate the use of the different options:

| Effect               | Image                                      |
|----------------------|--------------------------------------------|
| Big tree             | ![big tree](/Images/big.png)               |
| Different characters | ![different characters](/Images/chars.png) |
| Longer leaves        | ![longer leaves](/Images/leafy.png)        |


## Tree Types

tbc...