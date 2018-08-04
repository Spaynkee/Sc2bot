import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import *
import random

class charles(sc2.BotAI):
    def __init__(self):
        self.MAX_WORKERS = 70
        self.attack1_started = False
        self.attack2_started = False
        self.attack3_started = False
        self.ground1_started = False
        self.ground2_started = False
        self.ground3_started = False
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

    async def on_step(self, iteration):
        # we need to do things like distribute workers, build workers, build queens, build vespense every step
        # Every so often, we should do randomly, Build army, expand, tech up, upgrade.

        if iteration % 25 == 0:
            if not self.expanding and not self.building_army and not self.teching and not self.upgrading:
                choice = random.randint(1, 5)
                if choice == 1:
                    self.expanding = await self.build_expand()

                if choice == 2:
                    self.building_army = await self.build_army()

                if choice == 3:
                    self.teching = await self.tech_up()

                if choice == 4:
                    self.teching = True
                    #self.upgrading = await self.get_upgrades()
                    await self.chat_send("I'm upgrading! but really im teching for now.")
            else:
                # we're already doing something, so just keep doing that thing.

                if self.expanding:
                    self.expanding = await self.build_expand()

                if self.building_army:
                    self.building_army = await self.build_army()

                if self.teching:
                    self.teching = await self.tech_up()

                if self.upgrading:
                    #self.upgrading = await self.get_upgrades()
                    await self.chat_send("I'm upgrading!  ")

        if iteration % 10 == 0:

            await self.gather_army()
            await self.build_extractor()
            await self.attac(iteration)
            await self.inject_larva()
            await self.build_overlord()

            await self.distribute_workers()

            self.num_of_bases = self.units(UnitTypeId.HIVE).ready.amount
            self.num_of_bases += self.units(UnitTypeId.LAIR).ready.amount
            self.num_of_bases += self.units(UnitTypeId.HATCHERY).ready.amount

            if self.units(UnitTypeId.DRONE).amount < 18 * self.num_of_bases and self.units(UnitTypeId.DRONE).amount < self.MAX_WORKERS:
                await self.build_workers()

            await self.build_queens()

    async def tech_up(self):
        hq = self.townhalls.first

        ultra_cavern = self.units(UnitTypeId.ULTRALISKCAVERN).exists
        roach_warren = self.units(UnitTypeId.ROACHWARREN).exists
        a_hive = self.units(UnitTypeId.HIVE).exists
        infest_pit = self.units(UnitTypeId.INFESTATIONPIT).exists
        hydra_den = self.units(UnitTypeId.HYDRALISKDEN).exists
        a_lair = self.units(UnitTypeId.LAIR).exists
        spawning_pool = self.units(UnitTypeId.SPAWNINGPOOL).exists

        # check if we're done teching...
        if ultra_cavern and a_hive and infest_pit and hydra_den and a_lair and spawning_pool:
            # self.upgrading = True
            await self.chat_send("We're actually done teching so I guess we'll do upgrades")
            return False

        # if we're not currently doing something
        if not self.building_spawningpool and not self.building_lair and not self.building_hydraliskden and not self.building_infestationpit and not self.building_hive and not self.building_ultraliskcavern and not self.building_roachwarren:
            choice = random.randint(1, 8)

            if choice == 1 and self.units(UnitTypeId.HIVE).ready.exists:
                if not self.units(UnitTypeId.ULTRALISKCAVERN).ready.exists and not self.already_pending(UnitTypeId.ULTRALISKCAVERN):
                    self.building_ultraliskcavern = True
                    await self.chat_send("I'm building an ultra cavern!")
                else:
                    self.building_ultraliskcavern = False
                    self.building_army = True
                    return False
            elif not self.units(UnitTypeId.HIVE).ready.exists:
                choice = 2

            if choice == 2 and self.units(UnitTypeId.INFESTATIONPIT).ready.exists and not self.units(UnitTypeId.HIVE).ready.exists and not self.already_pending(UnitTypeId.HIVE):
                self.building_hive = True
                await self.chat_send("I'm building a hive")
            else:
                choice = 3

            if choice == 3 and self.units(UnitTypeId.LAIR).ready.exists and not self.units(UnitTypeId.INFESTATIONPIT).ready.exists and not self.already_pending(UnitTypeId.INFESTATIONPIT):
                self.building_infestationpit = True
                await self.chat_send("I'm building an infestation pit")

            else:
                choice = 4

            if choice == 4 and self.units(UnitTypeId.LAIR).ready.exists and not self.units(UnitTypeId.HYDRALISKDEN).ready.exists and not self.already_pending(UnitTypeId.HYDRALISKDEN):
                await self.chat_send("I'm building a hydra den")
                self.building_hydraliskden = True
            else:
                choice = 5

            if choice == 5 and self.units(UnitTypeId.SPAWNINGPOOL).ready.exists and not self.units(UnitTypeId.HIVE) and not self.units(UnitTypeId.LAIR).ready.exists and not self.already_pending(UnitTypeId.LAIR):
                await self.chat_send("I'm building a LAIR")
                self.building_lair = True
            else:
                choice = 6

            if choice == 6 and self.units(UnitTypeId.SPAWNINGPOOL).ready.exists and not self.units(UnitTypeId.ROACHWARREN).ready.exists and not self.already_pending(UnitTypeId.ROACHWARREN):
                await self.chat_send("I'm building a roach warren")
                self.building_roachwarren = True
            else:
                choice = 7

            if choice == 7 and not self.units(UnitTypeId.SPAWNINGPOOL).ready.exists and not self.already_pending(UnitTypeId.SPAWNINGPOOL):
                await self.chat_send("I'm building a spawning pool")
                self.building_spawningpool = True

        # build a building
        if self.building_ultraliskcavern:
            if self.can_afford(UnitTypeId.ULTRALISKCAVERN):
                await self.build(UnitTypeId.ULTRALISKCAVERN, near=hq)
                self.building_ultraliskcavern = False
                return False
            else:
                return True

        # build a building
        if self.building_hive:
            if self.can_afford(UnitTypeId.HIVE):
                lair = self.units(UnitTypeId.LAIR).ready
                await self.do(lair.first.build(UnitTypeId.HIVE))
                self.building_hive = False
                return False
            else:
                return True

        # build a building
        if self.building_infestationpit:
            if self.can_afford(UnitTypeId.INFESTATIONPIT):
                await self.build(UnitTypeId.INFESTATIONPIT, near=hq)
                self.building_infestationpit = False
                return False
            else:
                return True

        # build a building
        if self.building_hydraliskden:
            if self.can_afford(UnitTypeId.HYDRALISKDEN):
                await self.build(UnitTypeId.HYDRALISKDEN, near=hq)
                self.building_hydraliskden = False
                return False
            else:
                return True

        # build a building
        if self.building_lair:
            if self.can_afford(UnitTypeId.LAIR):
                hatch = self.townhalls.first
                await self.do(hatch.build(UnitTypeId.LAIR))
                self.building_lair = False
                return False
            else:
                return True

        # build a building
        if self.building_roachwarren:
            if self.can_afford(UnitTypeId.ROACHWARREN):
                await self.build(UnitTypeId.ROACHWARREN, near=hq)
                self.building_roachwarren = False
                return False
            else:
                return True

        # build a building
        if self.building_spawningpool:
            if self.can_afford(UnitTypeId.SPAWNINGPOOL):
                await self.build(UnitTypeId.SPAWNINGPOOL, near=hq)
                self.building_spawningpool = False
                return False
            else:
                return True

    async def build_army(self):
        larvae = self.units(UnitTypeId.LARVA)
        # if any of the training flags are true, build. Otherwise, if they're not, get choice. and set the flags.
        if not self.training_hydras and not self.training_lings and not self.training_ultras and not self.training_roaches:
            choice = random.randint(1, 5)

            if choice == 1 and self.units(UnitTypeId.ULTRALISKCAVERN).ready.exists:
                self.training_ultras = True
                await self.chat_send("I'm training an ultra")
            else:
                choice = 2

            if choice == 2 and self.units(UnitTypeId.HYDRALISKDEN).ready.exists:
                self.training_hydras = True
                await self.chat_send("I'm training 2 hydras")
            else:
                choice = 3

            if choice == 3 and self.units(UnitTypeId.ROACHWARREN).ready.exists:
                await self.chat_send("I'm training some roaches")
                self.training_roaches = True
            else:
                choice = 4

            if choice == 4 and self.units(UnitTypeId.SPAWNINGPOOL).ready.exists:
                await self.chat_send("I'm training 8 zerglings")
                self.training_lings = True


        # build some units.
        if self.training_ultras:
            if self.can_afford(UnitTypeId.ULTRALISK) and larvae.exists:
                await self.do(larvae.random.train(UnitTypeId.ULTRALISK))
                self.training_ultras = False
                return False
            else:
                return True

        if self.training_hydras:
            if self.can_afford(UnitTypeId.HYDRALISK) and larvae.exists:
                await self.do(larvae.random.train(UnitTypeId.HYDRALISK))
                self.training_count += 1
                if self.training_count > 1:
                    self.training_hydras = False
                    self.training_count = 0
                    return False
                else:
                    return True
            else:
                return True

        if self.training_lings:
            if self.can_afford(UnitTypeId.ZERGLING) and larvae.exists:
                await self.do(larvae.random.train(UnitTypeId.ZERGLING))
                self.training_count += 1
                if self.training_count > 3:
                    self.training_lings = False
                    return False
                else:
                    return True
            else:
                return True

        if self.training_roaches:
            if self.can_afford(UnitTypeId.ROACH) and larvae.exists:
                await self.do(larvae.random.train(UnitTypeId.ROACH))
                self.training_count += 1
                if self.training_count > 2:
                    self.training_roaches = False
                    return False
                else:
                    return True
            else:
                return True

    async def build_expand(self):
        if self.townhalls.amount < 3:
            if self.can_afford(UnitTypeId.HATCHERY) and not self.already_pending(UnitTypeId.HATCHERY):
                location = await self.get_next_expansion()
                await self.build(UnitTypeId.HATCHERY, near=location)
                await self.chat_send("I'm expanding!")
                return False
            else:
                return True
        else:
            # if we have a bunch of expansions already, just build more army units.
            await self.chat_send("I wanted to expand, but I guess I'll build an army instead.")
            self.building_army = True
            return False


    async def gather_army(self):
        choice = random.randint(1, 2)
        # we want to put our units maybe in the middle of all of our town halls?
        # select them all and put them

    async def get_upgrades(self):
        await self.build_evo()
        if self.units(UnitTypeId.ULTRALISKCAVERN).ready.exists and self.can_afford(AbilityId.RESEARCH_CHITINOUSPLATING):
            uc = self.units(UnitTypeId.ULTRALISKCAVERN).ready.first
            await self.do(uc.train(AbilityId.CHITINOUSPLATING))

        if self.units(UnitTypeId.BANELINGNEST).ready.exists and self.can_afford(AbilityId.RESEARCH_CENTRIFUGALHOOKS):
            bns = self.units(UnitTypeId.BANELINGNEST).ready
            for bn in bns:
                if self.units(UnitTypeId.LAIR).ready.exists:
                    await self.do(bn(AbilityId.RESEARCH_CENTRIFUGALHOOKS))

        evos = self.units(UnitTypeId.EVOLUTIONCHAMBER).ready
        for evo in evos:
            if self.can_afford(AbilityId.RESEARCH_ZERGMELEEWEAPONSLEVEL1) and not self.attack1_started:
                await self.do(evo(AbilityId.RESEARCH_ZERGMELEEWEAPONSLEVEL1))
                self.attack1_started = True
                return

            if self.can_afford(AbilityId.RESEARCH_ZERGGROUNDARMORLEVEL1) and not self.ground1_started:
                await self.do(evo(AbilityId.RESEARCH_ZERGGROUNDARMORLEVEL1))
                self.ground1_started = True
                return

            if self.can_afford(AbilityId.RESEARCH_ZERGMELEEWEAPONSLEVEL2) and not self.attack2_started:
                await self.do(evo(AbilityId.RESEARCH_ZERGMELEEWEAPONSLEVEL2))
                self.attack2_started = True
                return

            if self.can_afford(AbilityId.RESEARCH_ZERGGROUNDARMORLEVEL2) and not self.ground2_started:
                await self.do(evo(AbilityId.RESEARCH_ZERGGROUNDARMORLEVEL2))
                self.ground2_started = True
                return

            if self.can_afford(AbilityId.RESEARCH_ZERGMELEEWEAPONSLEVEL3) and not self.attack3_started:
                await self.do(evo(AbilityId.RESEARCH_ZERGMELEEWEAPONSLEVEL3))
                self.attack3_started = True
                return

            if self.can_afford(AbilityId.RESEARCH_ZERGGROUNDARMORLEVEL3) and not self.ground3_started:
                await self.do(evo(AbilityId.RESEARCH_ZERGGROUNDARMORLEVEL3))
                self.ground3_started = True
                return

    async def build_evo(self):
        hq = self.townhalls.first
        if self.townhalls.ready.amount > 1 and self.can_afford(UnitTypeId.EVOLUTIONCHAMBER):
            if not self.units(UnitTypeId.EVOLUTIONCHAMBER).ready.exists and not self.already_pending(UnitTypeId.EVOLUTIONCHAMBER):
                await self.build(UnitTypeId.EVOLUTIONCHAMBER, near=hq)


    async def build_extractor(self):
        for th in self.townhalls.ready:
            vgs = self.state.vespene_geyser.closer_than(20.0, th)
            for vg in vgs:
                if not self.can_afford(UnitTypeId.EXTRACTOR):
                    break

                worker = self.select_build_worker(vg.position)
                if worker is None:
                    break

                if not self.units(UnitTypeId.EXTRACTOR).closer_than(1.0, vg).exists:
                    await self.do(worker.build(UnitTypeId.EXTRACTOR, vg))

    async def build_queens(self):
        hqs = self.townhalls.ready
        for hq in hqs:
            if self.units(UnitTypeId.SPAWNINGPOOL).ready.exists and self.units(UnitTypeId.QUEEN).amount <= self.townhalls.amount:
                if not self.already_pending(UnitTypeId.QUEEN):
                    if self.can_afford(UnitTypeId.QUEEN):
                        if hq.noqueue:
                            await self.do(hq.train(UnitTypeId.QUEEN))

    async def inject_larva(self):
        hq = self.townhalls.random
        for queen in self.units(UnitTypeId.QUEEN).idle:
            abilities = await self.get_available_abilities(queen)
            if AbilityId.EFFECT_INJECTLARVA in abilities:
                await self.do(queen(AbilityId.EFFECT_INJECTLARVA, hq))

    async def attac(self, iteration):
        forces = self.units(UnitTypeId.ZERGLING) | self.units(UnitTypeId.HYDRALISK) | self.units(UnitTypeId.ULTRALISK) | self.units(UnitTypeId.ROACH)
        if forces.amount > (iteration / 1000) + 5 or self.supply_used < 190:
            for unit in forces.idle:
                await self.do(unit.attack(self.select_target()))

    async def build_workers(self):
        hq = self.townhalls.first
        larvae = self.units(UnitTypeId.LARVA)
        if hq.assigned_harvesters < hq.ideal_harvesters:
            if self.can_afford(UnitTypeId.DRONE) and larvae.exists:
                larva = larvae.random
                await self.do(larva.train(UnitTypeId.DRONE))
                return

    async def build_overlord(self):
        larvae = self.units(UnitTypeId.LARVA)
        if self.supply_left < 2 or (self.supply_left < 4 and self.supply_cap > 28 ):
            if self.can_afford(UnitTypeId.OVERLORD) and not self.already_pending(UnitTypeId.OVERLORD) and larvae.exists:
                await self.do(larvae.random.train(UnitTypeId.OVERLORD))

    def select_target(self):
        if self.known_enemy_units.exists:
            return random.choice(self.known_enemy_units).position
        elif self.known_enemy_structures.exists:
            return random.choice(self.known_enemy_structures).position
        else:
            return self.enemy_start_locations[0]

def main():
    run_game(maps.get("AcidplantLE"), [
        Bot(Race.Zerg, charles()),
        Computer(Race.Random, Difficulty.Medium)
    ], realtime=False)

if __name__ == '__main__':
    main()
