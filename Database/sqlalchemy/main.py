import models, schemas
from datetime import datetime
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)
db = SessionLocal()

# Criação de uma instância de DadosAnimal
db_dados_animal = models.DadosAnimal(raca="Labrador", peso_medio=30.5, id=1)
db.add(db_dados_animal)
db.commit()  # Garante que o ID de DadosAnimal seja gerado

# Criação de um Animal relacionado ao DadosAnimal
db_animal = models.Animal(sexo="M", id_dados_animal=db_dados_animal.id)
db.add(db_animal)
db.commit()

# Criação de ControlePesagem para o Animal criado
db_controle_pesagem = models.ControlePesagem(
    id_animal=db_animal.id,
    datahora_pesagem=datetime.now(),
    medicao_peso=31.0,
    observacoes="Pesagem após exercício"
)
db.add(db_controle_pesagem)
db.commit()

ls = db.query(models.Animal).all()

print(ls)

