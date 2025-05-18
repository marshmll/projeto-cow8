import json

from model.balanca import Balanca
from model.animal import Animal
from model.registro_pesagem import RegistroPesagem

class Callbacks():
    @staticmethod
    def record_measurement(logger, payload):
        data = json.loads(payload)

        logger.info(f'Weight measurement: {data}')

        if "scaleUid" not in data or "cowUid" not in data or "cowWeight" not in data:
            logger.warning(f"Ill formed payload of measurement: {data}")
            return

        scale = Balanca.get_balanca_by_uid(uid=data['scaleUid'])

        if not scale:
            logger.warning(f"Unregistered scale: {data['scaleUid']}")
            return

        cow = Animal.get_animal_by_uid(uid=data['cowUid'])

        if not cow:
            logger.warning(f"Unregistered animal: {data['cowUid']}")
            return

        RegistroPesagem.create_registro(
            id_animal=cow.id,
            uid_balanca=scale.uid,
            medicao_peso=data['cowWeight']
        )

        logger.info(f"Registered new weight measurement for animal with uid {data['cowUid']}: {data['cowWeight']}")

    @staticmethod
    def scale_status_refresh(logger, payload):
        data = json.loads(payload)

        if "uid" not in data or "status" not in data:
            logger.warning(f"Ill formed payload of status: {data}")
            return

        scale = Balanca.get_balanca_by_uid(uid=data['uid'])

        if not scale:
            logger.warning(f"Unregistered scale: {data['uid']}")
            return

        Balanca.update_status(data)

        logger.info(f"Updated scale status for scale with uid {data['uid']}: {data['status']}")