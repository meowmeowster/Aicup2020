import math
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
        enemylist = []

        for e in player_view.entities:
            if not is_mine(player_view, e):
                if e.entity_type != et.RESOURCE:
                    enemylist.append(e)
            else:
                countlist.append(e)

        for e in countlist:

            # старый код
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

                actions[e.id] = model.EntityAction(m, b, a, r)

                # новый код

                builders = list(filter(lambda s: s.entity_type == et.BUILDER_UNIT, countlist))
                melee = list(filter(lambda s: s.entity_type == et.MELEE_UNIT, countlist))
                ranged = list(filter(lambda s: s.entity_type == et.RANGED_UNIT, countlist))

                units = len(builders) + len(melee) + len(ranged)

                base_b = list(filter(lambda s: s.entity_type == et.BUILDER_BASE, countlist))
                base_m = list(filter(lambda s: s.entity_type == et.MELEE_BASE, countlist))
                base_r = list(filter(lambda s: s.entity_type == et.RANGED_BASE, countlist))

                turrets = list(filter(lambda s: s.entity_type == et.TURRET, countlist))
                houses = list(filter(lambda s: s.entity_type == et.HOUSE, countlist))
                walls = list(filter(lambda s: s.entity_type == et.WALL, countlist))
                places = (len(base_b) + len(base_m) + len(base_r) + len(houses)) * 5

                if e in turrets:
                    m = None
                    b = None
                    r = None
                    a = model.attack_action.AttackAction(
                        target=None,
                        auto_attack=model.auto_attack.AutoAttack(
                            pathfind_range=p.sight_range,
                            valid_targets=[et.BUILDER_UNIT, et.MELEE_UNIT, et.RANGED_UNIT]
                        )
                    )

                if e in base_b:
                    if len(builders) < (7 + len(houses) * 2) and player_view.current_tick < 900:
                        b = model.build_action.BuildAction(
                            3,
                            model.vec2_int.Vec2Int(
                                e.position.x + p.size,
                                e.position.y + p.size - 1,
                            )
                        )
                    actions[e.id] = model.EntityAction(m, b, a, r)
                if e in base_m:
                    if len(builders) >= 7 and len(melee) * len(base_m) <= len(ranged) * len(base_r):
                        b = model.build_action.BuildAction(
                            5,
                            model.vec2_int.Vec2Int(
                                e.position.x + p.size,
                                e.position.y + p.size - 1,
                            )
                        )
                    actions[e.id] = model.EntityAction(m, b, a, r)
                if e in base_r:
                    if (len(builders) >= 7 and len(ranged) * len(base_r) <= len(melee) * len(base_m)) or player_view.current_tick > 850:
                        b = model.build_action.BuildAction(
                            7,
                            model.vec2_int.Vec2Int(
                                e.position.x + p.size,
                                e.position.y + p.size - 1,
                            )
                        )
                    actions[e.id] = model.EntityAction(m, b, a, r)
                if e in builders:
                    b = None
                    if len(houses) < 1:
                        t = model.vec2_int.Vec2Int(player_view.map_size - 1, player_view.map_size - 1)
                        m = model.move_action.MoveAction(t, True, True)
                        b = model.build_action.BuildAction(
                            1,
                            model.vec2_int.Vec2Int(
                                e.position.x + p.size,
                                e.position.y + p.size - 1,
                            )
                        )
                    if len(base_m) < 1 + int(units/90):
                        t = model.vec2_int.Vec2Int(player_view.map_size - 1, player_view.map_size - 1)
                        m = model.move_action.MoveAction(t, True, True)
                        b = model.build_action.BuildAction(
                            4,
                            model.vec2_int.Vec2Int(
                                e.position.x + p.size,
                                e.position.y + p.size - 1,
                            )
                        )
                    if len(base_r) < 1 + int(units/90):
                        t = model.vec2_int.Vec2Int(player_view.map_size - 1, player_view.map_size - 1)
                        m = model.move_action.MoveAction(t, True, True)
                        b = model.build_action.BuildAction(
                            6,
                            model.vec2_int.Vec2Int(
                                e.position.x + p.size,
                                e.position.y + p.size - 1,
                            )
                        )

                    if len(base_b) < 1 + int(units/80):
                        t = model.vec2_int.Vec2Int(player_view.map_size - 1, player_view.map_size - 1)
                        m = model.move_action.MoveAction(t, True, True)
                        b = model.build_action.BuildAction(
                            2,
                            model.vec2_int.Vec2Int(
                                e.position.x + p.size,
                                e.position.y + p.size - 1,
                            )
                        )

                    if places < (units + 15) and player_view.current_tick < 900:
                        b = model.build_action.BuildAction(
                            1,
                            model.vec2_int.Vec2Int(
                                e.position.x + p.size,
                                e.position.y + p.size - 1,
                            )
                        )
                    if len(turrets) < int(len(houses)/2):
                        t = model.vec2_int.Vec2Int(player_view.map_size - 1, player_view.map_size - 1)
                        m = model.move_action.MoveAction(t, True, True)
                        b = model.build_action.BuildAction(
                            9,
                            model.vec2_int.Vec2Int(
                                e.position.x + p.size,
                                e.position.y + p.size - 1,
                            )
                        )
                    if player_view.current_tick >= 900:
                        b = model.build_action.BuildAction(
                            9,
                            model.vec2_int.Vec2Int(
                                e.position.x + p.size,
                                e.position.y + p.size - 1,
                            )
                        )
                    actions[e.id] = model.EntityAction(m, b, a, r)
                if e in houses or e in walls or e in base_b or e in base_m or e in base_r or e in turrets:
                    if (not e.active) or (e.health < int(player_view.entity_properties[e.entity_type].max_health)):
                        radius = 999999
                        chosen = 0
                        for e2 in builders:
                            new_radius = int(math.sqrt(math.pow(e2.position.x - e.position.x, 2) + math.pow(e2.position.y - e.position.y, 2)))
                            if (new_radius < radius or radius < 5):
                                try:
                                    if actions[int(e2.id)].repair_action is None:
                                        radius = new_radius
                                        chosen = int(e2.id)
                                        p = player_view.entity_properties[e.entity_type]
                                        m = model.move_action.MoveAction(
                                            model.vec2_int.Vec2Int(
                                                e.position.x + int(p.size/2),
                                                e.position.y + int(p.size/2),
                                            ),
                                            True, True)
                                        b = None
                                        a = None
                                except:
                                    radius = new_radius
                                    chosen = int(e2.id)
                                    p = player_view.entity_properties[e.entity_type]
                                    m = model.move_action.MoveAction(
                                        model.vec2_int.Vec2Int(
                                            e.position.x + int(p.size / 2),
                                            e.position.y + int(p.size / 2),
                                        ),
                                        True, True)
                                    b = None
                                    a = None
                                if radius < 2:
                                    m = None
                                    b = None
                                    a = None
                                    r = model.repair_action.RepairAction(e.id)
                                actions[chosen] = model.EntityAction(m, b, a, r)
                if e in melee:

                    if int(e.id) % 2 == 0:
                        coeff1 = 1
                    else:
                        coeff1 = -1
                    coord_x = int(player_view.map_size / 2 + (math.sin(coeff1 * player_view.current_tick/10 + e.id) * player_view.map_size / 2) / 1.1) - 1
                    coord_y = int(player_view.map_size / 2 + (math.cos(coeff1 * player_view.current_tick/10 + e.id) * player_view.map_size / 2) / 1.1) - 1

                    if player_view.current_tick < 40:
                        coord_x = int(player_view.map_size/1.1) - 1
                        coord_y = int(player_view.map_size/1.1) - 1

                    if len(enemylist) > 0:
                        radius = 999999
                        chosen = None
                        for y2 in enemylist:
                            new_radius = int(math.sqrt(
                                math.pow(y2.position.x - e.position.x, 2) + math.pow(y2.position.y - e.position.y, 2)))
                            if new_radius < radius or radius < 5:
                                radius = new_radius
                                chosen = y2
                                coord_x = chosen.position.x
                                coord_y = chosen.position.y
                            if len(melee) > 10 and y2.entity_type == et.BUILDER_BASE or y2.entity_type == et.MELEE_BASE or y2.entity_type == et.RANGED_BASE:
                                    chosen = y2
                                    coord_x = chosen.position.x
                                    coord_y = chosen.position.y

                    radius = 999999
                    chosen = None
                    for yb in countlist:
                        if (yb in builders or yb in base_b or yb in base_m or yb in base_r) \
                                and yb.active and yb.health < int(player_view.entity_properties[yb.entity_type].max_health / 2):
                            new_radius = int(math.sqrt(
                                math.pow(yb.position.x - e.position.x, 2) + math.pow(yb.position.y - e.position.y, 2)))
                            if new_radius < radius and 10 > radius > 5:
                                radius = new_radius
                                chosen = yb
                                coord_x = chosen.position.x
                                coord_y = chosen.position.y

                    t = model.vec2_int.Vec2Int(coord_x, coord_y)
                    m = model.move_action.MoveAction(t, True, True)
                    actions[e.id] = model.EntityAction(m, b, a, r)
                if e in ranged:

                    if int(e.id) % 2 == 0:
                        coeff1 = 1
                    else:
                        coeff1 = -1
                    coord_x = int(player_view.map_size / 2 + (math.sin(coeff1 * player_view.current_tick/12 + e.id + 90) * player_view.map_size / 2) / 1.2) - 1
                    coord_y = int(player_view.map_size / 2 + (math.cos(coeff1 * player_view.current_tick/12 + e.id + 90) * player_view.map_size / 2) / 1.2) - 1

                    if player_view.current_tick < 20:
                        coord_x = int(player_view.map_size / 1.2) - 1
                        coord_y = int(player_view.map_size / 1.2) - 1

                    if len(enemylist) > 0:
                        radius = 999999
                        chosen = None
                        for y2 in enemylist:
                            new_radius = int(math.sqrt(
                                math.pow(y2.position.x - e.position.x, 2) + math.pow(y2.position.y - e.position.y, 2)))
                            if new_radius < radius or radius < 5:
                                radius = new_radius
                                chosen = y2
                                coord_x = chosen.position.x
                                coord_y = chosen.position.y
                            if len(ranged) > 10 and y2.entity_type == et.BUILDER_BASE or y2.entity_type == et.MELEE_BASE or y2.entity_type == et.RANGED_BASE:
                                    chosen = y2
                                    coord_x = chosen.position.x
                                    coord_y = chosen.position.y

                    radius = 999999
                    chosen = None
                    for yb in countlist:
                        if (yb in base_b or yb in base_m or yb in base_r or yb in houses) \
                                and yb.active and yb.health < int(player_view.entity_properties[yb.entity_type].max_health / 2):
                            new_radius = int(math.sqrt(
                                math.pow(yb.position.x - e.position.x, 2) + math.pow(yb.position.y - e.position.y, 2)))
                            if new_radius < radius and 10 > radius > 5:
                                radius = new_radius
                                chosen = yb
                                coord_x = chosen.position.x
                                coord_y = chosen.position.y

                    t = model.vec2_int.Vec2Int(coord_x, coord_y)
                    m = model.move_action.MoveAction(t, True, True)
                    actions[e.id] = model.EntityAction(m, b, a, r)

        return model.Action(actions)

    def debug_update(self, player_view, debug_interface):
        debug_interface.send(model.DebugCommand.Clear())
        debug_interface.get_state()
