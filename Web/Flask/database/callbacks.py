import json

from database.database import get_db
from . import models

def record_measurement(logger, payload):
    data = json.loads(payload)

    logger.info(f'Weight measurement: {data}')

    if "scaleUid" not in data or "cowUid" not in data or "cowWeight" not in data:
        logger.warning(f"Ill formed payload of measurement: {data}")
        return

    db = get_db()

    scale = db.query(models.Balanca).filter_by(uid=data['scaleUid']).first()

    if not scale:
        logger.warning(f"Unregistered scale: {data['scaleUid']}")
        db.remove()
        return

    cow = db.query(models.Animal).filter_by(uid=data['cowUid']).first()

    if not cow:
        logger.warning(f"Unregistered animal: {data['cowUid']}")
        db.remove()
        return

    record = models.ControlePesagem(
        id_animal=cow.id,
        id_balanca=scale.id,
        medicao_peso=data['cowWeight']
    )

    db.add(record)
    db.commit()
    db.remove()

    logger.info(f"Registered new weight measurement for animal with uid {data['cowUid']}: {data['cowWeight']}")

def scale_status_refresh(logger, payload):
    data = json.loads(payload)

    logger.info(f"Status: {data}")