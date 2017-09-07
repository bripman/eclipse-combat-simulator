#!/usr/bin/env python3
"""ecs_def.py -- Defines the ECS (short for Eclipse Combat Simulator)
class. Has debugging functionality when called as __main__.
"""

import sys
import os
import copy

import player
import hull
import ship
import part
import user_input

if __name__ != '__main__':
    sys.path.insert(0, os.path.split(__file__)[0])


class ECS:
    """The ECS (Eclipse Combat Simulator) class simulates fleet combat
    between players in the 4X board game "Eclipse" and empirically
    determines the odds of each player emerging victorious. Currently
    only works with two players.
    """
    
    def __init__(self):
        print("Welcome to the Eclipse Combat Simulator!")
        self.parts = part.Part.get_parts()
        self.hulls = hull.Hull.get_hulls()
        self.setup_players()
        self.assemble_fleets()
        print("\nFinished with setup!")
        print("Here are the players participating in combat:")
        for a_player in self.players:
            print("\n", a_player)
        print()
        self.sim_results = [0] * (len(self.players) + 1)
        # One column to record the number of wins for each player and
        # one final column to record the number of stalemates.

    def setup_players(self):
        """Creates a Player object for each person participating in
        combat.
        """
        nplayers = 2
        self.players = []
        print("There are %i players participating in combat."% (nplayers))
        print("Player 1 is defending.")
        print("Player 2 is attacking.")
        for i in range(nplayers):
            name = user_input.get_str("Please enter player %i's name: "
                                          % (i + 1))
            self.players.append(player.Player(name))
        self.players[0].is_defending = 1

    def assemble_fleets(self):
        """Assembles a fleet for each player. This involves determining
        the number of ships of each hull type controlled by the player,
        building those ships, and adding those ships to the player's
        fleet.
        """
        for a_player in self.players:
            print("Let's build %s's fleet." % (a_player.name))
            for hull_name in self.hulls.keys():
                if (self.hulls[hull_name].is_mobile == 0 and not
                        a_player.is_defending):
                    # The defending player is the only one who can have
                    # immobile ships, e.g. the Space Station
                    continue
                a_hull = self.hulls[hull_name]
                nships = user_input.get_int(
                    "How many %ss does %s have (%i-%i)? "
                    % (a_hull.name, a_player.name, 0, a_hull.nmax),
                    True, 0, a_hull.nmax)
                if nships > 0:
                    print("Okay, let's build those %ss."
                        % (a_hull.name))
                    # First define the prototype
                    prototype = ship.Ship(a_hull,
                        self.parts, a_player)
                    for i in range(nships):
                        # Build nships duplicates of this prototype
                        a_player.fleet.append(
                            ship.Ship(a_hull, self.parts, a_player,
                            True, prototype.parts))
            a_player.sort_fleet()
    
    def run_simulations(self):
        """Runs combat simulations between two players."""
        if len(self.players) != 2:
            raise RuntimeError(
                "The ECS currently only supports 2 combatants. Sorry!")
        nsims = user_input.get_int(
            "How many combat sims should we run? ", True, 1, 10000)
        sim_num = 0
        print("Running simulation!")
        while sim_num < nsims:
            sim_num += 1
            defender = copy.deepcopy(self.players[0])
            attacker = copy.deepcopy(self.players[1])
            self.simulate_combat(defender, attacker, sim_num)
        print("Simulations complete.")

    def simulate_combat(self, defender, attacker, sim_num):
        """Simulates an instance of combat between two players from
        beginning to end.
        """
        combat_round = 1
        # Begin combat by resolving missile attacks
        self.roll_attacks(defender, attacker, False, True)
        # Now re-sort both fleets since kill_priority may have changed
        # when missile weapons were exhausted
        defender.sort_fleet()
        attacker.sort_fleet()
        while (len(defender.fleet) > 0 and
               len(attacker.fleet) > 0 and
               combat_round < 1000):
            # Each iteration here represents a full round of combat.
            # Combat continues until a fleet has been completely
            # destroyed or a stalemate has developed.
            self.roll_attacks(defender, attacker)
            combat_round += 1
        if len(defender.fleet) < 1:
            print("Player 2 wins simulation %i" % (sim_num))
            self.sim_results[1] += 1
        elif len(attacker.fleet) < 1:
            print("Player 1 wins simulation %i" % (sim_num))
            self.sim_results[0] += 1
        else:
            print("Simulation %i ended in a stalemate" % (sim_num))
            self.sim_results[-1] += 1

    def roll_attacks(self, defender, attacker,
                     firing_conventionals = True,
                     firing_missiles = False):
        """Makes attacks for all ships in combat."""
        firing_seq = sorted(defender.fleet + attacker.fleet,
            key=lambda a_ship: a_ship.initiative)
        while (len(firing_seq) > 0 and
               len(defender.fleet) > 0 and
               len(attacker.fleet) > 0):
            # During each iteration here a group of ships with
            # identical initiative values fire and are then removed
            # from the firing_seq. Note: we can assume that they are
            # all controlled by the same player due to how initiative
            # works (defending player has fractional initiative &
            # attacking player does not).
            firing_now = [firing_seq.pop()]             
            while (len(firing_seq) > 0 and
                   firing_seq[-1].initiative == firing_now[-1].initiative):
                firing_now.append(firing_seq.pop())
            # At this point, firing_now contains all ships with the
            # highest initiative value that have not yet fired. Now
            # they roll their attacks simultaneously.
            if firing_conventionals:
                attacks = [a_ship.roll_conventional_attacks()
                           for a_ship in firing_now]
            elif firing_missiles:
                attacks = [a_ship.roll_missile_attacks()
                           for a_ship in firing_now]
            else:
                # What the hell are we supposed to be firing?
                raise RuntimeError("roll_attacks called with bad args!")
            # Remove None values from ships that didn't make attacks
            attacks = [x for x in attacks if x is not None]
            # Then unpack all of the lists of tuples into one list
            attacks = [x for y in attacks for x in y]
            if not attacks:
                continue
            if firing_now[0].owner.id == defender.id:
                # Fire at the attacking fleet
                self.apply_attacks(attacks, firing_seq, attacker)
            else:
                # Fire at the defending fleet
                self.apply_attacks(attacks, firing_seq, defender)

    def apply_attacks(self, attacks, firing_seq, opponent):
        """Takes a collecton of attack rolls and applies them to the
        ships in an opposing fleet.
        """
        for attack in attacks:
            if len(opponent.fleet) == 0:
                # All of the opposing ships have been destroyed
                break
            elif attack[0] == 1:
                # A natural roll of 1 always misses
                pass
            elif attack[0] == 6:
                # A natural roll of 6 always hits so apply damage to
                # the first ship in the opponent's fleet, which should
                # have the highest kill_priority because fleets are
                # sorted that way.
                self.apply_damage(attack, opponent.fleet[0].id,
                                 firing_seq, opponent)
            else:
                # Preferentially attack the opposing ship with the 
                # highest kill_priority, which is located at the
                # beginning of the opponent's fleet. If we can't hit
                # that ship, go through the list and attack the first
                # ship we can hit. If we can't hit any of them, do
                # nothing.
                hit_roll = attack[0] + attack[1]
                for i in range(len(opponent.fleet)):
                    if hit_roll - opponent.fleet[i].shield > 5:
                        self.apply_damage(attack, opponent.fleet[i].id,
                                         firing_seq, opponent)
                        # Attack is resolved, move on to the next one
                        break

    def apply_damage(self, attack, target_id, firing_seq, opponent):
        """Applies damage from a single attack to a specific ship in
        the opposing fleet.
        """
        for a_ship in opponent.fleet:
            if a_ship.id == target_id:
                # This is the target - apply damage to it
                a_ship.armor -= attack[2]
                if a_ship.armor < 1:
                    # This ship was destroyed by the attack
                    self.destroy_ship(target_id, firing_seq, opponent)
                # Attack is resolved
                break

    def destroy_ship(self, target_id, firing_seq, opponent):
        """Removes a destroyed ship from its owner's fleet and from the
        firing sequence for this round.
        """
        for i in range(len(opponent.fleet)):
            if opponent.fleet[i].id == target_id:
                del opponent.fleet[i]
                break
        for i in range(len(firing_seq)):
            if firing_seq[i].id == target_id:
                del firing_seq[i]
                break

    def report_results(self):
        """Reports the simulation results to the user."""
        nsims_completed = sum(self.sim_results)
        if nsims_completed == 0:
            print("No simulations have been run yet!")
        else:
            print("\nHere are the simulation results:")
            for i in range(len(self.players)):
                print("%s won %i times (%.2f%% probability)"
                      % (self.players[i].name, self.sim_results[i],
                      100. * self.sim_results[i] / nsims_completed))
            if self.sim_results[-1] > 0:
                print("There were %i stalemates (%.2f%% probability)"
                      % (self.sim_results[-1],
                      100. * self.sim_results[-1] / nsims_completed))


def main():
    """Creates a new instance of ECS, runs the combat simulation, and
    reports the results.
    """
    sim = ECS()
    sim.run_simulations()
    sim.report_results()
    print("Thank you for using the ECS!\n")


if __name__ == '__main__':
    main()