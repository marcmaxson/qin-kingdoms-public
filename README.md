Here's a sample README file for the [Qin Kingdoms](https://github.com/marcmaxson/qin-kingdoms-public) GitHub repository:

---

# Qin Kingdoms

Welcome to the Qin Kingdoms project! This repository is dedicated to the development of a historical simulation game set in ancient China during the Warring States period.

## Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)

## Introduction

Qin Kingdoms is a strategy game that immerses players in the political, economic, and military complexities of ancient China. Players can control different states, manage resources, build armies, and engage in diplomacy and warfare to unify China under their rule.

## Features

- **Historical Accuracy**: Detailed representation of the Warring States period with historically accurate factions and events.
- **Strategic Gameplay**: Complex resource management, city building, and military tactics.
- **Diplomacy and Alliances**: Engage in negotiations, form alliances, and manage relationships with other states.
- **Rich Graphics**: High-quality graphics and immersive sound effects.

## Installation

To install and run Qin Kingdoms locally, follow these steps:

1. Clone the repository:
   ```sh
   git clone https://github.com/marcmaxson/qin-kingdoms-public.git
   ```

2. Navigate to the project directory:
   ```sh
   cd qin-kingdoms-public
   ```

3. Install the required dependencies:
   ```sh
   npm install
   ```

4. Start the development server:
   ```sh
   npm start
   ```

5. Open your web browser and go to `http://localhost:3000` to start playing.

## Usage

Detailed usage instructions and game rules are provided within the game. Explore the various menus and options to get familiar with the gameplay mechanics.

## Contributing

We welcome contributions from the community! To contribute:

1. Fork the repository.
2. Create a new branch for your feature or bugfix:
   ```sh
   git checkout -b feature-name
   ```
3. Make your changes and commit them with descriptive messages.
4. Push your changes to your forked repository:
   ```sh
   git push origin feature-name
   ```
5. Open a pull request in the main repository.

Please refer to our [Contributing Guide](CONTRIBUTING.md) for more details.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.

## Acknowledgements

Special thanks to all the contributors and the open-source community for their support and contributions.

## Changelog (and list of early design bug fixes)

### RESOLVED TODOs:
[x] 1. random map generator

[x] 2. attach unit info to board (not maphex); allow movement

[x] 3. add multiple armies; allow movement

[x] 4. add generals to armies; count movement points; next army only after finished moving;

[x] 5. mobilize works; player shields; added forests; add enemy armies; basic attacking/defending

[x] 6. subtract troops from attacks;

[x] 7. add castles (a random number, centralized, and adjacent to each other)

[x] 7. [took 1 week] any size board supported with scrolling
        allow screen to scroll when unit moves close to edge

[x] 7. put cursor and armies back on board

[x] 7. place enemy on castles to start


[x] 8. shift view to active army

[x] 8. prevent starting squares from being in water/mtn

[x] 8. ENEMY AI; path_to_enemy; finds nearest_enemy_army
        ignores mountains and accounts for terrain types in shortest path
        finds weakest enemy (calculates power ratio and sorts); choose attack/defend/range
[x] 8. moves towards best enemy to attack; attacks adjacent enemies; self.is_adjacent works!

[x] 9. basic side message console (vanilla, not using pygame-gui yet)

[x] 10. (Monday July 24, 2023)
        capture army works - moves to self.dead_armies
        enemies still not moving towards army well yet.
        self.menu_display - useful and versatile message function for all combat stuff.
        mobilize is not storing movement. Only +1 gets saved for human moves, but the console shows all saved movement.
        (might be same for AI)
        most messages are in console now.
        end of turn bug fixed (centers on new army)
        AI army blocked (add square into game grid and recalculate
        FIXED bug: FIRST time you move first army, background overwrites army; fix with enemy moving first?
        Fixed bug: enemy army can always attack me if left-1 and up-2; x is even.
        from enemy (6,3) attacking (5,2); so (6,3) is NOT next to (5,2) e.g. x-1, y-1 when x % 2 == 0
        also: (8, 7) to (7, 6) movement was 2 hexes (x-1, y-1) on even x-row.
        also: (10, 6), (11, 5) up+right on even row
        likely fixed: if enemy path crosses water, enemy doesnt store up movement points to cross        
        added (V)IEW MODE -(sub-loop where keys respond but locks out all other moves until ESC)

[x] 11. detects 2 hexes away consistently (for ranged attack)
        shows targeted hexes on screen, with specific army shown
        FUTURE: [TAB]: changes target -- not quite yet
        (r)anged attack works!
        FUTURE: move the "two_away()" function to return those spots, so enemy AI can know it is in range.
        FUTURE: animate volley of arrows from army to army        

[x] 12. battle ends with win/loss conditions (time up, armies defeated, all castles occupied)
        add +naval bonus; you lost worked;
        ComputerAI has a working three_hexes_away map (for ballistas)

[x] 13. detects mouse clicks on board; converts to screen hex position.
        ballistas work (3 hexes away)
        barricade (pikemen bonus)
        forest range defense bonus
        randomness to ranged attack results
        changed generals to 25-99 range instead of 10-99 range for abilities
        fix AI: blocked by other army (recalcs and goes around)
        view mode: shows army stats under cursor
        display possible move keys below army
        works: actually test all_castles_filled, all invaders dead
        AI: if range attack, use it instead of regular attack
        AI: only regular attack once
        Check castles only at end of turn
        FINALLY FIXED the first turn cursor bug!
        range attack bug: if off screen, scroll to them first.

[x] 14. mouse/touch control movement
        make 2-min demo video with loom
        mouse/touch side menu buttons
        refactor code army.owner != instead of 0 vs 1 (so 2,3,4 etc will work)
        mouseover hightlight buttons
        battle_test_AI -- calls game_loop with 2 computer players, and game runs!
        battle_test_AI.py -- able to watch game play at 100X speed and log results!

[x] 15. tracking win/loss data in log; fixing various AI bugs that broke game.
        bug: 21 days are up is always the end condition. did not exit when finds no army left.
        add experience at end of battle, to help with calculating best/worst styles
            experience is divided among all surviving generals of winning side, and is
            exp = (net troop loss / 10); or if a draw (sum troop loss/4) per army

[x] 16. plot results of 120 battles
        AI_level 3 options (player level difficulty)
        Track AI test options for plots
        have plotter show "test note" separately - works! And proves barricade improves def win rate 3X.

[x] 17. computerAI: range, backup
        I THINK I FIXED BUGS:
        DEF heavy infantry 5/5 with 100 troops not attacking anybody, just sits on castle
        despite being the biggest army. Does not attack adjacent either (lvl 4)
        DEF (level 4) infantry and militia not attacking me (from castle)
        DEF archers moved right next to my army instead of stopped 2 away
        DEF 5/2 calv did not engage any troops (level 4)
        FIX: if total friend army size is larger than enemy, AND
        another friend army is nearby,
        go ahead and engage the closest enemy (more aggressively):
        because two or littler armies will beat one larger one. current DEF AI waits
        if each army is weaker than the one invader.
        made archers 2/2 instead of 2/3
        ADDED: General's specialty adds +1 to attack, or if pikemen, +1 to defense, or if range, +1 range attack,
        if unit type matches their specialty type
        BUG -- battle_test: when armies are exactly even, nobody attacks
        (not a problem with lvl 1 (brute force))

### UNRESOLVED ISSUES:

BUG: I have one army left, but game keeps skipping it's move.
BUG: Why does it spin wheels when army is captured. Next turn function seems to have a slow step?

Add - if two foe armies nearby, move towards the weaker one
(a genetic algo step; not always the best move, but leads to more strategies)
Add - Pikemen: move between archer and army and barricade. (lvl5)

- AI: hide behind army or with mountains between army and enemy
- AI: if range and blocked, don't pass, move towards allied army instead
- add fire
- add loyalty (and switching)
- add rice (lvl5 DEF)
    - move towards rice, if rice unguarded
- lvl 5: set fire, if outnumbered
- lvl 6: move away from enemies, if outnumbered and more castles than can be occupied
- add mouse and fingerdown/fingerup/fingermotion tablet support
- range [TAB] to change target 
- toggle tileset from retro NES to modern tiles to cartoonish tiles
- captured generals: add to Player class for (main game state)
    - future: option to redeploy captured generals with 100 men on board (taken from army that defeated it)
    - add warning if loyalty is below 40
- linear interpolation when scrolling
- ??? for large maps, use random seed terrain types and grow the pieces around them,
- future, harder: split to defend archers from enemy

---

For more detailed documentation and updates, please visit our [GitHub repository](https://github.com/marcmaxson/qin-kingdoms-public).
