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
        self.hive_started = False
        self.lair_started = False

    async def on_step(self, iteration):
        await self.get_upgrades()
        await self.expand()
        await self.build_ultra_cavern()
        await self.upgrade_to_lair()
        await self.upgrade_to_hive()
        await self.build_hydra_den()
        await self.build_infest_pit()
        await self.build_ultra_cavern()
        await self.build_baneling_nest()
        await self.build_spawning_pool()
        await self.build_evo()
        await self.build_extractor()
        await self.attac()
        await self.inject_larva()
        await self.build_overlord()
        await self.distribute_workers()

        if self.units(UnitTypeId.DRONE).amount < self.MAX_WORKERS:
            await self.build_workers()

        await self.build_queens()
        if iteration % 2 == 1:
            await self.build_army(iteration)

    async def build_infest_pit(self):
        hq = self.townhalls.first
        if (self.units(UnitTypeId.LAIR).ready.exists or self.units(UnitTypeId.HIVE).ready.exists):
            if not self.units(UnitTypeId.INFESTATIONPIT).ready.exists and not self.already_pending(UnitTypeId.INFESTATIONPIT) and self.can_afford(UnitTypeId.INFESTATIONPIT):
                await self.build(UnitTypeId.INFESTATIONPIT, near=hq)

    async def build_baneling_nest(self):
        hq = self.townhalls.first
        if self.units(UnitTypeId.SPAWNINGPOOL).ready.exists and self.vespene > 300:
            if not self.already_pending(UnitTypeId.BANELINGNEST) and self.can_afford(UnitTypeId.BANELINGNEST) and not self.units(UnitTypeId.BANELINGNEST):
                await self.build(UnitTypeId.BANELINGNEST, near=hq)

    async def build_ultra_cavern(self):
        hq = self.townhalls.first
        if (self.units(UnitTypeId.HIVE).ready.exists):
            if not self.units(UnitTypeId.ULTRALISKCAVERN).ready.exists and not self.already_pending(UnitTypeId.ULTRALISKCAVERN) and self.can_afford(UnitTypeId.ULTRALISKCAVERN):
                await self.build(UnitTypeId.ULTRALISKCAVERN, near=hq)

    async def upgrade_to_lair(self):
        hq = self.townhalls.first
        if self.units(UnitTypeId.SPAWNINGPOOL).ready.exists:
            if not self.units(UnitTypeId.LAIR).exists and not self.units(UnitTypeId.HIVE).exists and hq.noqueue and not self.lair_started:
                if self.can_afford(UnitTypeId.LAIR):
                    await self.do(hq.build(UnitTypeId.LAIR))
                    self.lair_started = True

    async def upgrade_to_hive(self):
        lair = self.units(UnitTypeId.LAIR).ready
        infest = self.units(UnitTypeId.INFESTATIONPIT).ready
        if lair.exists and infest.exists:
            if not self.units(UnitTypeId.HIVE).exists and lair.noqueue and not self.hive_started:
                if self.can_afford(UnitTypeId.HIVE):
                    await self.do(lair.first.build(UnitTypeId.HIVE))
                    self.hive_started = True

    async def build_hydra_den(self):
        hq = self.townhalls.first
        if (self.units(UnitTypeId.LAIR).ready.exists or self.units(UnitTypeId.HIVE).ready.exists):
            if not self.units(UnitTypeId.HYDRALISKDEN).ready.exists and not self.already_pending(UnitTypeId.HYDRALISKDEN) and self.can_afford(UnitTypeId.HYDRALISKDEN):
                await self.build(UnitTypeId.HYDRALISKDEN, near=hq)

    async def get_upgrades(self):
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

    async def build_army(self, iteration):
        larvae = self.units(UnitTypeId.LARVA)
        hydras = self.units(UnitTypeId.HYDRALISK)
        lings = self.units(UnitTypeId.ZERGLING)
        ultras = self.units(UnitTypeId.ULTRALISK)
        banes = self.units(UnitTypeId.BANELING)


        if lings.exists and self.units(UnitTypeId.BANELINGNEST).ready.exists:
            for ling in lings:
                if self.vespene >= 600 and self.can_afford(UnitTypeId.BANELING) and banes.amount < 15:
                    await self.do(ling.train(UnitTypeId.BANELING))

        if self.units(UnitTypeId.ULTRALISKCAVERN).ready.exists and ultras.amount <= 3:
            if self.can_afford(UnitTypeId.ULTRALISK) and larvae.exists:
                await self.do(larvae.random.train(UnitTypeId.ULTRALISK))
            else:
                return

        if hydras.amount >= (lings.amount * 2 + banes.amount):
            if self.can_afford(UnitTypeId.ZERGLING) and larvae.exists and self.units(UnitTypeId.SPAWNINGPOOL).ready.exists:
                await self.do(larvae.random.train(UnitTypeId.ZERGLING))
        elif self.can_afford(UnitTypeId.HYDRALISK) and larvae.exists and self.units(UnitTypeId.HYDRALISKDEN).ready.exists:
            await self.do(larvae.random.train(UnitTypeId.HYDRALISK))
        else:
            if self.can_afford(UnitTypeId.ZERGLING) and larvae.exists and self.units(UnitTypeId.SPAWNINGPOOL).ready.exists:
                await self.do(larvae.random.train(UnitTypeId.ZERGLING))

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
        if not (self.units(UnitTypeId.SPAWNINGPOOL).exists or self.already_pending(UnitTypeId.SPAWNINGPOOL)):
            if self.can_afford(UnitTypeId.SPAWNINGPOOL):
                await self.build(UnitTypeId.SPAWNINGPOOL, near=hq)

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
