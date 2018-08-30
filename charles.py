import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import *
from sc2.unit import Unit
from sc2.position import Point2, Point3
import random
import configparser
import mysql.connector as sql
import atexit

config = configparser.ConfigParser()
config.read('general.cfg')

db_host = config.get('DATABASE', 'db_id')
db_user = config.get('DATABASE', 'db_user')
db_pw = config.get('DATABASE', 'db_password')
db_name = config.get('DATABASE', 'db_name')

# connection = sql.connect(host=db_host, user=db_user, password=db_pw, database=db_name)

aggression = random.randint(1,11)
greed = random.randint(1,11)
techs = random.randint(1,11)
vision = random.randint(1,11)
upgrades = random.randint(1,11)
enemy_race = ""
enemy_difficulty = "Harder"
outcome = 1

class charles(sc2.BotAI):
    def __init__(self):
        self.MAX_WORKERS = 90
        self.melee1_started = False
        self.melee2_started = False
        self.melee3_started = False
        self.armor1_started = False
        self.armor2_started = False
        self.armor3_started = False
        self.missle1_started = False
        self.missle2_started = False
        self.missle3_started = False
        self.melee_finished = False
        self.missle_finished = False
        self.armor_finished = False
        self.expanding = False
        self.building_army = False
        self.upgrading = False
        self.teching = False
        self.training_ultras = False
        self.training_hydras = False
        self.training_lings = False
        self.training_roaches = False
        self.training_count = 0
        self.building_spawningpool = False
        self.building_roachwarren = False
        self.building_hydraliskden = False
        self.building_ultraliskcavern = False
        self.building_infestationpit = False
        self.building_lair = False
        self.building_hive = False
        self.upgrading_melee = False
        self.upgrading_missle = False
        self.upgrading_armor = False
        self.upgrading_ulta_armor = False
        self.upgrading_hydra_range = False
        self.upgrading_hydra_speed = False
        self.upgrading_ling_attackspeed = False
        self.pthreat = {PROBE: 1, ZEALOT: 2, STALKER: 2, ADEPT: 2, ORACLE: 2, IMMORTAL: 4, VOIDRAY: 3, CARRIER: 8, MOTHERSHIP: 8, DARKTEMPLAR: 3, COLOSSUS: 7, ARCHON: 6, HIGHTEMPLAR: 4, TEMPEST: 7}
        self.zthreat = {}
        self.tthreat = {}
        self.fthreat = {ZERGLING: .5, ROACH: 2, HYDRALISK: 2.5, ULTRALISK: 6}
        self.enemy_threat = 0
        self.my_threat = 0

        # when charles is first ran, if we're not on the ladder, store some values into a db.

    async def on_start(self):
        await self.chat_send(str(self.game_info.players[0].race))
        await self.chat_send(str(self.game_info.players[1].race))
        if str(self.game_info.players[0].race) == str(Race.Zerg) and str(self.game_info.players[1].race) == str(Race.Zerg):
            enemy_race = "Zerg"

        if self.game_info.players[0].race == Race.Zerg and self.game_info.players[1].race == Race.Protoss:
            enemy_race = "Protoss"

        if self.game_info.players[0].race == Race.Zerg and self.game_info.players[1].race == Race.Terran:
            enemy_race = "Terran"

        if self.game_info.players[0].race == Race.Terran and self.game_info.players[1].race == Race.Zerg:
            enemy_race = "Terran"

        if self.game_info.players[0].race == Race.Protoss and self.game_info.players[1].race == Race.Zerg:
            enemy_race = "Protoss"

        if self.game_info.players[0].race == Race.Random or self.game_info.players[1].race == Race.Random:
            enemy_race = "Random"

    async def on_step(self, iteration):
        self.combinedActions = []
        # To do: find some way to set parameters like aggression level, scouting level? Technology level? upgrade level
        # as well as which upgrades we have? Melee 1, 2, 3, armor 1,2,3 ultra carapcace, hydra range, hydra speed, ling
        # ling as, we also could assign a random threat level to enemy units.
        # when we start a match(Or finish?)s, store the values of these levels, as well as the match result, the enemy race
        # and ??difficulty??
        # build some scouting lings and work on overlord scouting

        if iteration % 10 == 0:
            await self.get_threats()

            await self.chat_send("ENEMY: " + str(self.enemy_threat) + " SELF: " + str(self.my_threat))

            if self.minerals > 800 and (self.units(SPAWNINGPOOL).ready.exists or self.units(HYDRALISKDEN) or self.units(ROACHWARREN) or self.units(ULTRALISKCAVERN)):
                self.building_army = await self.build_army()

            # change this from random choice to something a bit more scripted.
            # maybe get a pickAction method that checks threat levels on map, trys to determine what units the enemy is
            # gonna make, what units to produce and therefor what upgrades to get. (This will be hard)
            # to determine threat level, I think we're gonna get/set a random value of threat for each enemy unit on
            # start, and then with enough games we can determine what threat levels win the most, and set those manually
            # We have to also, then, have a friendly threat level so we can determine what units to build to counter.
            # how the fuck do we even do this?
            if not self.expanding and not self.building_army and not self.teching and not self.upgrading:
                if self.my_threat > self.enemy_threat*1.5 or (self.my_threat == 0 and self.enemy_threat == 0):
                    choice = random.randint(1, 4)
                    if choice == 1:
                        self.expanding = await self.build_expand()
                    if choice == 2:
                        self.teching = await self.tech_up()
                    if choice == 3:
                        self.upgrading = await self.get_upgrades()
                else:
                    self.building_army = await self.build_army()

            else:
                # we're already doing something, so just keep doing that thing.
                if self.expanding:
                    self.expanding = await self.build_expand()

                if self.building_army:
                    self.building_army = await self.build_army()

                if self.teching:
                    self.teching = await self.tech_up()

                if self.upgrading:
                    self.upgrading = await self.get_upgrades()

            await self.doSomeMicro()
            await self.build_extractor()
            # await self.attac(iteration)
            await self.inject_larva()
            await self.build_overlord()

            await self.distribute_workers()

            self.num_of_bases = self.units(HIVE).ready.amount
            self.num_of_bases += self.units(LAIR).ready.amount
            self.num_of_bases += self.units(HATCHERY).ready.amount

            await self.build_queens()

            if self.units(DRONE).amount < 18 * self.num_of_bases and self.units(DRONE).amount < self.MAX_WORKERS:
                await self.build_workers()

    async def tech_up(self):
        hq = self.townhalls.first

        ultra_cavern = self.units(ULTRALISKCAVERN).exists
        roach_warren = self.units(ROACHWARREN).exists
        a_hive = self.units(HIVE).exists
        infest_pit = self.units(INFESTATIONPIT).exists
        hydra_den = self.units(HYDRALISKDEN).exists
        a_lair = self.units(LAIR).ready.exists
        spawning_pool = self.units(SPAWNINGPOOL).exists

        # check if we're done teching...
        if ultra_cavern and a_hive and infest_pit and hydra_den and spawning_pool:
            # self.upgrading = True
            await self.chat_send("We're actually done teching so I guess we'll build army.")
            self.building_army = True
            return False

        # if we're not currently doing something
        if not self.building_spawningpool and not self.building_lair and not self.building_hydraliskden and not self.building_infestationpit and not self.building_hive and not self.building_ultraliskcavern and not self.building_roachwarren:
            choice = random.randint(1, 8)

            if choice == 1 and self.units(HIVE).ready.exists:
                if not self.units(ULTRALISKCAVERN).ready.exists and not self.already_pending(ULTRALISKCAVERN):
                    self.building_ultraliskcavern = True
                    await self.chat_send("I'm building an ultra cavern!")
                else:
                    self.building_ultraliskcavern = False
                    self.building_army = True
                    return False
            elif not self.units(HIVE).ready.exists:
                choice = 2

            if choice == 2 and self.units(INFESTATIONPIT).ready.exists and not self.units(HIVE).ready.exists and not self.already_pending(HIVE) and self.units(LAIR).ready.exists:
                self.building_hive = True
                await self.chat_send("I'm building a hive")
            else:
                choice = 3

            if choice == 3 and self.units(LAIR).ready.exists and not self.units(INFESTATIONPIT).ready.exists and not self.already_pending(INFESTATIONPIT):
                self.building_infestationpit = True
                await self.chat_send("I'm building an infestation pit")

            else:
                choice = 4

            if choice == 4 and self.units(LAIR).ready.exists and not self.units(HYDRALISKDEN).ready.exists and not self.already_pending(HYDRALISKDEN):
                await self.chat_send("I'm building a hydra den")
                self.building_hydraliskden = True
            else:
                choice = 5

            if choice == 5 and self.units(SPAWNINGPOOL).ready.exists and not self.units(HIVE) and not self.units(LAIR).ready.exists and not self.already_pending(LAIR):
                await self.chat_send("I'm building a LAIR")
                self.building_lair = True
            else:
                choice = 6

            if choice == 6 and self.units(SPAWNINGPOOL).ready.exists and not self.units(ROACHWARREN).ready.exists and not self.already_pending(ROACHWARREN):
                await self.chat_send("I'm building a roach warren")
                self.building_roachwarren = True
            else:
                choice = 7

            if choice == 7 and not self.units(SPAWNINGPOOL).ready.exists and not self.already_pending(SPAWNINGPOOL):
                await self.chat_send("I'm building a spawning pool")
                self.building_spawningpool = True

        # build a building
        if self.building_ultraliskcavern:
            if self.can_afford(ULTRALISKCAVERN):
                await self.build(ULTRALISKCAVERN, near=hq)
                self.building_ultraliskcavern = False
                return False
            else:
                return True

        # build a building
        if self.building_hive:
            if self.can_afford(HIVE):
                lair = self.units(LAIR).ready
                await self.do(lair.first.build(HIVE))
                self.building_hive = False
                return False
            else:
                return True

        # build a building
        if self.building_infestationpit:
            if self.can_afford(INFESTATIONPIT):
                await self.build(INFESTATIONPIT, near=hq)
                self.building_infestationpit = False
                return False
            else:
                return True

        # build a building
        if self.building_hydraliskden:
            if self.can_afford(HYDRALISKDEN):
                await self.build(HYDRALISKDEN, near=hq)
                self.building_hydraliskden = False
                return False
            else:
                return True

        # build a building
        if self.building_lair:
            if self.can_afford(LAIR):
                hatch = self.townhalls.first
                await self.do(hatch.build(LAIR))
                self.building_lair = False
                return False
            else:
                return True

        # build a building
        if self.building_roachwarren:
            if self.can_afford(ROACHWARREN):
                await self.build(ROACHWARREN, near=hq)
                self.building_roachwarren = False
                return False
            else:
                return True

        # build a building
        if self.building_spawningpool:
            if self.can_afford(SPAWNINGPOOL):
                await self.build(SPAWNINGPOOL, near=hq)
                self.building_spawningpool = False
                return False
            else:
                return True

    async def build_army(self):
        larvae = self.units(LARVA)
        # if any of the training flags are true, build. Otherwise, if they're not, get choice. and set the flags.
        if not self.training_hydras and not self.training_lings and not self.training_ultras and not self.training_roaches:
            choice = random.randint(1, 5)

            # instead of a random choice we need to get unit specific threat and then figure out the correct composition
            # those units based on some kind of mixed unit dictionary

            if choice == 1 and self.units(ULTRALISKCAVERN).ready.exists:
                self.training_ultras = True
                await self.chat_send("I'm training an ultra")
            else:
                choice = 2

            if choice == 2 and self.units(HYDRALISKDEN).ready.exists:
                self.training_hydras = True
                await self.chat_send("I'm training 3 hydras")
            else:
                choice = 3

            if choice == 3 and self.units(ROACHWARREN).ready.exists:
                await self.chat_send("I'm training some roaches")
                self.training_roaches = True
            else:
                choice = 4

            if choice == 4 and self.units(SPAWNINGPOOL).ready.exists:
                await self.chat_send("I'm training 8 zerglings")
                self.training_lings = True

        # build some units.
        if self.training_ultras:
            if self.can_afford(ULTRALISK) and larvae.exists:
                await self.do(larvae.random.train(ULTRALISK))
                self.training_ultras = False
                return False
            else:
                return True

        if self.training_hydras:
            if self.can_afford(HYDRALISK) and larvae.exists:
                await self.do(larvae.random.train(HYDRALISK))
                self.training_count += 1
                if self.training_count > 2:
                    self.training_hydras = False
                    self.training_count = 0
                    return False
                else:
                    return True
            else:
                return True

        if self.training_lings:
            if self.can_afford(ZERGLING) and larvae.exists:
                await self.do(larvae.random.train(ZERGLING))
                self.training_count += 1
                if self.training_count > 3:
                    self.training_lings = False
                    return False
                else:
                    return True
            else:
                return True

        if self.training_roaches:
            if self.can_afford(ROACH) and larvae.exists:
                await self.do(larvae.random.train(ROACH))
                self.training_count += 1
                if self.training_count > 2:
                    self.training_roaches = False
                    return False
                else:
                    return True
            else:
                return True

    async def build_expand(self):
        if self.townhalls.amount < 5:
            if self.can_afford(HATCHERY) and not self.already_pending(HATCHERY):
                location = await self.get_next_expansion()
                await self.build(HATCHERY, near=location)
                await self.chat_send("I'm expanding!")
                return False
            else:
                return True
        else:
            # if we have a bunch of expansions already, just build more army units.
            await self.chat_send("I wanted to expand, but I guess I'll build an army instead.")
            self.building_army = True
            return False

    async def doSomeMicro(self):
        melee = self.units(ZERGLING) | self.units(ULTRALISK)
        ranged = self.units(HYDRALISK)
        roaches = self.units(ROACH)

        all_units = melee | ranged | roaches

        # if our threat level isn't high enough to win a fight we need to gtfo and not fight until we can actually win
        if self.my_threat < self.enemy_threat:
            for u in all_units:
                retreatPoints = self.neighbors8(u.position, distance=2) | self.neighbors8(u.position, distance=4)
                # filter points that are pathable
                retreatPoints = {x for x in retreatPoints if self.inPathingGrid(x)}
                if retreatPoints:
                    retreatPoint = self.townhalls.first.position
                    self.combinedActions.append(u.move(retreatPoint))
                    continue

            await self.do_actions(self.combinedActions)
            return

        # move roaches to their own category
        for r in ranged:
            # move to range 15 of closest unit if reaper is below 20 hp and not regenerating
            enemyThreatsClose = self.known_enemy_units.filter(lambda x: x.can_attack_ground).closer_than(15, r) # threats that can attack the reaper
            if r.health_percentage < 2/5 and enemyThreatsClose.exists:
                retreatPoints = self.neighbors8(r.position, distance=2) | self.neighbors8(r.position, distance=4)
                # filter points that are pathable
                retreatPoints = {x for x in retreatPoints if self.inPathingGrid(x)}
                if retreatPoints:
                    closestEnemy = enemyThreatsClose.closest_to(r)
                    retreatPoint = closestEnemy.position.furthest(retreatPoints)
                    self.combinedActions.append(r.move(retreatPoint))
                    continue # continue for loop, dont execute any of the following

            # reaper is ready to attack, shoot nearest unit
            enemyUnits = self.known_enemy_units.closer_than(4, r) # hardcoded attackrange of 5
            if r.weapon_cooldown == 0 and enemyUnits.exists:
                enemyUnits = enemyUnits.sorted(lambda x: x.distance_to(r))
                closestEnemy = enemyUnits[0]
                self.combinedActions.append(r.attack(closestEnemy))
                continue # continue for loop, dont execute any of the following

            # move towards to max unit range if enemy is closer than 4
            enemyThreatsVeryClose = self.known_enemy_units.filter(lambda x: x.can_attack_ground).closer_than(3.5, r) # hardcoded attackrange minus 0.5
            # threats that can attack the reaper
            if r.weapon_cooldown != 0 and enemyThreatsVeryClose.exists:
                retreatPoints = self.neighbors8(r.position, distance=2) | self.neighbors8(r.position, distance=4)
                # filter points that are pathable by a reaper
                retreatPoints = {x for x in retreatPoints if self.inPathingGrid(x)}
                if retreatPoints:
                    closestEnemy = enemyThreatsVeryClose.closest_to(r)
                    retreatPoint = max(retreatPoints, key=lambda x: x.distance_to(closestEnemy) - x.distance_to(r))
                    # retreatPoint = closestEnemy.position.furthest(retreatPoints)
                    self.combinedActions.append(r.move(retreatPoint))
                    continue # continue for loop, don't execute any of the following

            # move to nearest enemy ground unit/building because no enemy unit is closer than 5
            allEnemyUnits = self.known_enemy_units
            if allEnemyUnits.exists:
                closestEnemy = allEnemyUnits.closest_to(r)
                self.combinedActions.append(r.move(closestEnemy))
                continue # continue for loop, don't execute any of the following

            # move to random enemy start location if no enemy buildings have been seen
            self.combinedActions.append(r.move(random.choice(self.enemy_start_locations)))


        for m in melee:
            # move to range 15 of closest unit if reaper is below 20 hp and not regenerating
            enemyThreatsClose = self.known_enemy_units.filter(lambda x: x.can_attack_ground).closer_than(15, m) # threats that can attack the reaper
            if m.health_percentage < 2/5 and enemyThreatsClose.exists:
                retreatPoints = self.neighbors8(m.position, distance=2) | self.neighbors8(m.position, distance=4)
                # filter points that are pathable
                retreatPoints = {x for x in retreatPoints if self.inPathingGrid(x)}
                if retreatPoints:
                    closestEnemy = enemyThreatsClose.closest_to(m)
                    retreatPoint = closestEnemy.position.furthest(retreatPoints)
                    self.combinedActions.append(m.move(retreatPoint))
                    continue # continue for loop, dont execute any of the following

            # reaper is ready to attack, shoot nearest unit
            enemyGroundUnits = self.known_enemy_units.not_flying.closer_than(.5, m) # hardcoded attackrange of 5
            if m.weapon_cooldown == 0 and enemyGroundUnits.exists:
                enemyGroundUnits = enemyGroundUnits.sorted(lambda x: x.distance_to(m))
                closestEnemy = enemyGroundUnits[0]
                self.combinedActions.append(m.attack(closestEnemy))
                continue # continue for loop, dont execute any of the following

            # move to nearest enemy ground unit/building because no enemy unit is closer than 5
            allEnemyUnits = self.known_enemy_units.not_flying
            if allEnemyUnits.exists:
                closestEnemy = allEnemyUnits.closest_to(m)
                self.combinedActions.append(m.move(closestEnemy))
                continue # continue for loop, don't execute any of the following

            # move to random enemy start location if no enemy buildings have been seen
            self.combinedActions.append(m.move(random.choice(self.enemy_start_locations)))

        for r in roaches:
            # move to range 15 of closest unit if reaper is below 20 hp and not regenerating
            enemyThreatsClose = self.known_enemy_units.filter(lambda x: x.can_attack_ground).closer_than(15, r) # threats that can attack the reaper
            if r.health_percentage < 2/5 and enemyThreatsClose.exists:
                retreatPoints = self.neighbors8(r.position, distance=2) | self.neighbors8(r.position, distance=4)
                # filter points that are pathable
                retreatPoints = {x for x in retreatPoints if self.inPathingGrid(x)}
                if retreatPoints:
                    closestEnemy = enemyThreatsClose.closest_to(r)
                    retreatPoint = closestEnemy.position.furthest(retreatPoints)
                    self.combinedActions.append(r.move(retreatPoint))
                    continue # continue for loop, dont execute any of the following

            # reaper is ready to attack, shoot nearest unit
            enemyUnits = self.known_enemy_units.closer_than(4, r) # hardcoded attackrange of 5
            if r.weapon_cooldown == 0 and enemyUnits.exists:
                enemyUnits = enemyUnits.sorted(lambda x: x.distance_to(r))
                closestEnemy = enemyUnits[0]
                self.combinedActions.append(r.attack(closestEnemy))
                continue # continue for loop, dont execute any of the following

            # move towards to max unit range if enemy is closer than 4
            enemyThreatsVeryClose = self.known_enemy_units.filter(lambda x: x.can_attack_ground).closer_than(3.5, r) # hardcoded attackrange minus 0.5
            # threats that can attack the reaper
            if r.weapon_cooldown != 0 and enemyThreatsVeryClose.exists:
                retreatPoints = self.neighbors8(r.position, distance=2) | self.neighbors8(r.position, distance=4)
                # filter points that are pathable by a reaper
                retreatPoints = {x for x in retreatPoints if self.inPathingGrid(x)}
                if retreatPoints:
                    closestEnemy = enemyThreatsVeryClose.closest_to(r)
                    retreatPoint = max(retreatPoints, key=lambda x: x.distance_to(closestEnemy) - x.distance_to(r))
                    # retreatPoint = closestEnemy.position.furthest(retreatPoints)
                    self.combinedActions.append(r.move(retreatPoint))
                    continue # continue for loop, don't execute any of the following

            # move to nearest enemy ground unit/building because no enemy unit is closer than 5
            allEnemyUnits = self.known_enemy_units
            if allEnemyUnits.exists:
                closestEnemy = allEnemyUnits.closest_to(r)
                self.combinedActions.append(r.move(closestEnemy))
                continue # continue for loop, don't execute any of the following

        # move to random enemy start location if no enemy buildings have been seen
            self.combinedActions.append(r.move(random.choice(self.enemy_start_locations)))


        await self.do_actions(self.combinedActions)

    async def get_upgrades(self):
        evo = self.units(EVOLUTIONCHAMBER).ready.exists

        hydra_den = self.units(HYDRALISKDEN).ready.exists
        ultra_den = self.units(ULTRALISKCAVERN).ready.exists
        spawning_pool = self.units(SPAWNINGPOOL).ready.exists
        hive = self.units(HIVE).ready.exists

        # all upgrades are finished.
        if self.melee_finished and self.missle_finished and self.armor_finished and self.upgrading_hydra_range:
            if self.upgrading_hydra_speed and self.upgrading_ulta_armor and self.upgrading_ling_attackspeed:
                self.building_army = True
                return False

        # do a random upgrade:
        # in the future, pick the upgrade that helps the most units.
        # or an armor upgrade already_pending_upgrade exists
        choice = random.randint(1, 8)
        if choice == 1 or choice == 2 or choice == 3:
            if not self.units(EVOLUTIONCHAMBER).ready.exists and not self.already_pending(EVOLUTIONCHAMBER):
                await self.build_evo()

        if choice == 1 and not self.melee3_started and evo:
            self.upgrading_melee = True

        if choice == 2 and not self.missle3_started and evo:
            self.upgrading_missle = True

        if choice == 3 and not self.armor3_started and evo:
            self.upgrading_armor = True

        if choice == 4 and hydra_den:
            self.upgrading_hydra_range = True

        if choice == 5 and hydra_den:
            self.upgrading_hydra_speed = True

        if choice == 6 and ultra_den:
            self.upgrading_ulta_armor = True

        if choice == 7 and spawning_pool and hive:
            self.upgrading_ling_attackspeed = True

        if self.upgrading_melee:
            # all melee upgrades are done, we need to
            if self.melee1_started and self.melee2_started and self.melee3_started:
               self.upgrading_melee = False
               self.melee_finished = True
               return True

            # melee 1
            if not self.melee3_started and not self.melee2_started and not self.melee1_started:
                ec = self.units(EVOLUTIONCHAMBER).ready.first
                if self.can_afford(AbilityId.RESEARCH_ZERGMELEEWEAPONSLEVEL1):
                    await self.do(ec(AbilityId.RESEARCH_ZERGMELEEWEAPONSLEVEL1))
                    self.melee1_started = True
                    return False
                else:
                    return True

            # melee 2
            if self.melee1_started and not self.melee2_started and not self.melee3_started:
                ec = self.units(EVOLUTIONCHAMBER).ready.first
                if self.can_afford(AbilityId.RESEARCH_ZERGMELEEWEAPONSLEVEL2):
                    await self.do(ec(AbilityId.RESEARCH_ZERGMELEEWEAPONSLEVEL2))
                    self.melee2_started = True
                    return False
                else:
                    return True

            # melee 3
            if self.melee1_started and self.melee2_started and not self.melee3_started:
                ec = self.units(EVOLUTIONCHAMBER).ready.first
                if self.can_afford(AbilityId.RESEARCH_ZERGMELEEWEAPONSLEVEL3):
                    await self.do(ec(AbilityId.RESEARCH_ZERGMELEEWEAPONSLEVEL3))
                    self.melee3_started = True
                    return False
                else:
                    return True

        if self.upgrading_missle:
            # all melee upgrades are done, we need to
            if self.missle1_started and self.missle2_started and self.missle3_started:
                self.upgrading_missle = False
                self.missle_finished = True
                return True

            # missle 1
            if not self.missle3_started and not self.missle2_started and not self.missle1_started:
                ec = self.units(EVOLUTIONCHAMBER).ready.first
                if self.can_afford(AbilityId.RESEARCH_ZERGMISSILEWEAPONSLEVEL1):
                    await self.do(ec(AbilityId.RESEARCH_ZERGMISSILEWEAPONSLEVEL1))
                    self.missle1_started = True
                    return False
                else:
                    return True

            # missle 2
            if self.missle1_started and not self.missle2_started and not self.missle3_started:
                ec = self.units(EVOLUTIONCHAMBER).ready.first
                if self.can_afford(AbilityId.RESEARCH_ZERGMISSILEWEAPONSLEVEL2):
                    await self.do(ec(AbilityId.RESEARCH_ZERGMISSILEWEAPONSLEVEL2))
                    self.missle2_started = True
                    return False
                else:
                    return True

        if self.upgrading_armor:
            # all melee upgrades are done, we need to
            if self.armor1_started and self.armor2_started and self.armor3_started:
                self.upgrading_armor = False
                self.armor_finished = True
                return True

            # armor 1
            if not self.armor3_started and not self.armor2_started and not self.armor1_started:
                ec = self.units(EVOLUTIONCHAMBER).ready.first
                if self.can_afford(AbilityId.RESEARCH_ZERGGROUNDARMORWEAPONSLEVEL1):
                    await self.do(ec(AbilityId.RESEARCH_ZERGGROUNDARMORWEAPONSLEVEL1))
                    self.armor1_started = True
                    return False
                else:
                    return True

            # armor 2
            if self.armor1_started and not self.armor2_started and not self.armor3_started:
                ec = self.units(EVOLUTIONCHAMBER).ready.first
                if self.can_afford(AbilityId.RESEARCH_ZERGGROUNDARMORLEVEL2):
                    await self.do(ec(AbilityId.RESEARCH_ZERGGROUNDARMORWEAPONSLEVEL2))
                    self.armor2_started = True
                    return False
                else:
                    return True

            # armor 3
            if self.armor1_started and self.armor2_started and not self.armor3_started:
                ec = self.units(EVOLUTIONCHAMBER).ready.first
                if self.can_afford(AbilityId.RESEARCH_ZERGGROUNDARMORWEAPONSLEVEL3):
                    await self.do(ec(AbilityId.RESEARCH_ZERGGROUNDARMORWEAPONSLEVEL3))
                    self.armor3_started = True
                    return False
                else:
                    return True
            # armor 3
            if self.armor1_started and self.armor2_started and not self.armor3_started:
                ec = self.units(EVOLUTIONCHAMBER).ready.first
                if self.can_afford(AbilityId.RESEARCH_ZERGGROUNDARMORWEAPONSLEVEL3):
                    await self.do(ec(AbilityId.RESEARCH_ZERGGROUNDARMORWEAPONSLEVEL3))
                    self.armor3_started = True
                    return False
                else:
                    return True

        if self.upgrading_ling_attackspeed:
            spawning_pool = self.units(SPAWNINGPOOL).ready.first
            if self.can_afford(AbilityId.RESEARCH_ZERGLINGADRENALGLANDS):
                await self.do(spawning_pool.train(AbilityId.RESEARCH_ZERGLINGADRENALGLANDS))
                self.upgrading_ling_attackspeed = False
                return False
            else:
                return True


        if self.upgrading_hydra_range:
            if self.can_afford(AbilityId.RESEARCH_GROOVEDSPINES):
                hydra_den = self.units(HYDRALISKDEN).ready.first
                await self.do(hydra_den.train(AbilityId.RESEARCH_GROOVEDSPINES))
                self.upgrading_hydra_range = False
                return False
            else:
                return True

        if self.upgrading_hydra_speed:
            if self.can_afford(AbilityId.RESEARCH_MUSCULARAUGMENTS):
                hydra_den = self.units(HYDRALISKDEN).ready.first
                await self.do(hydra_den.train(AbilityId.RESEARCH_MUSCULARAUGMENTS))
                self.upgrading_hydra_speed = False
                return False
            else:
                return True

        if self.upgrading_ulta_armor:
            if self.can_afford(AbilityId.RESEARCH_CHITINOUSPLATING):
                ultra_den = self.units(ULTRALISKCAVERN).ready.first
                await self.do(ultra_den.train(AbilityId.RESEARCH_CHITINOUSPLATING))
                self.upgrading_ultra_armor = False
                return False
            else:
                return True

    async def build_evo(self):
        hq = self.townhalls.first
        if self.townhalls.ready.amount > 1 and self.can_afford(EVOLUTIONCHAMBER):
            if not self.units(EVOLUTIONCHAMBER).ready.exists and not self.already_pending(EVOLUTIONCHAMBER):
                await self.build(EVOLUTIONCHAMBER, near=hq)


    async def build_extractor(self):
        for th in self.townhalls.ready:
            vgs = self.state.vespene_geyser.closer_than(20.0, th)
            for vg in vgs:
                if not self.can_afford(EXTRACTOR):
                    break

                worker = self.select_build_worker(vg.position)
                if worker is None:
                    break

                if not self.units(EXTRACTOR).closer_than(1.0, vg).exists:
                    await self.do(worker.build(EXTRACTOR, vg))

    async def build_queens(self):
        hqs = self.townhalls.ready
        for hq in hqs:
            if self.units(SPAWNINGPOOL).ready.exists and self.units(QUEEN).amount <= self.townhalls.amount:
                if not self.already_pending(QUEEN):
                    if self.can_afford(QUEEN):
                        if hq.noqueue:
                            await self.do(hq.train(QUEEN))

    async def inject_larva(self):
        hq = self.townhalls.ready.random
        if hq:
            for queen in self.units(QUEEN).idle:
                abilities = await self.get_available_abilities(queen)
                if AbilityId.EFFECT_INJECTLARVA in abilities:
                    await self.do(queen(AbilityId.EFFECT_INJECTLARVA, hq))

    async def build_workers(self):
        hq = self.townhalls.first
        larvae = self.units(LARVA)
        if hq.assigned_harvesters < hq.ideal_harvesters:
            if self.can_afford(DRONE) and larvae.exists:
                larva = larvae.random
                await self.do(larva.train(DRONE))
                return

    async def build_overlord(self):
        larvae = self.units(LARVA)
        if self.supply_left < 2 or (self.supply_left < 4 and self.supply_cap > 28 ):
            if self.can_afford(OVERLORD) and not self.already_pending(OVERLORD) and larvae.exists:
                await self.do(larvae.random.train(OVERLORD))

    def select_target(self):
        if self.known_enemy_units.exists:
            return random.choice(self.known_enemy_units).position
        elif self.known_enemy_structures.exists:
            return random.choice(self.known_enemy_structures).position
        else:
            return self.enemy_start_locations[0]

    def inPathingGrid(self, pos):
        # returns True if it is possible for a ground unit to move to pos - doesnt seem to work on ramps or near edges
        assert isinstance(pos, (Point2, Point3, Unit))
        pos = pos.position.to2.rounded
        return self._game_info.pathing_grid[(pos)] != 0

    # stolen and modified from position.py
    def neighbors4(self, position, distance=1):
        p = position
        d = distance
        return {
            Point2((p.x - d, p.y)),
            Point2((p.x + d, p.y)),
            Point2((p.x, p.y - d)),
            Point2((p.x, p.y + d)),
        }

    # stolen and modified from position.py
    def neighbors8(self, position, distance=1):
        p = position
        d = distance
        return self.neighbors4(position, distance) | {
            Point2((p.x - d, p.y - d)),
            Point2((p.x - d, p.y + d)),
            Point2((p.x + d, p.y - d)),
            Point2((p.x + d, p.y + d)),
        }

    async def do_actions(self, actions):
        for action in actions:
            cost = self._game_data.calculate_ability_cost(action.ability)
            self.minerals -= cost.minerals
            self.vespene -= cost.vespene

        r = await self._client.actions(actions, game_data=self._game_data)
        return r

    async def get_threats(self):
        self.enemy_threat = 0
        self.my_threat = 0

        # Calulate their threat level.
        for u in self.known_enemy_units:
            if u.name == "Zealot":
                self.enemy_threat += self.pthreat[ZEALOT]

            if u.name == "Stalker":
                self.enemy_threat += self.pthreat[STALKER]

            if u.name == "Adept":
                self.enemy_threat += self.pthreat[ADEPT]

            if u.name == "Oracle":
                self.enemy_threat += self.pthreat[ORACLE]

            if u.name == "Immortal":
                self.enemy_threat += self.pthreat[IMMORTAL]

            if u.name == "Voidray":
                self.enemy_threat += self.pthreat[VOIDRAY]

            if u.name == "Carrier":
                self.enemy_threat += self.pthreat[CARRIER]

            if u.name == "Mothership":
                self.enemy_threat += self.pthreat[MOTHERSHIP]

            if u.name == "Darktemplar":
                self.enemy_threat += self.pthreat[DARKTEMPLAR]

            if u.name == "Hightemplar":
                self.enemy_threat += self.pthreat[HIGHTEMPLAR]

            if u.name == "Archon":
                self.enemy_threat += self.pthreat[ARCHON]

            if u.name == "Colossus":
                self.enemy_threat += self.pthreat[COLOSSUS]

            if u.name == "Tempest":
                self.enemy_threat += self.pthreat[TEMPEST]

        #calculate my threat level
        my_units =  self.units(ZERGLING) | self.units(ULTRALISK) | self.units(HYDRALISK) | self.units(ROACH)

        for u in my_units:
            if u.name == "Zergling":
                self.my_threat += self.fthreat[ZERGLING]

            if u.name == "Roach":
                self.my_threat += self.fthreat[ROACH]

            if u.name == "Hydralisk":
                self.my_threat += self.fthreat[HYDRALISK]

            if u.name == "Ultralisk":
                self.my_threat += self.fthreat[ULTRALISK]

            if self.my_threat <= self.enemy_threat:
                if self.units(SPAWNINGPOOL).ready.exists:
                    self.building_army = await self.build_army()

@atexit.register
def cleanup():
    # cursor = connection.cursor()
    return

    #table = "INSERT INTO charles (agression, outcome, greed, techs, vision, upgrades, enemy_race, enemy_difficulty) VALUES ({}, {}, {}, {}, {}, {}, '{}', '{}');".format(aggression, outcome, greed, techs, vision, upgrades, enemy_race, enemy_difficulty)
    #cursor.execute(table)
    #connection.commit()

    # add line to db

def main():
    run_game(maps.get("AcidplantLE"), [
        Bot(Race.Zerg, charles()),
        Computer(Race.Protoss, Difficulty.Hard)
    ], realtime=False)

if __name__ == '__main__':
    main()
