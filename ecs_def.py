#!/usr/bin/env python3
"""ecs_def.py -- Defines the ECS (short for Eclipse Combat Simulator) class.
Has debugging functionality when called as __main__."""

import sys
import os
import copy
if __name__ != '__main__':
    sys.path.insert(0, os.path.split(__file__)[0])
import player_def
import hull_def
import ship_def
import part_def
import user_input

class ECS:
    """The ECS (Eclipse Combat Simulator) class simulates fleet combat
    between players in the 4X board game "Eclipse" and empirically determines
    the odds of each player emerging victorious. Currently only works with 2
    players."""
    
    def __init__(self):
        print("Welcome to the Eclipse Combat Simulator!")
        self.parts = part_def.Part.GetParts()
        self.hulls = hull_def.Hull.GetHulls()
        self.SetupPlayers()
        self.AssembleFleets()
        print("\nFinished with setup!")
        print("Here are the players participating in combat:")
        for player in self.players:
            print("\n", player)
        print()
        self.sim_results = [0] * (len(self.players) + 1)
        # One column to record number of wins for each player
        # and one final column to record the number of stalemates.
    
    def SetupPlayers(self):
        """Creates a Player object for each person participating in combat."""
        nplayers = 2
        self.players = []
        print("There are %i players participating in combat." % (nplayers))
        print("Player 1 is defending.")
        print("Player 2 is attacking.")
        for i in range(nplayers):
            name = user_input.GetStr("Please enter player %i's name: "
                                          % (i + 1))
            self.players.append(player_def.Player(name))
    
    def AssembleFleets(self):
        """Assembles a fleet for each Player. This involves determining the
        number of Ships of each Hull type controlled by the Player, building
        those Ships (i.e. determining which Parts are attached to them), and
        adding those Ships to the Player's fleet."""
        for player in self.players:
            print("Let's build %s's fleet." % (player.name))
            for hull_name in self.hulls.keys():
                if self.hulls[hull_name].is_mobile == 0 and player.id != 0:
                    # The Player with ID 0 is the defender; they are the only
                    # one who can have immobile Ships (e.g. the space station).
                    continue
                hull = self.hulls[hull_name]
                nships = user_input.GetInt(
                    "How many %ss does %s have (%i-%i)? "
                    % (hull.name, player.name, 0, hull.nmax),
                    True, 0, hull.nmax)
                if nships > 0:
                    print("Okay, let's build those %ss." % (hull.name))
                    # First define the prototype
                    prototype = ship_def.Ship(hull, self.parts, player)
                    for i in range(nships):
                        # Build nships duplicates of this prototype
                        player.fleet.append(
                            ship_def.Ship(hull, self.parts, player,
                            True, prototype.parts))
            # Finished creating Ships for this Player, now sort their fleet
            player.SortFleet()
    
    def RunSimulations(self):
        """Runs combat simulations between Players."""
        if len(self.players) != 2:
            raise RuntimeError(
                "The ECS currently only supports 2 combatants. Sorry!")
        defender = self.players[0]
        attacker = self.players[1]
        # Apply initiative bonus to the defending player.
        for ship in defender.fleet:
            ship.initiative += 0.5
        nsims = user_input.GetInt(
            "How many combat sims should we run? ", True, 1, 1000000)
        sim_num = 0
        print("Running simulation!")
        while sim_num < nsims:
            # Each iteration here is a full combat simulation.
            def_fleet = copy.deepcopy(defender.fleet)
            atk_fleet = copy.deepcopy(attacker.fleet)
            self.SimulateCombat(def_fleet, atk_fleet, sim_num)
            sim_num += 1
        print("Simulations complete.")

    def SimulateCombat(self, def_fleet, atk_fleet, sim_num):
        combat_round = 0
        while (len(def_fleet) > 0 and
               len(atk_fleet) > 0 and
               combat_round < 1000):
            # Each iteration here represents a full round of combat.
            # Combat continues until a fleet has been completely destroyed
            # or a stalemate has developed.
            combat_round += 1
            firing_seq = sorted(def_fleet + atk_fleet,
                key=lambda ship: -ship.initiative)
            while (len(firing_seq) > 0 and
                   len(def_fleet) > 0 and
                   len(atk_fleet) > 0):
                # During each iteration here a group of Ships with identical
                # initiative values fire and are then removed from the
                # firing_seq. Note: we can assume that they are all controlled
                # by the same Player due to how initiative works (defending
                # Player has fractional initiative & attacking Player does not).
                firing_now = [firing_seq.pop(0)]             
                while (len(firing_seq) > 0 and
                       firing_seq[0].initiative == firing_now[0].initiative):
                    firing_now.append(firing_seq.pop(0))
                # At this point, firing_now contains all Ships with the highest
                # initiative value that have not yet fired this round. Now they
                # roll their attacks simultaneously. 
                attacks = [ship.RollAttacks()
                           for ship in firing_now
                           if ship.has_weapon]
                if firing_now[0].owner.id == def_fleet[0].owner.id:
                    # Fire at the attacking fleet
                    self.MakeAttacks(attacks, firing_seq, atk_fleet)
                else:
                    # Fire at the defending fleet
                    self.MakeAttacks(attacks, firing_seq, def_fleet)
        if len(def_fleet) < 1:
            print("Player 2 wins simulation %i" % (sim_num + 1))
            self.sim_results[1] += 1
        elif len(atk_fleet) < 1:
            print("Player 1 wins simulation %i" % (sim_num + 1))
            self.sim_results[0] += 1
        else:
            print("Simulation %i ended in a stalemate" % (sim_num + 1))
            self.sim_results[-1] += 1
        return
    
    def MakeAttacks(self, attacks, firing_seq, opposing_fleet):
        """Takes some number of attack rolls by one of the game's Players and
        applies them to the opponent's Ships. Any Ships that are destroyed are
        removed from the appropriate fleet and from the firing sequence."""
        for attack in attacks:
            if len(opposing_fleet) == 0:
                # All of the opposing Ships have been destroyed; combat is over!
                pass
            elif attack[0] == 1:
                # A natural roll of 1 always misses
                pass
            elif attack[0] == 6:
                # A natural roll of 6 always hits so apply damage to the first
                # Ship in opposing_fleet, which should have the highest
                # kill_priority because fleets are sorted that way.
                opposing_fleet[0].armor -= attack[2]
                if opposing_fleet[0].armor < 1:
                    # This Ship was destroyed by the attack
                    self.DestroyShip(firing_seq, opposing_fleet, 0)
            else:
                # Preferentially attack the opposing Ship with the highest
                # kill_priority, which is located at the beginning of the
                # opposing_fleet list. If we can't hit that Ship, go through the
                # list and attack the first Ship we can hit. If we can't hit any
                # of them, do nothing.
                attack_roll = attack[0] + attack[1]
                for i in range(len(opposing_fleet)):
                    if attack_roll - opposing_fleet[i].shield > 5:
                        # Hit - apply damage to this Ship
                        opposing_fleet[i].armor -= attack[2]
                        if opposing_fleet[i].armor < 1:
                            # This Ship was destroyed by the attack
                            self.DestroyShip(firing_seq, opposing_fleet, i)
                        # The attack is resolved; move on to the next one.
                        break
    
    def DestroyShip(self, firing_seq, opposing_fleet, target_index):
        """Removes the Ship at [target_index] in opposing_fleet from the
        game. Also removes that ship from firing_seq if it has not yet fired
        this round."""
        target_id = opposing_fleet[target_index].id
        del opposing_fleet[target_index]
        for i in range(len(firing_seq)):
            if firing_seq[i].id == target_id:
                del firing_seq[i]
                break
    
    def ReportResults(self):
        """Reports the simulation results to the user."""
        nsims_completed = sum(self.sim_results)
        if nsims_completed == 0:
            print("No simulations have been run yet!")
        else:
            print("\nHere are the simulation results:")
            for i in range(len(self.players)):
                print("%s won %i times (%.2f%% probability)" \
                      % (self.players[i].name, self.sim_results[i], \
                      100. * self.sim_results[i] / nsims_completed))
            if self.sim_results[-1] > 0:
                print("There were %i stalemates (%.2f%% probability)" \
                      % (self.sim_results[-1], \
                      100. * self.sim_results[-1] / nsims_completed))

def main():
    """Creates a new instance of ECS, runs the combat simulation, and
    reports the results."""
    sim = ECS()
    sim.RunSimulations()
    sim.ReportResults()
    print("Thank you for using the ECS!\n")
    
if __name__ == '__main__':
    main()