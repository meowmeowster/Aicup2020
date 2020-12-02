import random

import model
from model.entity_type import EntityType as et


def is_unit(e, t=None):
    if t is None:
        t = [et.BUILDER_UNIT, et.MELEE_UNIT, et.RANGED_UNIT]
    return True if e.entity_type in t else False


def is_base(e, t=None):
    if t is None:
        t = [et.BUILDER_BASE, et.MELEE_BASE, et.RANGED_BASE]
    return True if e.entity_type in t else False


def is_mine(player_view, e):
    return True if e.player_id == player_view.my_id and e.entity_type != et.RESOURCE else False





class MyStrategy:

    def get_action(self, player_view, debug_interface):
        actions = {}
        my_id = player_view.my_id

        countlist = []

        for e in player_view.entities:
            if not is_mine(player_view, e):
                continue
            countlist.append(e)
        print(len(countlist))

        for e in countlist:
            #if e.entity_type == et.BUILDER_UNIT:
            builders = list(filter(lambda s: s.entity_type == et.BUILDER_UNIT, countlist))
            melee = list(filter(lambda s: s.entity_type == et.MELEE_UNIT, countlist))
            ranged = list(filter(lambda s: s.entity_type == et.RANGED_UNIT, countlist))


            p = player_view.entity_properties[e.entity_type]
            if e.player_id == my_id:
                m = None
                b = None
                a = None
                r = None
                if is_unit(e):
                    t = model.vec2_int.Vec2Int(player_view.map_size - 1, player_view.map_size - 1)
                    m = model.move_action.MoveAction(t, True, True)
                    a = model.attack_action.AttackAction(
                        target=None,
                        auto_attack=model.auto_attack.AutoAttack(
                            pathfind_range=p.sight_range,
                            valid_targets=[et.RESOURCE] if e.entity_type == et.BUILDER_UNIT else []
                        )
                    )
                elif is_base(e):
                    a = model.attack_action.AttackAction(
                        target=None,
                        auto_attack=model.auto_attack.AutoAttack(
                            pathfind_range=p.sight_range,
                            valid_targets=[et.RESOURCE] if e.entity_type == et.BUILDER_UNIT else []
                        )
                    )
                    if player_view.current_tick < 40:
                        b = model.build_action.BuildAction(
                            3,
                            model.vec2_int.Vec2Int(
                                e.position.x + p.size,
                                e.position.y + p.size - 1,
                            )
                        )
                    else:
                        b = model.build_action.BuildAction(
                            7,
                            model.vec2_int.Vec2Int(
                                e.position.x + p.size,
                                e.position.y + p.size - 1,
                            )
                        )

                actions[e.id] = model.EntityAction(m, b, a, r)

        return model.Action(actions)

    def debug_update(self, player_view, debug_interface):
        debug_interface.send(model.DebugCommand.Clear())
        debug_interface.get_state()
