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
        # One column to record the number of wins for each player and one final
        # column to record the number of stalemates.
    
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
        self.players[0].is_defending = 1
    
    def AssembleFleets(self):
        """Assembles a fleet for each player. This involves determining the
        number of ships of each hull type controlled by the player, building
        those ships, and adding those ships to the player's fleet."""
        for player in self.players:
            print("Let's build %s's fleet." % (player.name))
            for hull_name in self.hulls.keys():
                if (self.hulls[hull_name].is_mobile == 0 and not
                        player.is_defending):
                    # The defending player is the only one who can have immobile
                    # ships (e.g. the Space Station).
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
            # Sort the fleet by descending kill_priority. The combat algorithm
            # currently relies on this, which is kludgey.
            player.fleet = sorted(
                player.fleet, key=lambda ship: -ship.kill_priority)
    
    def RunSimulations(self):
        """Runs combat simulations between two players."""
        if len(self.players) != 2:
            raise RuntimeError(
                "The ECS currently only supports 2 combatants. Sorry!")
        defender = self.players[0]
        attacker = self.players[1]
        nsims = user_input.GetInt(
            "How many combat sims should we run? ", True, 1, 1000000)
        sim_num = 0
        print("Running simulation!")
        while sim_num < nsims:
            # Each iteration here is a full combat simulation.
            sim_num += 1
            def_fleet = copy.deepcopy(defender.fleet)
            atk_fleet = copy.deepcopy(attacker.fleet)
            self.SimulateCombat(def_fleet, atk_fleet, sim_num)
        print("Simulations complete.")

    def SimulateCombat(self, def_fleet, atk_fleet, sim_num):
        """Simulates an instance of combat between two players from
        beginning to end."""
        # Begin combat by resolving missile attacks
        self.RollAttacks(def_fleet, atk_fleet, False, True)
        # Now have to re-sort both fleets since kill_priority may have changed
        # when missile weapons were exhausted.
        def_fleet = sorted(
                def_fleet, key=lambda ship: -ship.kill_priority)
        atk_fleet = sorted(
                atk_fleet, key=lambda ship: -ship.kill_priority)
        combat_round = 1
        while (len(def_fleet) > 0 and
               len(atk_fleet) > 0 and
               combat_round < 1000):
            # Each iteration here represents a full round of combat.
            # Combat continues until a fleet has been completely destroyed
            # or a stalemate has developed.
            self.RollAttacks(def_fleet, atk_fleet)
            combat_round += 1
        if len(def_fleet) < 1:
            print("Player 2 wins simulation %i" % (sim_num))
            self.sim_results[1] += 1
        elif len(atk_fleet) < 1:
            print("Player 1 wins simulation %i" % (sim_num))
            self.sim_results[0] += 1
        else:
            print("Simulation %i ended in a stalemate" % (sim_num))
            self.sim_results[-1] += 1

    def RollAttacks(self, def_fleet, atk_fleet,
                     firing_conventionals = True,
                     firing_missiles = False):
        """Makes attacks for all ships in combat."""
        firing_seq = sorted(def_fleet + atk_fleet,
            key=lambda ship: ship.initiative)
        while (len(firing_seq) > 0 and
               len(def_fleet) > 0 and
               len(atk_fleet) > 0):
            # During each iteration here a group of Ships with identical
            # initiative values fire and are then removed from the
            # firing_seq. Note: we can assume that they are all controlled
            # by the same Player due to how initiative works (defending
            # Player has fractional initiative & attacking Player does not).
            firing_now = [firing_seq.pop()]             
            while (len(firing_seq) > 0 and
                   firing_seq[-1].initiative == firing_now[-1].initiative):
                firing_now.append(firing_seq.pop())
            # At this point, firing_now contains all Ships with the highest
            # initiative value that have not yet fired. Now they roll their
            # attacks simultaneously.
            if firing_conventionals:
                attacks = [ship.RollConventionalAttacks()
                           for ship in firing_now]
            elif firing_missiles:
                attacks = [ship.RollMissileAttacks()
                           for ship in firing_now]
            else:
                # What the hell are we supposed to be firing?
                print("RollAttacks called with bad args!")
                continue
            # Remove any None values from ships that didn't make any attacks
            attacks = [x for x in attacks if x != None]
            # Then unpack all of the lists of tuples into one list
            attacks = [x for y in attacks for x in y]
            if len(attacks) == 0:
                # No attacks to make so we're finished
                continue
            if firing_now[0].owner.id == def_fleet[0].owner.id:
                # Fire at the attacking fleet
                self.ApplyAttacks(attacks, firing_seq, atk_fleet)
            else:
                # Fire at the defending fleet
                self.ApplyAttacks(attacks, firing_seq, def_fleet)
    
    def ApplyAttacks(self, attacks, firing_seq, opp_fleet):
        """Takes a collecton of attack rolls and applies them to the ships in an
        opposing fleet."""
        for attack in attacks:
            if len(opp_fleet) == 0:
                # All of the opposing Ships have been destroyed
                break
            elif attack[0] == 1:
                # A natural roll of 1 always misses
                pass
            elif attack[0] == 6:
                # A natural roll of 6 always hits so apply damage to the first
                # ship in opp_fleet, which should have the highest
                # kill_priority because fleets are sorted that way.
                self.ApplyDamage(attack, opp_fleet[0].id, firing_seq, opp_fleet)
            else:
                # Preferentially attack the opposing ship with the highest
                # kill_priority, which is located at the beginning of the
                # opp_fleet list. If we can't hit that ship, go through the
                # list and attack the first ship we can hit. If we can't hit any
                # of them, do nothing.
                hit_roll = attack[0] + attack[1]
                for i in range(len(opp_fleet)):
                    if hit_roll - opp_fleet[i].shield > 5:
                        self.ApplyDamage(attack, opp_fleet[i].id,
                                         firing_seq, opp_fleet)
                        # The attack is resolved; move on to the next one.
                        break

    def ApplyDamage(self, attack, target_id, firing_seq, opp_fleet):
        """Applies damage from a single attack to a specific ship in the firing
        sequence and in the opposing fleet."""
        for ship in opp_fleet:
            if ship.id == target_id:
                # This is the target - apply damage to it
                ship.armor -= attack[2]
                if ship.armor < 1:
                    # This ship was destroyed by the attack
                    self.DestroyShip(target_id, firing_seq, opp_fleet)
                # Finished resolving this attack
                break
        
    
    def DestroyShip(self, target_id, firing_seq, opp_fleet):
        """Removes a destroyed ship from combat."""
        for i in range(len(opp_fleet)):
            if opp_fleet[i].id == target_id:
                del opp_fleet[i]
                break
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