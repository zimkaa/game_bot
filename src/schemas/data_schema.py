from decimal import Decimal
from typing import List
from typing import Union

import attr

from pydantic import BaseModel
from pydantic import Field

from request import Connection


@attr.s
class StopOrHit:
    html: Connection = attr.ib()
    stop: bool = attr.ib()


@attr.s
class EndBattleProp:
    fexp: str = attr.ib()
    fres: str = attr.ib()
    vcode: str = attr.ib()
    ftype: str = attr.ib()
    min1: str = attr.ib()
    max1: str = attr.ib()
    min2: str = attr.ib()
    max2: str = attr.ib()
    sum1: str = attr.ib()
    sum2: str = attr.ib()


@attr.s
class EndBattle(EndBattleProp):
    get_id: str = attr.ib(default="61")
    act: str = attr.ib(default="7")


@attr.s
class DataForFight:
    fight_ty: List[Union[str, int, float]] = attr.ib()
    param_ow: List[Union[str, int, float]] = attr.ib()
    lives_g1: List[Union[str, int, float]] = attr.ib()
    lives_g2: List[Union[str, int, float]] = attr.ib()
    alchemy: List[Union[str, int, float]] = attr.ib()
    magic_in: List[Union[str, int, float]] = attr.ib()
    param_en: List[Union[str, int, float]] = attr.ib()
    fight_pm: List[Union[str, int, float]] = attr.ib()


@attr.s
class Post:
    post_id: str = attr.ib()
    pnick: str = attr.ib()
    agree: str = attr.ib()
    vcode: str = attr.ib()
    wuid: str = attr.ib()
    wsubid: str = attr.ib()
    wsolid: str = attr.ib()


@attr.s
class Enemy:
    bot_name: str = attr.ib()
    bot_hp: Decimal = attr.ib(converter=Decimal)
    bot_max_hp: Decimal = attr.ib(converter=Decimal)
    bot_mp: Decimal = attr.ib(converter=Decimal)
    bot_max_mp: Decimal = attr.ib(converter=Decimal)
    bot_level: Decimal = attr.ib(converter=Decimal)


@attr.s
class Hit:
    inu: str = attr.ib()
    inb: str = attr.ib()
    ina: str = attr.ib()


@attr.s
class QueryHit(Hit):
    vcode: str = attr.ib()
    enemy: str = attr.ib()
    group: str = attr.ib()
    inf_bot: str = attr.ib()
    inf_zb: str = attr.ib()
    lev_bot: str = attr.ib()
    ftr: str = attr.ib()
    post_id: str = attr.ib(default="7")


class FightConfig(BaseModel):
    HP: bool = Field(default=True, title="Use HP", alias="hp")
    NEED_HP_PERCENT: float = Field(
        default=1.0,
        title="HP coefficient to restore",
        alias="needHpPercent",
        ge=0.0,
        le=1.0,
    )

    MP: bool = Field(default=True, title="Use MP", alias="mp")
    NEED_MP_PERCENT: float = Field(
        default=0.4,
        title="MP coefficient to restore",
        alias="needMpPercent",
        ge=0.0,
        le=1.0,
    )
    MP_NEED_INSIDE_BATTLE: int = Field(
        default=500,
        title="Try to restore at least this amount of mana",
        alias="mpNeedInsideBattle",
        ge=0,
        le=29970,
    )  # used to get need_mp
    NEED_MP_COUNT: int = Field(
        default=500,
        title="Restore MP when least or equal this amount",
        alias="needMpCount",
        ge=0,
        le=29970,
    )

    SCROLL: bool = Field(default=False, title="Use scroll like (The Rage Strike Scroll)", alias="scroll")
    KICK: bool = Field(default=False, title="Use buffs like (Bounty of Lightning)", alias="kick")
    KICK_COUNT: int = Field(default=1, title="Count buffs per step", alias="kickCount", ge=0, le=5)

    SUPER_HIT: bool = Field(default=True, title="Use super hit", alias="superHit")
    STABLE_HIT: bool = Field(default=True, title="Use physical hit", alias="stableHit")

    STABLE_MAGIC_HIT: bool = Field(default=True, title="Use magical hit", alias="stableMagicHits")
    MP_HIT: int = Field(default=5, title="MP per hit", alias="mpHit", ge=5, le=500)
    MIN_MP_COEFFICIENT: float = Field(
        default=0.3,
        title="Coefficient when stop used magic stable hits",
        alias="minMpCoefficient",
        ge=0.0,
        le=1.0,
    )  # used for magic hits


class StableHit(BaseModel):
    name: list[str]
    code: list[int]
    mp_cost: list[int]
    od: list[int]
    priority: list[int]
