# coding=utf-8
import logging
import traceback

if __name__ == '__main__':
    import os
    import django

    os.environ['TAM_SETTINGS'] = "settings_arte"
    django.setup()

import pytz
from decimal import Decimal
import datetime
from django.db import transaction
from django.conf import settings
from tam.models import Viaggio, Luogo
from tam.views.tamviews import associate

logger = logging.getLogger('tam.arte.check')
tz_italy = pytz.timezone('Europe/Rome')


class EndOfTestExeption(Exception):
    pass


def classifica_assertion(classifica, assertions, message=""):
    """
    @param message: the message to presento when the assertion fail
    @type assertions: dict(str:Decimal)
    @type classifica: dict(str:Decimal)
    """
    errors = []
    for key, expected in assertions.items():
        if classifica[key] != expected:
            errors.append("{key} is {val} instead of {expected}".format(
                key=key, val=classifica[key], expected=expected
            ))
    assert errors == [], "\n".join(errors) + ("\n" + message) if message else ""


def arrivo_singolo_o_due_arrivi():
    """
        Test congruenza mail Rob. Lup. 26/6/2015
    """
    try:
        with transaction.atomic():
            abano = Luogo.objects.get(nome=".Abano Montegrotto")
            venezia = Luogo.objects.get(nome=".VENEZIA  AEROPORTO")
            arrivo_singolo = Viaggio(
                data=tz_italy.localize(datetime.datetime(2020, 6, 27, 12, 10)),
                da=venezia,
                a=abano,
                prezzo=Decimal("60"),
                numero_passeggeri=2,
                esclusivo=False,
                luogoDiRiferimento=abano,
            )
            arrivo_singolo.costo_autostrada = arrivo_singolo.costo_autostrada_default()
            # arrivo_singolo.abbuono_fisso = settings.ABBUONO_AEROPORTI
            arrivo_singolo.updatePrecomp(force_save=True)

            classifica_assertion(arrivo_singolo.classifiche(),
                                 {'prezzoVenezia': Decimal("37.94")})

            arrivo_v1 = Viaggio(
                data=tz_italy.localize(datetime.datetime(2020, 6, 27, 12, 11)),
                da=venezia,
                a=abano,
                prezzo=Decimal("30"),
                numero_passeggeri=1,
                esclusivo=False,
                luogoDiRiferimento=abano,
            )
            arrivo_v1.costo_autostrada = arrivo_v1.costo_autostrada_default()
            arrivo_v1.abbuono_fisso = settings.ABBUONO_AEROPORTI
            arrivo_v1.updatePrecomp(force_save=True)
            arrivo_v2 = Viaggio(
                data=tz_italy.localize(datetime.datetime(2020, 6, 27, 12, 12)),
                da=venezia,
                a=abano,
                prezzo=Decimal("30"),
                numero_passeggeri=1,
                esclusivo=False,
                luogoDiRiferimento=abano,
            )
            arrivo_v2.costo_autostrada = arrivo_v2.costo_autostrada_default()
            arrivo_v2.abbuono_fisso = settings.ABBUONO_AEROPORTI
            arrivo_v2.updatePrecomp(force_save=True)

            associate(assoType='link', viaggiIds=[arrivo_v1.id, arrivo_v2.id])

            # I have to retake the objects from the db
            arrivo_v1.refresh_from_db()
            arrivo_v2.refresh_from_db()

            classifica_assertion(
                arrivo_v1.classifiche(),
                {'prezzoVenezia': arrivo_singolo.prezzoVenezia},
                "Due singoli in arrivo dovrebbe avere le stesse caratteristiche di arrivo singolo"
            )
            raise EndOfTestExeption
    except EndOfTestExeption:
        logger.info("Ok.")


def partenza_singola_o_due_partenze():
    """
        Test congruenza mail Rob. Lup. 29/8/2015
    """
    try:
        with transaction.atomic():
            abano = Luogo.objects.get(nome=".Abano Montegrotto")
            venezia = Luogo.objects.get(nome=".VENEZIA  AEROPORTO")
            partenza_singolo = Viaggio(
                data=tz_italy.localize(datetime.datetime(2020, 6, 27, 12, 12)),
                da=venezia,
                a=abano,
                prezzo=Decimal("62"),
                numero_passeggeri=2,
                esclusivo=False,
                luogoDiRiferimento=abano,
            )
            partenza_singolo.costo_autostrada = partenza_singolo.costo_autostrada_default()
            partenza_singolo.abbuono_fisso = 0
            partenza_singolo.updatePrecomp(force_save=True)

            classifica_assertion(partenza_singolo.classifiche(),
                                 {'prezzoVenezia': Decimal("40.78")}, "Check prezzoVenezia")

            partenza_v1 = Viaggio(
                data=tz_italy.localize(datetime.datetime(2020, 6, 27, 12, 11)),
                da=abano,
                a=venezia,
                prezzo=Decimal("31"),
                numero_passeggeri=1,
                esclusivo=False,
                luogoDiRiferimento=abano,
            )

            partenza_v1.costo_autostrada = partenza_v1.costo_autostrada_default()
            partenza_v1.abbuono_fisso = 0
            partenza_v1.updatePrecomp(force_save=True)
            assert partenza_v1.classifiche()['prezzoVenezia'] == Decimal('8.27')

            partenza_v2 = Viaggio(
                data=tz_italy.localize(datetime.datetime(2020, 6, 27, 12, 12)),
                da=abano,
                a=venezia,
                prezzo=Decimal("31"),
                numero_passeggeri=1,
                esclusivo=False,
                luogoDiRiferimento=abano,
            )
            partenza_v2.costo_autostrada = partenza_v2.costo_autostrada_default()
            partenza_v2.abbuono_fisso = 0
            partenza_v2.updatePrecomp(force_save=True)

            associate(assoType='link', viaggiIds=[partenza_v1.id, partenza_v2.id])
            # I have to retake the objects from the db
            partenza_v1.refresh_from_db()
            partenza_v2.refresh_from_db()
            classifica_assertion(
                partenza_v1.classifiche(),
                {'prezzoVenezia': partenza_singolo.prezzoVenezia},
                "Due singoli in arrivo dovrebbe avere le stesse caratteristiche di arrivo singolo"
            )
            # classifica_assertion(
            #     partenza_v1.classifiche(),
            #     {'prezzoVenezia': 0},
            #     "Due singoli in arrivo dovrebbe avere le stesse caratteristiche di arrivo singolo"
            # )

            raise EndOfTestExeption
    except EndOfTestExeption:
        logger.info("Ok.")


def check_associata():
    """
        Test congruenza mail Rob. Lup. 26/6/2015
    """
    try:
        with transaction.atomic():
            abano = Luogo.objects.get(nome=".Abano Montegrotto")
            venezia = Luogo.objects.get(nome=".VENEZIA  AEROPORTO")

            andata = Viaggio(
                data=tz_italy.localize(datetime.datetime(2020, 6, 27, 12, 12)),
                da=abano,
                a=venezia,
                prezzo=Decimal("31"),
                numero_passeggeri=1,
                esclusivo=False,
                luogoDiRiferimento=abano,
            )
            andata.costo_autostrada = andata.costo_autostrada_default()
            andata.updatePrecomp(force_save=True)
            assert andata.classifiche()['prezzoVenezia'] == Decimal('8.27')

            ritorno = Viaggio(
                data=tz_italy.localize(datetime.datetime(2020, 6, 27, 13, 12)),
                da=venezia,
                a=abano,
                prezzo=Decimal("31"),
                numero_passeggeri=1,
                esclusivo=False,
                luogoDiRiferimento=abano,
            )
            ritorno.costo_autostrada = ritorno.costo_autostrada_default()
            ritorno.abbuono_fisso = settings.ABBUONO_AEROPORTI
            ritorno.updatePrecomp(force_save=True)
            assert ritorno.abbuono_fisso == settings.ABBUONO_AEROPORTI  # it's coming from an airport
            assert ritorno.classifiche()['prezzoVenezia'] == Decimal('-1.73')

            associate(assoType='link', viaggiIds=[andata.id, ritorno.id])

            # I have to retake the objects from the db
            andata.refresh_from_db()
            ritorno.refresh_from_db()
            classifica = andata.classifiche()
            assert classifica['puntiAbbinata'] == 1
            assert andata.prezzoPunti == Decimal('56.40')
            raise EndOfTestExeption
    except EndOfTestExeption:
        logger.info("Ok.")


if __name__ == '__main__':
    for test_name in (
        arrivo_singolo_o_due_arrivi,
        partenza_singola_o_due_partenze,
        check_associata,
    ):
        try:
            logger.info("Testing %s", test_name.__name__)
            test_name()
        except:
            logger.error("FAILED")
            logger.error(traceback.format_exc())