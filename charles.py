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
        self.training_count = 0
        self.building_spawningpool = False
        self.building_hydraliskden = False
        self.building_ultraliskcavern = False
        self.building_infestationpit = False
        self.building_lair = False
        self.building_hive = False

    async def on_step(self, iteration):
        # we need to do things like distribute workers, build workers, build queens, build vespense every step
        # Every so often, we should do randomly, Build army, expand, tech up, upgrade.

        if iteration % 100 == 0:
            if not self.expanding and not self.building_army and not self.teching and not self.upgrading:
                choice = random.randint(1, 5)
                if choice == 1:
                    self.expanding = await self.build_expand()
                    await self.chat_send("I'm expanding!")

                if choice == 2:
                    self.building_army = await self.build_army()
                    await self.chat_send("I'm building some army units!")

                if choice == 3:
                    self.teching = await self.tech_up()
                    await self.chat_send("I'm teching up!")

                if choice == 4:
                    self.upgrading = await self.get_upgrades()
                    await self.chat_send("I'm upgrading!")
            else:
                # we're already doing something, so just keep doing that thing.

                if self.expanding:
                    self.expanding = await self.build_expand()
                    await self.chat_send("I'm expanding!")

                if self.building_army:
                    self.building_army = await self.build_army()
                    await self.chat_send("I'm building some army units!")

                if self.teching:
                    self.teching = await self.tech_up()
                    await self.chat_send("I'm teching up!")

                if self.upgrading:
                    self.upgrading = await self.get_upgrades()
                    await self.chat_send("I'm upgrading!")

        if iteration % 5 == 0:

            await self.gather_army()
            await self.build_extractor()
            await self.attac()
            await self.inject_larva()
            await self.build_overlord()

            await self.distribute_workers()
            self.num_of_bases = self.units(UnitTypeId.HIVE).ready.exists.amount
            self.num_of_bases += self.units(UnitTypeId.LAIR).ready.exists.amount
            self.num_of_bases += self.units(UnitTypeId.HATCHERY).ready.exists.amount

            if self.units(UnitTypeId.DRONE).amount < 18 * self.units(UnitTypeId) and self.units(UnitTypeId.DRONE).amount > self.MAX_WORKERS:
                await self.build_workers()

            await self.build_queens()

    async def build_infest_pit(self):
        hq = self.townhalls.first
        if self.units(UnitTypeId.LAIR).ready.exists or self.units(UnitTypeId.HIVE).ready.exists:
            if not self.units(UnitTypeId.INFESTATIONPIT).ready.exists and not self.already_pending(UnitTypeId.INFESTATIONPIT):
                while self.minerals < 200 and self.vespene < 150:
                    if self.can_afford(UnitTypeId.INFESTATIONPIT):
                        await self.build(UnitTypeId.INFESTATIONPIT, near=hq)
                        return True
            else:
                return False
        else:
            return False

    async def tech_up(self):
        hq = self.townhalls.first

        ultra_cavern = self.units(UnitTypeId.ULTRALISKCAVERN).exists
        a_hive = self.units(UnitTypeId.HIVE).exists
        infest_pit = self.units(UnitTypeId.INFESTATIONPIT).exists
        hydra_den = self.units(UnitTypeId.HYDRALISKDEN).exists
        a_lair = self.units(UnitTypeId.LAIR).exists
        spawning_pool = self.units(UnitTypeId.SPAWNINGPOOL).exists

        # check if we're done teching...
        if ultra_cavern and a_hive and infest_pit and hydra_den and a_lair and spawning_pool:
            self.upgrading = True
            return False

        # if we're not currently doing something
        if not self.building_spawningpool and not self.building_lair and not self.building_hydraliskden and not self.building_infestationpit and not self.building_hive and not self.building_ultralistcavern:
            choice = random.randint(1, 7)

            if choice == 1 and self.units(UnitTypeId.HIVE).ready.exists and not self.units(UnitTypeId.ULTRALISKCAVERN).ready.exists and not self.already_pending(UnitTypeId.ULTRALISKCAVERN):
                self.building_ultraliskcavern = True
            else:
                choice = random.randint(2, 7)

            if choice == 2 and self.units(UnitTypeId.INFESTATIONPIT).ready.exists and not self.units(UnitTypeId.HIVE).ready.exists and not self.already_pending(UnitTypeId.HIVE):
                self.building_hive = True
            else:
                choice = random.randint(2, 7)

            if choice == 3 and self.units(UnitTypeId.LAIR).ready.exists and not self.units(UnitTypeId.INFESTATIONPIT) and not self.already_pending(UnitTypeId.INFESTATIONPIT):
                self.building_infestationpit = True
            else:
                choice = random.randint(5, 7)

            if choice == 4 and self.units(UnitTypeId.LAIR).ready.exists and not self.units(UnitTypeId.HYDRALISKDEN).ready.exists and not self.already_pending(UnitTypeId.HYDRALISKDEN):
                self.building_hydraliskden = True
            else:
                choice = random.randint(5, 7)

            if choice == 5 and self.units(UnitTypeId.SPAWNINGPOOL).ready.exists and not self.units(UnitTypeId.LAIR).ready.exists and not self.already_pending(UnitTypeId.LAIR):
                self.building_lair = True
            else:
                choice = 6

            if choice == 6 if :
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
        if not self.training_hydras and not self.training_lings and not self.training_ultras:

            choice = random.randint(1, 4)

            if choice == 1 and self.units(UnitTypeId.ULTRALISKCAVERN).ready.exists:
                self.training_ultras = True
            else:
                choice = random.randint(2, 4)

            if choice == 2 and self.units(UnitTypeId.HYDRALISKDEN).ready.exists:
                self.training_hydras = True
            else:
                choice = 3

            if choice == 3 and self.units(UnitTypeId.SPAWNINGPOOL).ready.exists:
                self.training_lings = True


        # build some units.
        if self.training_ultras:
            if self.can_afford(UnitTypeId.ULTRALISK) and larvae.exists:
                await self.build(UnitTypeId.ULTRALISKCAVERN, near=hq)
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


    async def build_expand(self):
        if self.townhalls.amount < 4 and not self.already_pending(UnitTypeId.HATCHERY):
            if self.can_afford(UnitTypeId.HATCHERY):
                location = await self.get_next_expansion()
                await self.build(UnitTypeId.HATCHERY, near=location)
                return False
            else:
                return True
        else:
            return True


    async def gather_army(self):
        choice = random.randint(1, 2)
        # we want to put our units maybe in the middle of all of our town halls?
        # select them all and put them

    async def build_baneling_nest(self):
        hq = self.townhalls.first
        if self.units(UnitTypeId.SPAWNINGPOOL).ready.exists and self.vespene > 300:
            if not self.already_pending(UnitTypeId.BANELINGNEST) and self.can_afford(UnitTypeId.BANELINGNEST) and not self.units(UnitTypeId.BANELINGNEST):
                await self.build(UnitTypeId.BANELINGNEST, near=hq)

    async def build_ultra_cavern(self):
        hq = self.townhalls.first
        if not self.units(UnitTypeId.ULTRALISKCAVERN).ready.exists and not self.already_pending(UnitTypeId.ULTRALISKCAVERN):
            while self.minerals < 300 and self.vespene < 150:
                if self.can_afford(UnitTypeId.ULTRALISKCAVERN):
                    await self.build(UnitTypeId.ULTRALISKCAVERN, near=hq)
                    return True
            else:
                return False

    async def upgrade_to_lair(self):
        hq = self.townhalls.first
        if self.units(UnitTypeId.SPAWNINGPOOL).ready.exists:
            if not self.units(UnitTypeId.LAIR).exists and not self.units(UnitTypeId.HIVE).exists and hq.noqueue and not self.lair_started:
                while True:
                    if self.can_afford(UnitTypeId.LAIR):
                        await self.do(hq.build(UnitTypeId.LAIR))
                        self.lair_started = True
                        return True
            else:
                return False
        else:
            return False

    async def upgrade_to_hive(self):
        lair = self.units(UnitTypeId.LAIR).ready
        infest = self.units(UnitTypeId.INFESTATIONPIT).ready
        if lair.exists and infest.exists:
            if not self.units(UnitTypeId.HIVE).exists and lair.noqueue and not self.hive_started:
                while self.minerals < 300 and self.vespene < 200:
                    if self.can_afford(UnitTypeId.HIVE):
                        await self.do(lair.first.build(UnitTypeId.HIVE))
                        self.hive_started = True
                        return True
            else:
                return False
        return False

    async def build_hydra_den(self):
        hq = self.townhalls.first
        if self.units(UnitTypeId.LAIR).ready.exists or self.units(UnitTypeId.HIVE).ready.exists:
            if not self.units(UnitTypeId.HYDRALISKDEN).ready.exists and not self.already_pending(UnitTypeId.HYDRALISKDEN):
                while self.minerals < 200 and self.vespene < 150:
                    if self.can_afford(UnitTypeId.HYDRALISKDEN):
                        await self.build(UnitTypeId.HYDRALISKDEN, near=hq)
                        return True
            else:
                return False
        else:
            return False

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
            if self.units(UnitTypeId.SPAWNINGPOOL).ready.exists and self.units(UnitTypeId.QUEEN).amount <= self.townhalls.amount + 1:
                if not self.already_pending(UnitTypeId.QUEEN):
                    if self.can_afford(UnitTypeId.QUEEN):
                        await self.do(hq.train(UnitTypeId.QUEEN))

    async def inject_larva(self):
        hq = self.townhalls.random
        for queen in self.units(UnitTypeId.QUEEN).idle:
            abilities = await self.get_available_abilities(queen)
            if AbilityId.EFFECT_INJECTLARVA in abilities:
                await self.do(queen(AbilityId.EFFECT_INJECTLARVA, hq))

    async def expand(self):
        if self.townhalls.amount < 4 and not self.already_pending(UnitTypeId.HATCHERY):
            if self.can_afford(UnitTypeId.HATCHERY):
                location = await self.get_next_expansion()
                await self.build(UnitTypeId.HATCHERY, near=location)

    async def attac(self):
        forces = self.units(UnitTypeId.ZERGLING) | self.units(UnitTypeId.HYDRALISK) | self.units(UnitTypeId.ULTRALISK) | self.units(UnitTypeId.BANELING)
        if forces.amount > (self.supply_used / 3):
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

    async def build_spawning_pool(self):
        hq = self.townhalls.first
        if not (self.units(UnitTypeId.SPAWNINGPOOL).exists or not self.already_pending(UnitTypeId.SPAWNINGPOOL)):
            if self.can_afford(UnitTypeId.SPAWNINGPOOL):
                await self.build(UnitTypeId.SPAWNINGPOOL, near=hq, max_distance=6)
               # We need to build an extractor as well.
                while self.minerals < 25:
                    await self.build_extractor()

                return True
            else:
                return False
        else:
            return False


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
        Computer(Race.Random, Difficulty.Harder)
    ], realtime=False)

if __name__ == '__main__':
    main()
