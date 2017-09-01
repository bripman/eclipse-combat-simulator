#!/usr/bin/env python
"""ecs_def.py -- Defines the ECS (short for Eclipse Combat Simulator) class.
Has debugging functionality when called as __main__."""

"""
To do:
- Make sure I'm managing Parts correctly (there's a list of Parts stored in each
  instance of the ECS class and that list keeps track of whether each Part is
  available but I generate Parts in other places as well.)
- I saved the default_parts for each Hull as a list of Part objects. Is this
  needlessly inefficient? There will be a lot of unneeded Part objects out there
  this way... could just have it be a list of names instead. Actually, is this 
  even true? Currently we make a list of Hulls, each of which has a list of
  default parts. Then each individual Ship's Hull references the same object, so
  I think it's actually not that inefficient.
- Generally speaking, I think the way I'm handling objects is sloppy and leaves
  the program open to errors in the future. Rethink this once I have it working
  again.
- Add more error-checking
- Fix doc strings to be PEP8 compliant, ensure all lines are <80 lines, etc.
- Make sure that constructed ships never have more than 1 empty slot (or better
  yet, have that as a property of the Hull class and check it as a function in
  Verify_Legality or whatever.
- kill_priority stat could stand to be improved (currently takes shield
  into account when determining toughness, but shield isn't relevant if
  opponents' ships have no hit bonus. Maybe opponent's ships should each
  calculate kill_priority values for themselves? Then they could take into
  account their own hit bonuses and initiative and damage output and so on.
- Right now we have automated target priority. Would be nice to add manual entry
  of target priority by ship type, e.g. I want my cruisers to attack their
  dreadnought, my interceptors to attack their cruisers, and so on.
- Make it so that ancient parts go back to the correct place in the parts list
  when they're returned.
- Should make sure both sides have at least one ship and one weapon or else
  combat might never end.
- At one point I got rid of the owner_id and owner_name attributes of the Ship
  class and replaced them with self.owner (the Player object). In practice this
  slows the code down by a factor of 100 or more. Use the profiler to figure out
  what's going on.
- Maybe the two static methods BuildShip and BuildDefaultShip should be folded
  into the constructor for the Ship class:

  class Ship:
      ships = 0 # Used to tag each Ship with a unique ID
    
      def __init__(self, hull, player, is_custom=false): 

  Make BuildShip and BuildDefaultShip private methods within Ship and
  __init__ can call either one of them as needed.
"""


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
        """Upon creation of an ECS object, the __init__function gets names
        for each participating Player and constructs their fleets."""
        print("Welcome to the Eclipse Combat Simulator!")
        self.parts = part_def.Part.GetPartsFromDB()
        self.hulls = hull_def.Hull.GetHullsFromDB()
        self.players = self.SetupPlayers()
        self.AssembleFleets()
        print("Finished with setup!")
        print("Here are the players participating in combat:")
        for player in self.players:
            print(player)
        self.sim_results = [0 for x in range(len(self.players))]
    
    def SetupPlayers(self, nplayers=2):
        """Gets names for each player participating in combat, creates & returns
        a list of Player objects representing them. Currently only works with 2
        players."""
        if nplayers < 2:
            raise RuntimeError("Number of players must be > 1!")
        players = []
        print("There are %i players participating in combat." % (nplayers))
        print("Player 1 is defending.")
        if nplayers == 2:
            print("Player 2 is attacking.")
        else:
            print("Players 2-%i are attacking and higher-numbered players \
                    arrived in the system later." % (nplayers))
        for i in range(nplayers):
            name = user_input.GetInput("Please enter player %i's name: "
                    % (i + 1), str)
            players += [player_def.Player(name)]
        return players
    
    def AssembleFleets(self):
        """Assembles a fleet for each Player. This involves determining the
        number of Ships of each Hull type controlled by the Player, building
        those Ships (i.e. determining which Parts are attached to them), and
        adding those Ships to the Player's fleet."""
        for player in self.players:
            print("Let's build %s's fleet." % (player.name))
            for hull_name in self.hulls.keys():
                if self.hulls[hull_name].is_mobile == 0 and player.id > 0:
                    # The Player with ID 0 is the defender; they are the only
                    # one who can have immobile Ships (e.g. the space station).
                    continue
                hull = self.hulls[hull_name]
                nships = user_input.GetInput(
                    "How many %ss does %s have (%i-%i)? "
                    % (hull.name, player.name, 0, hull.nmax),
                    int, True, 0, hull.nmax)
                if nships > 0:
                    print("Okay, let's build those %ss." % (hull.name))
                    new_ship = ship_def.Ship.BuildShip(hull, self.parts, player)
                    for i in range(nships):
                        # Can't just add nships * new_ship; they would all be
                        # the same Ship object. Fool me once, Python.
                        player.fleet.append(copy.deepcopy(new_ship))
            # Finished creating Ships for this Player, now sort their fleet
            player.SortFleet()
    
    def RunSimulations(self):
        """Runs a user-specified number of combat simulations between
        Players. Currently hardcoded for 2 players."""
        if len(self.players) != 2:
            raise RuntimeError(
                "The ECS currently only supports 2 combatants. Sorry!")
        nsims = user_input.GetInput(
            "How many combat sims should we run? ", int, True, 1, 1000000)
        sim_num = 0
        # Apply initiative bonus to the defending player.
        for ship in self.players[0].fleet:
            ship.initiative += 0.5
        print("Running simulation!")
        while sim_num < nsims:
            # Each iteration here is a full combat simulation.
            fleet1 = copy.deepcopy(self.players[0].fleet)
            fleet2 = copy.deepcopy(self.players[1].fleet)
            self.SimulateCombat(fleet1, fleet2, sim_num)
            sim_num += 1

    def SimulateCombat(self, fleet1, fleet2, sim_num):
        while len(fleet1) > 0 and len(fleet2) > 0:
            # Each iteration here represents a full round of combat.
            # Combat continues until one fleet has been completely destroyed.
            firing_seq = sorted(fleet1 + fleet2,
                key=lambda ship: -ship.initiative)
            while len(firing_seq) > 0 and len(fleet1) > 0 and len(fleet2) > 0:
                # During each iteration here a group of Ships with identical
                # initiative values fire and are then removed from the
                # firing_seq. Note: we can assume that they are all controlled
                # by the same Player due to how initiative works (defending
                # Player has fractional initiative & attacking Player does not).
                firing_now = [firing_seq.pop(0)]             
                while len(firing_seq) > 0 and \
                           firing_seq[0].initiative == firing_now[0].initiative:
                    firing_now.append(firing_seq.pop(0))
                # At this point, firing_now contains all Ships with the highest
                # intiative value that have not yet fired this round. Now they
                # attack simultaneously. 
                attacks = [ship.RollAttacks() for ship in firing_now
                           if ship.has_weapon]
                if firing_now[0].owner.id == fleet1[0].owner.id:
                    # The attacking ships belong to fleet1, so fire at fleet2
                    self.MakeAttacks(attacks, firing_seq, fleet2)
                else:
                    # The attacking ships belong to fleet2, so fire at fleet1
                    self.MakeAttacks(attacks, firing_seq, fleet1)
        if len(fleet1) < 1:
            print("Player 2 wins simulation %i!" % (sim_num + 1))
            self.sim_results[1] += 1
        else:
            print("Player 1 wins simulation %i!" % (sim_num + 1))
            self.sim_results[0] += 1
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
            print("Here are the simulation results:")
            for i in range(len(self.players)):
                print("%s won %i times (%.2f%% probability of victory)" \
                      % (self.players[i].name, self.sim_results[i], \
                      100. * self.sim_results[i] / nsims_completed))

def main():
    """Creates a new instance of ECS, runs the combat simulation, and
    reports the results."""
    sim = ECS()
    sim.RunSimulations()
    sim.ReportResults()
    print("Thank you for using the ECS!")
    
if __name__ == '__main__':
    main()