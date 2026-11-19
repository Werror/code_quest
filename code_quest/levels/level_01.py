from .level import Level

LEVEL_01 = Level(
    name="Level 1",
    rows=[
        "################",
        "#P.....#.......#",
        "#.####.#.#####.#",
        "#.#C...#.#...#.#",
        "#.#.####.#.C.#.#",
        "#.#......#...#.#",
        "#.########.###.#",
        "#..........#...#",
        "####.#####.#.###",
        "#C...#...#.#...#",
        "#.##...#...#.G.#",
        "################",
    ],
    starter_code=(
        "# INPUT:  wallet = gold you have\n"
        "# OUTPUT: wallet = gold after coin\n"
        "# This runs once for every coin.\n"
        "# Goal: each coin adds 1 gold.\n"
        "\n"
        "wallet = wallet   # <- change me"
    ),
)
